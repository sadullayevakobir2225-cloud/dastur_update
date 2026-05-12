from gui_app import MarketApp, LoginWindow

def start_app():
    # Login to'g'ri bo'lsa, asosiy oynani ochish funksiyasi
    app = MarketApp()
    app.mainloop()

if __name__ == "__main__":
    # Dastur ishga tushganda birinchi login oynasi ochiladi
    login_screen = LoginWindow(on_success=start_app)
    login_screen.mainloop()
