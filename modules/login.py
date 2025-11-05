# Ventana de login

# modules/login.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import conectar # Importa la función que establece la conexión a la base de datos.
from modules.menu import MenuApp # Importa la clase principal del menú, a la que se accederá tras el login exitoso.

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimarket - Login")
        self.root.geometry("350x250")
        self.root.resizable(False, False) # Impide que el usuario cambie el tamaño de la ventana de login.

        #Titulo
        tk.Label(root, text="Iniciar Sesión", font=("Arial", 16, "bold")).pack(pady=15)

        #Email
        tk.Label(root, text="Email:").pack(pady=5)
        self.email_entry = tk.Entry(root, width=30)
        self.email_entry.pack(pady=5)
        self.email_entry.insert(0, "agus@minimarket.com") #Inserta un email de prueba por defecto para facilitar el testeo.

        #Rol
        tk.Label(root, text="Rol:").pack(pady=5)
        self.rol_var = tk.StringVar(value="admin") # Variable de control para el Combobox del rol.
        ttk.Combobox(root, textvariable=self.rol_var, values=["admin", "empleado"], 
                     state="readonly", width=27).pack(pady=5) # El rol solo puede ser seleccionado de la lista (readonly).

        #Boton
        tk.Button(root, text="Ingresar", bg="#18451C", fg="white", 
                  font=("Arial", 10, "bold"), command=self.login).pack(pady=15) # Llama al método 'login' al hacer clic.

    def login(self):
        email = self.email_entry.get().strip() # Obtiene y limpia el email introducido.
        rol = self.rol_var.get() # Obtiene el rol seleccionado del Combobox.

        if not email or not rol:
            messagebox.showwarning("Campos incompletos", "Por favor, complete todos los campos.")
            return
        
        conn = conectar() # Intenta establecer la conexión a la base de datos.
        if not conn:
            return
        
        try: 
            cursor = conn.cursor()
            # Consulta SQL que verifica si existe un usuario con el 'email' Y el 'rol' especificados.
            cursor.execute("SELECT id_usuario, nombre, apellido, email, rol FROM usuarios WHERE email = %s AND rol = %s", (email, rol))
            usuario = cursor.fetchone() # Recupera la primera fila que coincida (el usuario), o None si no hay coincidencias.
            conn.close() # Cierra la conexión a la BD inmediatamente después de la consulta.

            if usuario:
                self.root.destroy() # Cierra la ventana actual de login.
                root_menu = tk.Tk()
                MenuApp(root_menu, usuario) # Inicializa la aplicación del menú, pasando los datos del 'usuario' autenticado.
                root_menu.mainloop()
            else:
                messagebox.showerror("Error de autenticación", "Email o rol incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al intentar iniciar sesión:\n{e}")