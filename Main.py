import customtkinter as ctk
import asyncio
import threading
from Login import LoginPage
from Registration import RegistrationPage
from Contacts import ContactsPage

class Window(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chatium")
        self.geometry("800x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_event_loop, daemon=True).start()

        self.login_page = LoginPage(self, self.show_contacts_page, self.show_registration_page)
        self.registration_page = RegistrationPage(self, self.show_login_page)
        self.contacts_page = None

        self.login_page.grid(row=0, column=0)
        self.registration_page.grid(row=0, column=0)

        self.show_login_page()

    def start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def show_login_page(self):
        if self.contacts_page:
            self.contacts_page.grid_remove()
        self.registration_page.grid_remove()
        self.login_page.grid()

    def show_registration_page(self):
        self.login_page.grid_remove()
        if self.contacts_page:
            self.contacts_page.grid_remove()
        self.registration_page.grid()

    def show_contacts_page(self, username, token):
        self.login_page.grid_remove()
        self.registration_page.grid_remove()
        self.contacts_page = ContactsPage(self, username, token, self.loop)
        self.contacts_page.grid(row=0, column=0)
        asyncio.run_coroutine_threadsafe(self.contacts_page.load_contacts(), self.loop)

window = Window()
window.mainloop()