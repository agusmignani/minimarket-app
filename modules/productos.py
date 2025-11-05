# Gestión de productos
# modules/productos.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import conectar # Importa la función de conexión a la BD.

class ProductosApp:
    # Recibe el argumento 'es_admin' para determinar los permisos de la UI.
    def __init__(self, root, es_admin=False): 
        self.root = root
        self.es_admin = es_admin
        self.root.title("Gestión de Productos")

        frame_form = tk.Frame(root)
        frame_form.pack(pady=10, fill="x", padx=20)

        campos = ["Nombre", "Precio", "Stock", "Categoría", "Proveedor"] 
        self.entries = {}
        
        for i, campo in enumerate(campos):
            tk.Label(frame_form, text=campo + ":").grid(row=i, column=0, sticky="w", pady=2)
            
            if campo in ["Categoría", "Proveedor"]:
                # Usa Combobox de solo lectura para seleccionar FKs (categoría y proveedor).
                self.entries[campo] = ttk.Combobox(frame_form, width=30, state="readonly") 
            else:
                self.entries[campo] = tk.Entry(frame_form, width=33)
                
            self.entries[campo].grid(row=i, column=1, pady=2, padx=5)

        btn_frame = tk.Frame(frame_form)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Lógica de Permisos: Deshabilita los botones de modificación (CRUD) si no es administrador.
        if not self.es_admin:
            tk.Button(btn_frame, text="Agregar", state="disabled", bg="gray").pack(side="left", padx=5)
            tk.Button(btn_frame, text="Actualizar", state="disabled", bg="gray").pack(side="left", padx=5)
            tk.Button(btn_frame, text="Eliminar", state="disabled", bg="gray").pack(side="left", padx=5)
        else:
            # Botones activos para administradores.
            tk.Button(btn_frame, text="Agregar", bg="#4CAF50", fg="black",
                      command=self.agregar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Actualizar", bg="#2196F3", fg="black",
                      command=self.actualizar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Eliminar", bg="#F44336", fg="black",
                      command=self.eliminar).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Limpiar",
                      command=self.limpiar).pack(side="left", padx=5)

        # Configuración de la tabla Treeview para mostrar los productos.
        self.tree = ttk.Treeview(root, columns=("ID", "Nombre", "Precio", "Stock", "Cat", "Prov"),
                                 show="headings", height=15)
        
        col_widths = {"ID": 50, "Nombre": 150, "Precio": 80, "Stock": 70, "Cat": 100, "Prov": 100}
        for col, width in col_widths.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
            
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

        # Carga inicial de datos al iniciar la aplicación.
        self.cargar_categorias()
        self.cargar_proveedores()
        self.cargar_productos()
        # Enlaza el evento de selección de fila con la función 'seleccionar'.
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar) 

    def cargar_categorias(self):
        """Carga los nombres de las categorías en el Combobox."""
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            # Consulta para llenar el Combobox 'Categoría'.
            cursor.execute("SELECT nombre_categoria FROM categorias") 
            cats = [row[0] for row in cursor.fetchall()]
            self.entries["Categoría"]["values"] = cats
            conn.close()

    def cargar_proveedores(self):
        """Carga los nombres de los proveedores en el Combobox."""
        conn = conectar()
        # ... (Lógica similar a cargar_categorias, pero para proveedores) ...
        # Consulta para llenar el Combobox 'Proveedor'.
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM proveedores") 
            provs = [row[0] for row in cursor.fetchall()]
            self.entries["Proveedor"]["values"] = provs
            conn.close()

    def cargar_productos(self):
        """Carga todos los productos en la tabla Treeview."""
        # Limpia la tabla antes de cargar nuevos datos.
        for item in self.tree.get_children():
            self.tree.delete(item) 
            
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            # Consulta JOIN para obtener nombres de categoría y proveedor en lugar de solo IDs.
            # Se usan los nombres correctos de las columnas de la BD (id_productos, stock, nombre_categoria, etc.).
            cursor.execute("""
                SELECT 
                    p.id_productos, p.nombre, p.precio, p.stock, 
                    c.nombre_categoria, pr.nombre
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            """)
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row) # Inserta cada fila de la BD en la tabla UI.
                
            conn.close()

    def obtener_datos(self):
        """Recupera, valida y convierte los datos del formulario."""
        nombre = self.entries["Nombre"].get().strip()
        precio = self.entries["Precio"].get().strip()
        stock = self.entries["Stock"].get().strip() 
        cat = self.entries["Categoría"].get()
        prov = self.entries["Proveedor"].get()
        
        # Validación de campos vacíos.
        if not all([nombre, precio, stock, cat, prov]):
            messagebox.showwarning("Faltan datos", "Completa todos los campos")
            return None
            
        try:
            precio = float(precio)
            stock = int(stock) 
            # Validación de valores numéricos y restricciones (precio > 0, stock >= 0).
            if precio <= 0 or stock < 0: 
                raise ValueError
        except ValueError: 
            messagebox.showerror("Error", "El Precio debe ser > 0 y el Stock debe ser ≥ 0")
            return None
            
        return (nombre, precio, stock, cat, prov) 

    def agregar(self):
        """Inserta un nuevo producto en la base de datos."""
        datos = self.obtener_datos() 
        if not datos: 
            return
            
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            # INSERT con subconsultas: Obtiene los IDs de categoría y proveedor a partir de sus nombres.
            cursor.execute("""
                INSERT INTO productos (nombre, precio, stock, id_categoria, id_proveedor)
                VALUES (%s, %s, %s,
                        (SELECT id_categoria FROM categorias WHERE nombre_categoria=%s),
                        (SELECT id_proveedor FROM proveedores WHERE nombre=%s))
            """, (*datos,))  
            
            conn.commit() # Confirma la inserción en la BD.
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
        product_id = item["values"][0] # Recupera el ID del producto seleccionado (primera columna).
        
        datos = self.obtener_datos() 
        if not datos: 
            return
            
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            # UPDATE con subconsultas: Actualiza todos los campos, incluyendo las FKs usando nombres.
            # La cláusula WHERE asegura que solo se actualice el producto con el 'id_productos' seleccionado.
            cursor.execute("""
                UPDATE productos SET nombre=%s, precio=%s, stock=%s,
                id_categoria=(SELECT id_categoria FROM categorias WHERE nombre_categoria=%s),
                id_proveedor=(SELECT id_proveedor FROM proveedores WHERE nombre=%s)
                WHERE id_productos=%s
            """, (*datos, product_id))
            
            conn.commit()
            conn.close()
            
            self.cargar_productos()
            messagebox.showinfo("Éxito", "Producto actualizado exitosamente")

    def eliminar(self):
        """Elimina el producto seleccionado de la base de datos."""
        seleccion = self.tree.selection()
        # ... (Validación de selección) ...
            
        # Pide confirmación antes de la eliminación irreversible.
        if messagebox.askyesno("Confirmar Eliminación", "¿Estás seguro de que deseas eliminar este producto?"): 
            product_id = self.tree.item(seleccion[0])["values"][0]
            
            conn = conectar()
            if conn:
                cursor = conn.cursor()
                # DELETE: Elimina la fila usando la clave primaria 'id_productos'.
                cursor.execute("DELETE FROM productos WHERE id_productos=%s", (product_id,)) 
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
            # Inserta los datos de la fila seleccionada en los campos de entrada/combobox.
            self.entries["Nombre"].insert(0, valores[1])
            self.entries["Precio"].insert(0, valores[2])
            self.entries["Stock"].insert(0, valores[3]) 
            self.entries["Categoría"].set(valores[4])
            self.entries["Proveedor"].set(valores[5])

    def limpiar(self):
        """Limpia todos los campos del formulario."""
        # Recorre todos los campos (Entry y Combobox) y los vacía.
        for entry in self.entries.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, "end")
            elif isinstance(entry, ttk.Combobox):
                entry.set("")