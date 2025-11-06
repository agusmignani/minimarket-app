# modules/usuarios.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import conectar  # Importa la conexión a la BD

class UsuariosApp:
    def __init__(self, root, super_usuario=False):
        self.root = root
        self.super_usuario = super_usuario
        self.root.title("Gestión de Usuarios")

        frame_form = tk.Frame(root)
        frame_form.pack(pady=10, fill="x", padx=20)

        campos = ["Nombre", "Apellido", "Email", "Rol"]
        self.entries = {}

        for i, campo in enumerate(campos):
            tk.Label(frame_form, text=campo + ":").grid(row=i, column=0, sticky="w", pady=2)

            if campo == "Rol":
                # El rol puede ser "admin" o "usuario"
                self.entries[campo] = ttk.Combobox(frame_form, width=30, state="readonly",
                                                   values=["admin", "usuario"])
            else:
                self.entries[campo] = tk.Entry(frame_form, width=33)

            self.entries[campo].grid(row=i, column=1, pady=2, padx=5)

        # --- Botones de acción ---
        btn_frame = tk.Frame(frame_form)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        if not self.super_usuario:
            tk.Button(btn_frame, text="Agregar", state="disabled", bg="gray").pack(side="left", padx=5)
            tk.Button(btn_frame, text="Actualizar", state="disabled", bg="gray").pack(side="left", padx=5)
            tk.Button(btn_frame, text="Eliminar", state="disabled", bg="gray").pack(side="left", padx=5)
        else:
            tk.Button(btn_frame, text="Agregar", bg="#4CAF50", fg="black", command=self.agregar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Actualizar", bg="#2196F3", fg="black", command=self.actualizar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Eliminar", bg="#F44336", fg="black", command=self.eliminar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Limpiar", command=self.limpiar).pack(side="left", padx=5)

        # --- Tabla Treeview ---
        self.tree = ttk.Treeview(root, columns=("ID", "Nombre", "Apellido", "Email", "Rol"),
                                 show="headings", height=15)
        col_widths = {"ID": 50, "Nombre": 120, "Apellido": 120, "Email": 180, "Rol": 100}
        for col, width in col_widths.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(pady=10, padx=20, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar)

        self.cargar_usuarios()

    # ==============================
    # FUNCIONES DE BASE DE DATOS
    # ==============================

    def cargar_usuarios(self):
        """Carga los usuarios en la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario, nombre, apellido, email, rol FROM usuarios")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            conn.close()

    def obtener_datos(self):
        """Valida y devuelve los datos del formulario."""
        nombre = self.entries["Nombre"].get().strip()
        apellido = self.entries["Apellido"].get().strip()
        email = self.entries["Email"].get().strip()
        rol = self.entries["Rol"].get().strip()

        if not all([nombre, apellido, email, rol]):
            messagebox.showwarning("Faltan datos", "Completa todos los campos")
            return None

        if "@" not in email or "." not in email:
            messagebox.showerror("Email inválido", "Ingresa un correo electrónico válido")
            return None

        return (nombre, apellido, email, rol)

    def agregar(self):
        """Agrega un nuevo usuario."""
        datos = self.obtener_datos()
        if not datos:
            return

        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nombre, apellido, email, rol)
                VALUES (%s, %s, %s, %s)
            """, datos)
            conn.commit()
            conn.close()

            self.cargar_usuarios()
            self.limpiar()
            messagebox.showinfo("Éxito", "Usuario agregado exitosamente")

    def actualizar(self):
        """Actualiza un usuario existente."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona", "Selecciona un usuario de la tabla para actualizar")
            return

        user_id = self.tree.item(seleccion[0])["values"][0]
        datos = self.obtener_datos()
        if not datos:
            return

        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET nombre=%s, apellido=%s, email=%s, rol=%s
                WHERE id_usuario=%s
            """, (*datos, user_id))
            conn.commit()
            conn.close()

            self.cargar_usuarios()
            messagebox.showinfo("Éxito", "Usuario actualizado exitosamente")

    def eliminar(self):
        """Elimina el usuario seleccionado."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona", "Selecciona un usuario para eliminar")
            return

        if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este usuario?"):
            return

        user_id = self.tree.item(seleccion[0])["values"][0]
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (user_id,))
            conn.commit()
            conn.close()

            self.cargar_usuarios()
            self.limpiar()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")

    def seleccionar(self, event):
        """Carga los datos del usuario seleccionado."""
        seleccion = self.tree.selection()
        if seleccion:
            valores = self.tree.item(seleccion[0])["values"]
            self.limpiar()
            self.entries["Nombre"].insert(0, valores[1])
            self.entries["Apellido"].insert(0, valores[2])
            self.entries["Email"].insert(0, valores[3])
            self.entries["Rol"].set(valores[4])

    def limpiar(self):
        """Limpia todos los campos."""
        for entry in self.entries.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, "end")
            elif isinstance(entry, ttk.Combobox):
                entry.set("")
