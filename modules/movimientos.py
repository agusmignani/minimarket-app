# Entradas y salidas
# modules/movimientos.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import conectar # Función para conectarse a la BD.
from datetime import datetime

class MovimientosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Movimientos")
        
        # --- Formulario de Registro ---
        frame = tk.Frame(root)
        frame.pack(pady=20, padx=20)
        
        # Producto
        tk.Label(frame, text="Producto:").grid(row=0, column=0, sticky="w")
        self.producto_cb = ttk.Combobox(frame, width=40) # Campo para seleccionar el producto.
        self.producto_cb.grid(row=0, column=1, padx=5)
        
        # Tipo de Movimiento (Entrada/Salida)
        tk.Label(frame, text="Tipo:").grid(row=1, column=0, sticky="w", pady=5)
        self.tipo_var = tk.StringVar(value="salida") # Variable para controlar la selección del Radiobutton.
        
        ttk.Radiobutton(frame, text="Entrada", variable=self.tipo_var,
                        value="entrada").grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(frame, text="Salida (Venta)", variable=self.tipo_var,
                        value="salida").grid(row=1, column=1, sticky="e")
        
        # Cantidad
        tk.Label(frame, text="Cantidad:").grid(row=2, column=0, sticky="w", pady=5)
        self.cantidad_entry = tk.Entry(frame, width=20)
        self.cantidad_entry.grid(row=2, column=1, sticky="w")
        
        # Botón Registrar
        tk.Button(frame, text="REGISTRAR", bg="#FF5722", fg="blue", font=("Arial", 10, "bold"),
                  command=self.registrar).grid(row=3, column=0, columnspan=2, pady=15) # Llama al método 'registrar'.

        # --- Tabla de Movimientos Recientes (Treeview) ---
        self.tree = ttk.Treeview(root, columns=("Fecha", "Producto", "Tipo", "Cant", "Usuario"), show="headings")
        
        for col, text in zip(self.tree["columns"], ["Fecha", "Producto", "Tipo", "Cantidad", "Usuario"]):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=140)
            
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Cargar datos iniciales
        self.cargar_productos()
        self.cargar_movimientos()

    def cargar_productos(self):
        """Carga los productos disponibles en el Combobox."""
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_productos, nombre FROM productos")
            # Crea un diccionario para mapear el nombre del producto a su ID (nombre: id)
            productos = {row[1]: row[0] for row in cursor.fetchall()} 
            self.producto_cb["values"] = list(productos.keys())
            self.productos_dict = productos # Guarda el diccionario para obtener el ID en 'registrar'.
            conn.close()

    def cargar_movimientos(self):
        """Carga los últimos 20 movimientos de inventario en la tabla."""
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            # Consulta JOIN para obtener el nombre del producto y el nombre del usuario junto al movimiento.
            # Limita a 20 resultados ordenados por fecha descendente.
            cursor.execute("""
                SELECT m.fecha, p.nombre, m.tipo, m.cantidad, u.nombre
                FROM movimientos_inventario m
                JOIN productos p ON m.id_producto = p.id_productos
                LEFT JOIN usuarios u ON m.id_usuario = u.id_usuario
                ORDER BY m.fecha DESC LIMIT 20
            """)
            
            for row in cursor.fetchall():
                tipo = row[2].upper()
                # Inserta en la posición 0 ("") para que los movimientos más recientes aparezcan arriba.
                self.tree.insert("", 0, values=(row[0], row[1], tipo, row[3], row[4])) 
                
            conn.close()

    def registrar(self):
        """Valida y registra un nuevo movimiento de inventario."""
        producto_nombre = self.producto_cb.get()
        tipo = self.tipo_var.get()
        cantidad_str = self.cantidad_entry.get()

        # 1. Validación de campos y conversión de cantidad.
        # ... (Validación de campos vacíos y cantidad positiva) ...
        
        id_producto = self.productos_dict.get(producto_nombre) # Obtiene el ID del producto a partir del nombre seleccionado.

        conn = conectar()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        # 2. Lógica de Stock: Solo se ejecuta si el movimiento es una SALIDA (venta).
        if tipo == "salida":
            # Consulta el stock actual del producto.
            cursor.execute("SELECT stock FROM productos WHERE id_productos = %s", (id_producto,))
            stock = cursor.fetchone()
            
            stock_actual = stock[0]
            if cantidad > stock_actual:
                # Si la cantidad de venta supera el stock, emite un error y cancela la operación.
                messagebox.showerror("Stock insuficiente", f"Solo hay {stock_actual} unidades disponibles para la venta.")
                conn.close()
                return

        # 3. Registrar movimiento en la tabla 'movimientos_inventario'.
        # El ID del usuario está fijado a '1' (hardcodeado) en este ejemplo.
        cursor.execute("""
            INSERT INTO movimientos_inventario (id_producto, tipo, cantidad, id_usuario)
            VALUES (%s, %s, %s, 1)
        """, (id_producto, tipo, cantidad))
        
        # 4. Actualizar stock en la tabla 'productos'.
        op = "+" if tipo == "entrada" else "-" # Determina la operación (+ para entrada, - para salida).
        # Ejecuta el UPDATE dinámico para sumar o restar al campo 'stock'.
        cursor.execute(f"UPDATE productos SET stock = stock {op} %s WHERE id_productos = %s", (cantidad, id_producto)) 
        
        conn.commit() # Confirma los dos cambios (INSERT y UPDATE) como una sola transacción.
        conn.close()
        
        messagebox.showinfo("Éxito", f"Movimiento registrado: {tipo.upper()} de {cantidad} unidad(es) de {producto_nombre}.")
        
        # 5. Limpiar y recargar
        self.cargar_movimientos()
        self.cantidad_entry.delete(0, "end")