import flet as ft

def main(page: ft.Page):
    page.title = "Prueba"
    page.add(ft.Text("Hola mundo, funciona!"))

if __name__ == "__main__":
    ft.app(target=main, host="0.0.0.0", port=8000)
