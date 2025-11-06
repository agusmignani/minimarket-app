import tkinter as tk
from tkinter import ttk, messagebox
from modules.productos import ProductosApp  # Importa la clase de gestión de productos.
from modules.movimientos import MovimientosApp  # Importa la clase para registrar movimientos.
from modules.reportes import ReportesApp  # Importa la clase para visualizar reportes.
from modules.usuarios import UsuariosApp  # Importa la clase de gestión de usuarios.

class MenuApp:
    # Recibe 'root' (ventana principal) y 'usuario' (datos del usuario autenticado).
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        # Establece el título de la ventana usando el email del usuario (índice 3).
        self.root.title(f"Minimarket - {usuario[3].title()}") 
        self.root.geometry("800x500")

        # Muestra el nombre (índice 1) y el rol (índice 4) del usuario en la UI.
        tk.Label(root, text=f"Usuario: {usuario[1]} ({usuario[4]})",
                 font=("Arial", 10)).pack(anchor="ne", padx=20, pady=10) 
        
        tk.Label(root, text="MINIMARKET FULLSTACK B", font=("Arial", 18, "bold")).pack(pady=20)
        
        btn_style = {"width": 30, "height": 2, "font": ("Arial", 11, "bold")} # Define el estilo uniforme para los botones principales.
        
        # Botones de navegación. El comando llama al método que abre la ventana correspondiente.
        tk.Button(root, text="GESTIÓN DE PRODUCTOS", bg="#2196F3",
                  fg="white", **btn_style, command=self.abrir_productos).pack(pady=10)
        
        tk.Button(root, text="GESTIÓN DE USUARIOS", bg="#F5F242",
                  fg="white", **btn_style, command=self.abrir_usuarios).pack(pady=10)
        
        tk.Button(root, text="REGISTRAR MOVIMIENTOS", bg="#FF9800", fg="white",
                  **btn_style, command=self.abrir_movimientos).pack(pady=10)
        
        tk.Button(root, text="VER REPORTES", bg="#9C27B0", fg="white",
                  **btn_style, command=self.abrir_reportes).pack(pady=10)
        
        # El comando 'root.destroy' cierra esta ventana de menú.
        tk.Button(root, text="CERRAR SESIÓN", bg="#F44336", fg="white",
                  **btn_style, command=root.destroy).pack(pady=20)

    def abrir_productos(self):
        # Lógica de Permisos: Verifica si el rol del usuario (índice 4) es "admin".
        if self.usuario[4] == "admin": 
            # Si es admin, abre la ventana de productos y pasa 'es_admin=True' a la clase ProductosApp.
            self.nueva_ventana("Gestión de Productos", lambda root: ProductosApp(root, es_admin=True)) 
        else:
            # Si no es admin, notifica la restricción.
            messagebox.showwarning("Acceso denegado", "Solo el admin puede gestionar productos") 

    def abrir_usuarios(self):
        # Lógica de Permisos: Verifica si el rol del usuario (índice 4) es "super_usuario".
        if self.usuario[4] == "super_usuario": 
            # Si es super_usuario, abre la ventana de gestión de usuarios.
            self.nueva_ventana("Gestión de Usuarios", lambda root: UsuariosApp(root, super_usuario=True)) 
        else:
            # Si no es super_usuario, notifica la restricción.
            messagebox.showwarning("Acceso denegado", "Solo el super usuario puede gestionar usuarios")

    def abrir_movimientos(self):
        # Abre la ventana de Movimientos.
        self.nueva_ventana("Registro de Movimientos", lambda root: MovimientosApp(root))

    def abrir_reportes(self):
        # Abre la ventana de Reportes.
        self.nueva_ventana("Reportes de Inventario", lambda root: ReportesApp(root))

    # Función genérica para crear ventanas secundarias.
    def nueva_ventana(self, titulo, clase):
        ventana = tk.Toplevel(self.root) # Crea una nueva ventana de alto nivel, hija de la principal.
        ventana.title(titulo)
        ventana.geometry("900x600")
        clase(ventana) # Inicializa la aplicación específica (Productos, Movimientos, Reportes) dentro de la nueva ventana.