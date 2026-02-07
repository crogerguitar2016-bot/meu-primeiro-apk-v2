from kivy.app import App
from kivy.uix.label import Label

class MeuApp(App):
    def build(self):
        return Label(text='Meu primeiro APK com GitHub Actions')

MeuApp().run()
