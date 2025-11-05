# Gestión de productos
# modules/productos.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import conectar

class ProductosApp:
    def __init__(self, root, es_admin=False):
        self.root = root
        self.es_admin = es_admin
        self.root.title("Gestión de Productos")

        # --- Frame superior: Formulario y Botones ---
        frame_form = tk.Frame(root)
        frame_form.pack(pady=10, fill="x", padx=20)

        # 1. Campos
        campos = ["Nombre", "Precio", "Cantidad", "Categoría", "Proveedor"]
        self.entries = {}
        
        for i, campo in enumerate(campos):
            tk.Label(frame_form, text=campo + ":").grid(row=i, column=0, sticky="w", pady=2)
            
            if campo in ["Categoría", "Proveedor"]:
                self.entries[campo] = ttk.Combobox(frame_form, width=30)
            else:
                self.entries[campo] = tk.Entry(frame_form, width=33)
                
            self.entries[campo].grid(row=i, column=1, pady=2, padx=5)

        # 2. Botones de Acción (Condicional por Rol)
        btn_frame = tk.Frame(frame_form)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        if not self.es_admin:
            # Deshabilitar botones para usuarios no administradores
            tk.Button(btn_frame, text="Agregar", state="disabled", bg="gray").pack(side="left", padx=5)
            tk.Button(btn_frame, text="Actualizar", state="disabled", bg="gray").pack(side="left", padx=5)
            tk.Button(btn_frame, text="Eliminar", state="disabled", bg="gray").pack(side="left", padx=5)
        else:
            # Botones activos para administradores
            tk.Button(btn_frame, text="Agregar", bg="#4CAF50", fg="green",
                      command=self.agregar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Actualizar", bg="#2196F3", fg="blue",
                      command=self.actualizar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Eliminar", bg="#F44336", fg="red",
                      command=self.eliminar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Limpiar",
                      command=self.limpiar).pack(side="left", padx=5)

        # --- Tabla de Productos (Treeview) ---
        self.tree = ttk.Treeview(root, columns=("ID", "Nombre", "Precio", "Cantidad", "Cat", "Prov"),
                                 show="headings", height=15)
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
            
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

        # Cargar datos iniciales y configurar selección
        self.cargar_categorias()
        self.cargar_proveedores()
        self.cargar_productos()
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar)

    def cargar_categorias(self):
        """Carga los nombres de las categorías en el Combobox."""
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre_categoria FROM categorias")
            cats = [row[0] for row in cursor.fetchall()]
            self.entries["Categoría"]["values"] = cats
            conn.close()

    def cargar_proveedores(self):
        """Carga los nombres de los proveedores en el Combobox."""
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM proveedores")
            provs = [row[0] for row in cursor.fetchall()]
            self.entries["Proveedor"]["values"] = provs
            conn.close()

    def cargar_productos(self):
        """Carga todos los productos en la tabla Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.nombre, p.precio, p.cantidad, c.nombre, pr.nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            """)
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
                
            conn.close()

    def obtener_datos(self):
        """Recupera, valida y convierte los datos del formulario."""
        nombre = self.entries["Nombre"].get().strip()
        precio = self.entries["Precio"].get().strip()
        cantidad = self.entries["Cantidad"].get().strip()
        cat = self.entries["Categoría"].get()
        prov = self.entries["Proveedor"].get()
        
        if not all([nombre, precio, cantidad, cat, prov]):
            messagebox.showwarning("Faltan datos", "Completa todos los campos")
            return None
            
        try:
            precio = float(precio)
            cantidad = int(cantidad)
            if precio <= 0 or cantidad < 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "El Precio debe ser > 0 y la Cantidad debe ser ≥ 0")
            return None
            
        return (nombre, precio, cantidad, cat, prov)

    def agregar(self):
        """Inserta un nuevo producto en la base de datos."""
        datos = self.obtener_datos()
        if not datos: 
            return
            
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            # La inserción utiliza subconsultas para obtener los IDs de Categoría y Proveedor por su nombre
            cursor.execute("""
                INSERT INTO productos (nombre, precio, cantidad, id_categoria, id_proveedor)
                VALUES (%s, %s, %s,
                        (SELECT id FROM categorias WHERE nombre_categoria=%s),
                        (SELECT id FROM proveedores WHERE nombre=%s))
            """, (*datos,))  # Desempaqueta la tupla 'datos'
            
            conn.commit()
            conn.close()
            
            self.cargar_productos()
            self.limpiar()
            messagebox.showinfo("Éxito", "Producto agregado exitosamente")

    def actualizar(self):
        """Actualiza el producto seleccionado en la tabla."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona", "Selecciona un producto de la tabla para actualizar")
            return
            
        item = self.tree.item(seleccion[0])
        product_id = item["values"][0]  # El ID es el primer valor
        
        datos = self.obtener_datos()
        if not datos: 
            return
            
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos SET nombre=%s, precio=%s, cantidad=%s,
                categoria_id=(SELECT id FROM categorias WHERE nombre_categoria=%s),
                proveedor_id=(SELECT id FROM proveedores WHERE nombre=%s)
                WHERE id=%s
            """, (*datos, product_id))
            
            conn.commit()
            conn.close()
            
            self.cargar_productos()
            messagebox.showinfo("Éxito", "Producto actualizado exitosamente")

    def eliminar(self):
        """Elimina el producto seleccionado de la base de datos."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona", "Selecciona un producto de la tabla para eliminar")
            return
            
        if messagebox.askyesno("Confirmar Eliminación", "¿Estás seguro de que deseas eliminar este producto?"):
            product_id = self.tree.item(seleccion[0])["values"][0]
            
            conn = conectar()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM productos WHERE id:productos=%s", (product_id,))
                conn.commit()
                conn.close()
                
                self.cargar_productos()
                self.limpiar()
                messagebox.showinfo("Éxito", "Producto eliminado")

    def seleccionar(self, event):
        """Carga los datos del producto seleccionado en el formulario."""
        seleccion = self.tree.selection()
        if seleccion:
            valores = self.tree.item(seleccion[0])["values"]
            self.limpiar()
            # Insertar los valores del producto seleccionado en los campos del formulario
            self.entries["Nombre"].insert(0, valores[1])
            self.entries["Precio"].insert(0, valores[2])
            self.entries["Stock"].insert(0, valores[3])
            # Usar .set() para Combobox
            self.entries["Categoría"].set(valores[4])
            self.entries["Proveedor"].set(valores[5])

    def limpiar(self):
        """Limpia todos los campos del formulario."""
        for entry in self.entries.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, "end")
            elif isinstance(entry, ttk.Combobox):
                entry.set("")