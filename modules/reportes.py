# Reportes
# modules/reportes.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import conectar

class ReportesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reportes")
        
        # Crear el Notebook (contenedor de pestañas)
        notebook = ttk.Notebook(root)
        notebook.pack(pady=10, padx=20, fill="both", expand=True)

        # --- Pestaña 1: Stock Actual ---
        frame1 = tk.Frame(notebook)
        notebook.add(frame1, text="Stock Actual")
        
        # Treeview para Stock Actual
        self.tree_stock = ttk.Treeview(frame1, columns=("Producto", "Stock", "Categoría"), show="headings")
        
        for col, text in zip(self.tree_stock["columns"], ["Producto", "Stock", "Categoría"]):
            self.tree_stock.heading(col, text=text)
            self.tree_stock.column(col, width=200)
            
        self.tree_stock.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Pestaña 2: Movimientos del Día ---
        frame2 = tk.Frame(notebook)
        notebook.add(frame2, text="Movimientos del Día")
        
        # Treeview para Movimientos
        self.tree_mov = ttk.Treeview(frame2, columns=("Hora", "Producto", "Tipo", "Cant"), show="headings")
        
        for col, text in zip(self.tree_mov["columns"], ["Hora", "Producto", "Tipo", "Cantidad"]):
            self.tree_mov.heading(col, text=text)
            self.tree_mov.column(col, width=150)
            
        self.tree_mov.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cargar los datos al iniciar
        self.cargar_reportes()

    def cargar_reportes(self):
        conn = conectar()
        if not conn:
            return

        cursor = conn.cursor()

        # 1. Stock actual
        for i in self.tree_stock.get_children():
            self.tree_stock.delete(i)
            
        cursor.execute("""
            SELECT p.nombre, p.cantidad, c.nombre
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE p.cantidad > 0
            ORDER BY p.cantidad DESC
        """)
        
        for row in cursor.fetchall():
            self.tree_stock.insert("", "end", values=row)

        # 2. Movimientos del día
        for i in self.tree_mov.get_children():
            self.tree_mov.delete(i)
            
        cursor.execute("""
            SELECT DATE_FORMAT(m.fecha, '%H:%i'), p.nombre, m.tipo, m.cantidad
            FROM movimientos_inventario m
            JOIN productos p ON m.producto_id = p.id
            WHERE DATE(m.fecha) = CURDATE()
            ORDER BY m.fecha DESC
        """)
        
        for row in cursor.fetchall():
            # Determinar el tipo de movimiento para mostrarlo en mayúsculas
            tipo = "ENTRADA" if row[2] == "entrada" else "SALIDA"
            self.tree_mov.insert("", "end", values=(row[0], row[1], tipo, row[3]))

        conn.close()