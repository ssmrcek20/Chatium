import customtkinter as ctk
import asyncio
import aiohttp

class RegistrationPage(ctk.CTkFrame):
    def __init__(self, master, switch_to_login):
        super().__init__(master)
        self.master = master
        self.switch_to_login = switch_to_login
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Name").grid(row=0, column=0, padx=(20,10), pady=(20, 5), sticky="w")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=0, column=1, padx=(10,20), pady=(20, 5))

        ctk.CTkLabel(self, text="Surname").grid(row=1, column=0, padx=(20,10), pady=5, sticky="w")
        self.surname_entry = ctk.CTkEntry(self)
        self.surname_entry.grid(row=1, column=1, padx=(10,20), pady=5)

        ctk.CTkLabel(self, text="Username").grid(row=2, column=0, padx=(20,10), pady=5, sticky="w")
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.grid(row=2, column=1, padx=(10,20), pady=5)

        ctk.CTkLabel(self, text="Password").grid(row=3, column=0, padx=(20,10), pady=5, sticky="w")
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.grid(row=3, column=1, padx=(10,20), pady=5)

        ctk.CTkButton(self, text="Register", command=self.register).grid(row=4, column=0, columnspan=2, padx=10, pady=(15, 5))
        ctk.CTkButton(self, text="Back to Login", command=self.switch_to_login).grid(row=5, column=0, columnspan=2, padx=10, pady=(5, 20))

        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 20))
        self.message_label.grid_remove()

    async def register_request(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:5000/register", json=data) as response:
                return response.status

    def register(self):
        name = self.name_entry.get()
        surname = self.surname_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        data = [
            {"key": "name", "value": name},
            {"key": "surname", "value": surname},
            {"key": "username", "value": username},
            {"key": "password", "value": password}
        ]
        asyncio.run_coroutine_threadsafe(self._perform_registration(data), self.master.loop)

    async def _perform_registration(self, data):
        status = await self.register_request(data)
        if status == 201:
            self.message_label.configure(text="Registration successful", text_color="green")
            self.message_label.grid()
            self.switch_to_login()
        else:
            self.message_label.configure(text="Registration failed", text_color="red")
            self.message_label.grid()
