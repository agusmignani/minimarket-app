# Ventana de login

# modules/login.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import conectar 
from modules.menu import MenuApp

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimarket - Login")
        self.root.geometry("350x250")
        self.root.resizable(False, False)

        #Titulo
        tk.Label(root, text="Iniciar Sesión", font=("Arial", 16, "bold")).pack(oady=15)

        #Email
        tk.Label(root, text="Email:").pack(pady=5)
        self.email_entry = tk.Entry(root, width=30)
        self.email_entry.pack(pady=5)
        self.email_entry.insert(0, "agus@minimarket.com")

        #Rol
        tk.Label(root, text="Rol:").pack(pady=5)
        self.rol_var = tk.StringVar(value="admin")
        ttk.Combobox(root, textvariable=self.rol_var, values=["admin", "empleado"], state="readonly", width=27).pack(pady=5)

        #Boton
        tk.Button(root, text="Ingresar", bg="#18451C", fg="white", font=("Arial", 10, "bold"), command=self.login).pack(pady=15)

    def login(self):
        email = self.email_entry.get().strip()
        rol = self.rol_var.get()

        if not email or not rol:
            messagebox.showwarning("Campos incompletos", "Por favor, complete todos los campos.")
            return
        
        conn = conectar()
        if not conn:
            return
        
        try: 
            cursor = conn.cursor()
            cursor.execude("SELECT id_usuario, nombre, apellido, email FROM usuarios WHERE email = %s AND rol = %s", (email, rol))
            usuario = cursor.fetchone()
            conn.close()

            if usuario:
                self.root.destroy()
                root_menu = tk.Tk()
                MenuApp(root_menu, usuario)
                root_menu.mainloop()
            else:
                messagebox.showerror("Error de autenticación", "Email o rol incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al intentar iniciar sesión:\n{e}")