import customtkinter as ctk
import asyncio
import aiohttp

class LoginPage(ctk.CTkFrame):
    def __init__(self, master, switch_to_contacts, switch_to_registration):
        super().__init__(master)
        self.master = master
        self.switch_to_contacts = switch_to_contacts
        self.switch_to_registration = switch_to_registration
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Username").grid(row=0, column=0, padx=(20,10), pady=(20, 5), sticky="w")
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.grid(row=0, column=1, padx=(10,20), pady=(20, 5))

        ctk.CTkLabel(self, text="Password").grid(row=1, column=0, padx=(20,10), pady=5, sticky="w")
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=(10,20), pady=5)

        ctk.CTkButton(self, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, padx=10, pady=(15, 5))
        ctk.CTkButton(self, text="Register", command=self.switch_to_registration).grid(row=3, column=0, columnspan=2, padx=10, pady=(5, 20))

        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.grid(row=4, column=0, columnspan=2, padx=10, pady=(5, 20))
        self.message_label.grid_remove()

    async def login_request(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://localhost:5000/login", json=data, ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        data = [
            {"key": "username", "value": username},
            {"key": "password", "value": password}
        ]
        asyncio.run_coroutine_threadsafe(self._login(data), self.master.loop)

    async def _login(self, data):
        response = await self.login_request(data)
        if response:
            token = response.get("access_token")
            self.message_label.configure(text="Login successful", text_color="green")
            self.message_label.grid()
            self.switch_to_contacts(data[0]["value"], token)
        else:
            self.message_label.configure(text="Login failed", text_color="red")
            self.message_label.grid()
