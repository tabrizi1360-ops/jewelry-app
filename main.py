from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import requests
from kivy.properties import ListProperty, DictProperty
from app_config import API_URL

KV = '''
ScreenManager:
    ProductListScreen:
    CartScreen:

<ProductListScreen>:
    name: 'list'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'فروشگاه جواهرات'
            size_hint_y: None
            height: '48dp'
        ScrollView:
            GridLayout:
                id: grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Button:
                text: 'سبد'
                on_release: app.root.current = 'cart'

<CartScreen>:
    name: 'cart'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'سبد خرید'
            size_hint_y: None
            height: '48dp'
        ScrollView:
            GridLayout:
                id: cart_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Button:
                text: 'بازگشت'
                on_release: app.root.current = 'list'
            Button:
                text: 'ثبت سفارش'
                on_release: root.place_order()
'''

class ProductListScreen(Screen):
    pass

class CartScreen(Screen):
    def place_order(self):
        app = App.get_running_app()
        if not app.cart:
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            Popup(title='خطا', content=Label(text='سبد خالی است'), size_hint=(0.6,0.4)).open(); return
        payload = {'items':[{'product_id': pid, 'quantity': qty} for pid, qty in app.cart.items()], 'payment_method': 'cash'}
        try:
            r = requests.post(f'{API_URL}/api/orders', json=payload, timeout=10)
            if r.status_code == 200:
                app.cart = {}
                from kivy.uix.popup import Popup
                from kivy.uix.label import Label
                Popup(title='موفق', content=Label(text='سفارش ثبت شد'), size_hint=(0.6,0.4)).open()
            else:
                raise Exception(r.text)
        except Exception as e:
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            Popup(title='خطا', content=Label(text=str(e)), size_hint=(0.8,0.6)).open()

class JewelryApp(App):
    products = ListProperty([])
    cart = DictProperty({})

    def build(self):
        self.sm = Builder.load_string(KV)
        self.fetch_products()
        return self.sm

    def fetch_products(self):
        try:
            r = requests.get(f'{API_URL}/api/products', timeout=8)
            if r.status_code == 200:
                self.products = r.json()
                grid = self.sm.get_screen('list').ids.grid
                grid.clear_widgets()
                for p in self.products:
                    from kivy.uix.boxlayout import BoxLayout
                    from kivy.uix.image import AsyncImage
                    from kivy.uix.label import Label
                    from kivy.uix.button import Button
                    bl = BoxLayout(size_hint_y=None, height='140dp')
                    img = AsyncImage(source=p['images'][0]['url'] if p['images'] else '')
                    bl.add_widget(img)
                    col = BoxLayout(orientation='vertical')
                    col.add_widget(Label(text=f"{p['name']} - {p['weight_gram']} g"))
                    col.add_widget(Label(text=f"سود: {p['profit_percent']}%"))
                    btn = Button(text='اضافه به سبد')
                    def add_closure(pid=p['id']):
                        def _add(x):
                            self.cart[pid] = self.cart.get(pid,0) + 1
                        return _add
                    btn.bind(on_release=add_closure())
                    col.add_widget(btn)
                    bl.add_widget(col)
                    grid.add_widget(bl)
        except Exception as e:
            print('Failed to fetch products', e)

if __name__ == '__main__':
    JewelryApp().run()
