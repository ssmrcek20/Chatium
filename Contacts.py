from threading import Thread
import customtkinter as ctk
import asyncio
import aiohttp
import socketio
from datetime import datetime
from AddContacts import AddContactFrame

class ContactsScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

class ChatScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

    def set_title(self, title):
        self.configure(label_text=title)

class ContactsPage(ctk.CTkFrame):
    def __init__(self, master, username, token, loop):
        super().__init__(master)
        self.master = master
        self.username = username
        self.token = token
        self.loop = loop
        self.selected_contact = None
        self.sio = socketio.Client(ssl_verify=False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        self.grid_columnconfigure(2, weight=1)
        self.create_widgets()
        self.setup_socketio()

    def create_widgets(self):
        self.contacts_frame = ContactsScrollableFrame(self, label_text="Chats", width=160, height=300)
        self.contacts_frame.grid(row=0, column=0, padx=(20, 0), pady=20, sticky="nsew")

        self.chat_frame = ChatScrollableFrame(self, label_text="Chat", width=500, height=300)
        self.chat_frame.grid(row=0, column=1, columnspan=2, padx=20, pady=20, sticky="nsew")

        self.add_contact_button = ctk.CTkButton(self, text="Add Chat", command=self.show_add_contact)
        self.add_contact_button.grid(row=1, column=0, padx=(20, 10), pady=(0, 20))

        self.message_text = ctk.CTkEntry(self)
        self.message_text.grid(row=1, column=1, padx=(20, 0), pady=(0, 20), sticky="ew")
        self.message_text.bind("<Return>", lambda event: self.send_message())
        self.message_text.grid_remove()

        self.send_message_button = ctk.CTkButton(self, text="Send", width=80, command=self.send_message)
        self.send_message_button.grid(row=1, column=2, padx=(0, 20), pady=(0, 20), sticky="e")
        self.send_message_button.grid_remove()

        self.add_contact_frame = AddContactFrame(self, self.show_contacts_frame, self.token)
        self.add_contact_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.add_contact_frame.grid_remove()

    async def fetch_contacts(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://localhost:5000/chats", ssl=False, headers={"Authorization": f"Bearer {self.token}"}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print("Failed to fetch contacts")
                    return []

    def load_contacts(self):
        return asyncio.run_coroutine_threadsafe(self._load_contacts(), self.loop)

    async def _load_contacts(self):
        contacts = await self.fetch_contacts()
        self.display_contacts(contacts)

    def display_contacts(self, contacts):
        for i, contact in enumerate(contacts):
            first_name = contact.get("name", "")
            last_name = contact.get("surname", "")
            username = contact.get("username", "")
            contact_button = ctk.CTkButton(self.contacts_frame, text=f"{first_name} {last_name}", command=lambda fn=first_name, ln=last_name, us=username: self.open_chat(fn, ln, us))
            contact_button.grid(row=i, column=0, padx=10, pady=10, sticky="w")

    async def fetch_chat(self, username):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://localhost:5000/chats?user={username}", ssl=False, headers={"Authorization": f"Bearer {self.token}"}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print("Failed to fetch chat messages")
                    return []

    def open_chat(self, first_name, last_name, username):
        self.selected_contact = username
        self.chat_frame.set_title(f"{first_name} {last_name}")

        self.message_text.grid()
        self.send_message_button.grid()
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

        asyncio.run_coroutine_threadsafe(self._open_chat(username), self.loop)
        Thread(target=self.start_socketio, args=(username,), daemon=True).start()

    async def _open_chat(self, username):
        messages = await self.fetch_chat(username)
        self.display_messages(messages)

    def display_messages(self, messages):
        for i, message in enumerate(messages):
            if message["sender_id"] == self.username:
                message_label = ctk.CTkLabel(self.chat_frame, text=message["content"], anchor="e", justify="left", fg_color=("#5a8fd4", "#4a7ebc"), text_color="white", corner_radius=6, wraplength=200)
                message_label.grid(row=i, column=1, padx=20, pady=5, sticky="e")
            else:
                message_label = ctk.CTkLabel(self.chat_frame, text=message["content"], anchor="w", justify="left", fg_color=("#2d4e7c", "#1a3b67"), text_color=("#DCE4EE", "#DCE4EE"), corner_radius=6, wraplength=200)
                message_label.grid(row=i, column=0, padx=20, pady=5, sticky="w")
        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    async def send_message_request(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://localhost:5000/send_message", json=data, ssl=False, headers={"Authorization": f"Bearer {self.token}"}) as response:
                return response.status

    def send_message(self):
        if self.selected_contact:
            username = self.selected_contact
            message = self.message_text.get().strip()
            if not message:
                return
            timestamp = datetime.now().isoformat()
            self.message_text.delete(0, "end")
            data = [
                {"key": "receiver", "value": username},
                {"key": "message", "value": message},
                {"key": "timestamp", "value": timestamp}
            ]
            asyncio.run_coroutine_threadsafe(self._send_message(data, message), self.loop)
        else:
            print("No contact selected")

    async def _send_message(self, data, message):
        status = await self.send_message_request(data)
        if status == 201:
            message_label = ctk.CTkLabel(self.chat_frame, text=message, anchor="e", justify="left", fg_color=("#5a8fd4", "#4a7ebc"), text_color="white", corner_radius=6, wraplength=200)
            message_label.grid(row=len(self.chat_frame.winfo_children()), column=1, padx=20, pady=5, sticky="e")
            self.chat_frame.update_idletasks()
            self.chat_frame._parent_canvas.yview_moveto(1.0)
        else:
            print("Failed to send message")

    def setup_socketio(self):
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('new_message', self.on_message)

    def start_socketio(self, username):
        try:
            self.sio.connect('wss://localhost:5000', headers={"Authorization": f"Bearer {self.token}"})
            self.sio.emit('join_chat', {'target_user': self.username})
        except socketio.exceptions.ConnectionError as e:
            print("Connection error:", e)

    def on_connect(self):
        print("Connected to WebSocket server")

    def on_disconnect(self):
        print("Disconnected from WebSocket server")

    def on_message(self, data, namespace):
        message_label = ctk.CTkLabel(self.chat_frame, text=data["content"], anchor="w", justify="left", fg_color=("#2d4e7c", "#1a3b67"), text_color=("#DCE4EE", "#DCE4EE"), corner_radius=6, wraplength=200)
        message_label.grid(row=len(self.chat_frame.winfo_children()), column=0, padx=20, pady=5, sticky="w")
        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def show_add_contact(self):
        self.contacts_frame.grid_remove()
        self.chat_frame.grid_remove()
        self.add_contact_button.grid_remove()
        self.message_text.grid_remove()
        self.send_message_button.grid_remove()
        self.add_contact_frame.grid()

    def show_contacts_frame(self):
        self.add_contact_frame.grid_remove()
        self.contacts_frame.grid()
        self.chat_frame.grid()
        self.add_contact_button.grid()
        self.message_text.grid()
        self.send_message_button.grid()
        self.load_contacts()
