from fastapi import APIRouter, HTTPException, Depends
from .db import SessionLocal, engine, Base
from .models import *
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import decimal

router = APIRouter()
pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_if_needed():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role=='admin').first()
        if not admin:
            u = User(name='Admin', email='admin@local', phone='', password_hash=pwd.hash('Passw0rd!'), role='admin')
            db.add(u)
            db.commit()
        rate = db.query(GoldRate).first()
        if not rate:
            r = GoldRate(rate_per_gram=2000000, source='seed')
            db.add(r); db.commit()
        prod = db.query(Product).first()
        if not prod:
            p = Product(name='Ring Sample', weight_gram=2.5, cost_per_gram=1800000, profit_percent=12, is_available=True)
            db.add(p); db.commit()
            # create inventory and image
            from .models import ProductImage, Inventory
            pi = ProductImage(product_id=p.id, url='https://via.placeholder.com/400', is_primary=True)
            inv = Inventory(product_id=p.id, quantity=10)
            db.add(pi); db.add(inv); db.commit()
    finally:
        db.close()

@router.get('/products')
def list_products(available: bool = True, future: bool = False, db: Session = Depends(get_db)):
    q = db.query(Product)
    if available:
        q = q.filter(Product.is_available==True)
    if not future:
        q = q.filter(Product.is_future_item==False)
    prods = q.all()
    out = []
    for p in prods:
        images = db.query(ProductImage).filter_by(product_id=p.id).all()
        inv = db.query(Inventory).filter_by(product_id=p.id).first()
        out.append({
            'id': p.id, 'name': p.name, 'weight_gram': float(p.weight_gram), 'profit_percent': float(p.profit_percent),
            'is_future_item': p.is_future_item, 'is_available': p.is_available, 'inventory': inv.quantity if inv else 0,
            'images': [{'url': i.url, 'is_primary': i.is_primary} for i in images]
        })
    return out

@router.get('/gold-rate')
def current_gold_rate(db: Session = Depends(get_db)):
    r = db.query(GoldRate).order_by(GoldRate.created_at.desc()).first()
    if not r:
        raise HTTPException(status_code=404, detail='No gold rate')
    return {'rate_per_gram': float(r.rate_per_gram), 'source': r.source, 'timestamp': r.created_at}

@router.post('/orders')
def create_order(payload: dict, db: Session = Depends(get_db)):
    items = payload.get('items')
    payment_method = payload.get('payment_method')
    if not items or not isinstance(items, list):
        raise HTTPException(status_code=400, detail='items required')
    rate = db.query(GoldRate).order_by(GoldRate.created_at.desc()).first()
    if not rate:
        raise HTTPException(status_code=400, detail='no gold rate')
    total = decimal.Decimal('0')
    total_weight = decimal.Decimal('0')
    order = Order(user_id=payload.get('user_id'), total_amount=0, total_weight=0, payment_method=payment_method, gold_rate_per_gram=rate.rate_per_gram)
    db.add(order); db.commit(); db.refresh(order)
    for it in items:
        pid = it.get('product_id')
        qty = int(it.get('quantity',1))
        p = db.query(Product).get(pid)
        if not p:
            db.rollback(); raise HTTPException(status_code=400, detail=f'invalid product {pid}')
        inv = db.query(Inventory).filter_by(product_id=p.id).first()
        if inv and inv.quantity < qty:
            db.rollback(); raise HTTPException(status_code=400, detail=f'insufficient inventory for {p.id}')
        unit_price = decimal.Decimal(str(float(p.weight_gram))) * decimal.Decimal(str(float(rate.rate_per_gram))) * (decimal.Decimal('1') + decimal.Decimal(str(float(p.profit_percent)))/decimal.Decimal('100'))
        subtotal = (unit_price * qty).quantize(decimal.Decimal('0.01'))
        oi = OrderItem(order_id=order.id, product_id=p.id, unit_price=unit_price, profit_percent=p.profit_percent, quantity=qty, subtotal=subtotal, product_snapshot_name=p.name, product_snapshot_weight=p.weight_gram)
        db.add(oi)
        total += subtotal
        total_weight += decimal.Decimal(str(float(p.weight_gram))) * qty
        if inv:
            inv.quantity = inv.quantity - qty
            db.add(inv)
    order.total_amount = total
    order.total_weight = total_weight
    db.add(order); db.commit(); db.refresh(order)
    return {'order_id': order.id, 'total_amount': float(order.total_amount)}
