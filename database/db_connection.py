# Conexión a MySQL

# database/db_connection.py
import mysql.connector # Módulo para conectar Python con MySQL.
from tkinter import messagebox

def conectar():
    """Conecta a la base de datos MySQL"""
    try:
        conn = mysql.connector.connect(
            host="localhost",       # Dirección del servidor de BD.
            user="root",            # Usuario de la BD.
            password="",            # Contraseña del usuario.
            database="minimarket_fullstack_b" # Nombre de la BD a usar.
        )
        return conn                 # Devuelve el objeto de conexión si es exitoso.
    except mysql.connector.Error as e: # Captura errores específicos de MySQL.
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return None                 # Devuelve None si falla la conexión.