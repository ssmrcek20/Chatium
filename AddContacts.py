import customtkinter as ctk
import asyncio
import aiohttp

class AddContactFrame(ctk.CTkFrame):
    def __init__(self, master, cancel_callback, token):
        super().__init__(master)
        self.master = master
        self.cancel_callback = cancel_callback
        self.token = token
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Username").grid(row=0, column=0, padx=(20,10), pady=(20, 5), sticky="w")
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.grid(row=0, column=1, padx=(10,20), pady=(20, 5))

        ctk.CTkButton(self, text="Add", command=self.add_contact).grid(row=1, column=0, padx=10, pady=(15, 20))
        ctk.CTkButton(self, text="Cancel", command=self.cancel_callback).grid(row=1, column=1, padx=10, pady=(15, 20))

        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(5, 20))
        self.message_label.grid_remove()

    async def add_contact_request(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://localhost:5000/addchat", json=data, ssl=False, headers={"Authorization": f"Bearer {self.token}"}) as response:
                return response.status

    def add_contact(self):
        username = self.username_entry.get()
        data = [
            {"key": "username", "value": username}
        ]
        asyncio.run_coroutine_threadsafe(self._add_contact(data), self.master.loop)

    async def _add_contact(self, data):
        status = await self.add_contact_request(data)
        if status == 201:
            self.message_label.configure(text="Chat added successfully", text_color="green")
            self.message_label.grid()
            self.cancel_callback()
        else:
            self.message_label.configure(text="Failed to add chat", text_color="red")
            self.message_label.grid()