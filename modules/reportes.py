# Reportes
# modules/reportes.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import conectar # Función para la conexión a la base de datos.

class ReportesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reportes de Inventario y Movimientos")
        
        # Crea el contenedor de pestañas (Notebook) para organizar los reportes.
        notebook = ttk.Notebook(root) 
        notebook.pack(pady=10, padx=20, fill="both", expand=True)

        # --- Pestaña 1: Stock Actual ---
        frame1 = tk.Frame(notebook)
        notebook.add(frame1, text="Stock Actual") # Añade la primera pestaña al Notebook.
        
        # Treeview para mostrar el stock de productos.
        self.tree_stock = ttk.Treeview(frame1, columns=("Producto", "Stock", "Categoría"), show="headings")
        
        for col, text in zip(self.tree_stock["columns"], ["Producto", "Stock", "Categoría"]):
            self.tree_stock.heading(col, text=text)
            self.tree_stock.column(col, width=200, anchor="center") 
            
        self.tree_stock.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Pestaña 2: Movimientos del Día ---
        frame2 = tk.Frame(notebook)
        notebook.add(frame2, text="Movimientos del Día") # Añade la segunda pestaña al Notebook.
        
        # Treeview para mostrar los movimientos registrados.
        self.tree_mov = ttk.Treeview(frame2, columns=("Hora", "Producto", "Tipo", "Cantidad"), show="headings")
        
        for col, text in zip(self.tree_mov["columns"], ["Hora", "Producto", "Tipo", "Cantidad"]):
            self.tree_mov.heading(col, text=text)
            self.tree_mov.column(col, width=150, anchor="center")
            
        self.tree_mov.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.cargar_reportes() # Llama a la función que ejecuta las consultas SQL.

    def cargar_reportes(self):
        conn = conectar()
        if not conn:
            messagebox.showerror("Error de Conexión", "No se pudo conectar a la base de datos.")
            return

        cursor = conn.cursor()

        # 1. Reporte de Stock Actual
        for i in self.tree_stock.get_children():
            self.tree_stock.delete(i) # Limpia la tabla antes de recargar.
            
        try:
            # Consulta para obtener los productos, su stock y el nombre de su categoría.
            # Se usa JOIN y se filtra solo por productos con stock > 0, ordenados descendentemente.
            cursor.execute("""
                SELECT p.nombre, p.stock, c.nombre_categoria
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.stock > 0
                ORDER BY p.stock DESC
            """)
            
            for row in cursor.fetchall():
                self.tree_stock.insert("", "end", values=row) # Inserta cada producto en la tabla de Stock.
        except Exception as e:
            messagebox.showerror("Error SQL (Stock)", f"Ocurrió un error al cargar el stock: {e}")

        # 2. Reporte de Movimientos del Día
        for i in self.tree_mov.get_children():
            self.tree_mov.delete(i) # Limpia la tabla.
            
        try:
            # Consulta para obtener los movimientos del día actual (WHERE DATE(m.fecha) = CURDATE()).
            # Utiliza DATE_FORMAT para mostrar solo la hora (HH:MM:SS) y JOINs para obtener el nombre del producto y el usuario.
            cursor.execute("""
                SELECT DATE_FORMAT(m.fecha, '%H:%i:%s'), p.nombre, m.tipo, m.cantidad, u.nombre
                FROM movimientos_inventario m
                JOIN productos p ON m.id_producto = p.id_productos
                LEFT JOIN usuarios u ON m.id_usuario = u.id_usuario 
                WHERE DATE(m.fecha) = CURDATE()
                ORDER BY m.fecha DESC
            """)
            
            for row in cursor.fetchall():
                tipo_display = row[2].capitalize() # Capitaliza 'entrada' o 'salida' para mejor visualización.
                # Inserta el movimiento en la tabla.
                self.tree_mov.insert("", "end", values=(row[0], row[1], tipo_display, row[3]))
        except Exception as e:
            messagebox.showerror("Error SQL (Movimientos)", f"Ocurrió un error al cargar movimientos: {e}")


        conn.close() # Cierra la conexión después de completar todas las consultas.