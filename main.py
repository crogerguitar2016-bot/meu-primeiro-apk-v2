from kivy.app import App
from kivy.uix.label import Label

class MeuPrimeiroApp(App):
    def build(self):
        return Label(text="Olá! Meu primeiro APK 😄")

if __name__ == "__main__":
    MeuPrimeiroApp().run()
