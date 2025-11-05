# Conexión a MySQL

# database/db_connection.py

import mysql.connector
from tkinter import messagebox

def conectar():
    """Conecta a la base de datos MySQL"""
    try: 
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="minimarket_fullstack_b"
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return None