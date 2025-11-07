# Minimarket FullStack B 🛒

**Una aplicación de gestión de inventario para minimarkets, desarrollada en Python con una interfaz gráfica Tkinter y persistencia de datos en MySQL.**

assets/login.png

---

## 💻 Descripción del Proyecto

Esta es una aplicación de escritorio diseñada para centralizar la gestión de productos, usuarios, proveedores y movimientos de stock en un minimarket.

_Funcionalidades Clave:_

* **Login con Roles:** Permite el acceso diferenciado para `admin` y `empleado`. 
* **Gestión de Productos (CRUD):** Creación, Lectura, Actualización y Eliminación de ítems en el inventario. 
* **Gestión de Proveedores y Categorías:** Relaciona los productos con sus fuentes de suministro y clasificación.
* **Registro de Movimientos:** Controla las entradas y salidas de stock por parte de los usuarios. 
* **Base de Datos Relacional:** Utiliza MySQL para asegurar la integridad de los datos mediante Claves Foráneas y restricciones. 

## 🚀 Tecnologías Utilizadas

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Lógica de Negocio** | Python 3.11+ | Orquestación, validación y construcción de consultas.  |
| **Interfaz Gráfica (GUI)** | Tkinter | Librería estándar de Python para el Front-end.  |
| **Base de Datos (SGBD)** | MySQL | Motor de almacenamiento estructurado de datos. |
| **Conector DB** | `mysql-connector-python` | Puente de comunicación entre Python y MySQL. |

---

## 📂 Estructura del Proyecto
MINIMARKET_FULLSTACK_B_APP/ 
├── assets/ (Imágenes, iconos, etc.) 
├── database/ (Scripts SQL) 
├── modules/ (Módulos de la app) 
│ ├── login.py 
│ ├── menu.py 
│ ├── movimientos.py 
│ ├── productos.py 
│ └── reportes.py 
├── db_connection.py (Módulo de conexión a MySQL) 
└── main.py (Punto de entrada de la aplicación) 
└── README.md

---

## ⚙️ Instalación y Configuración

### Requisitos Previos 

Asegúrate de tener instalado lo siguiente:

1.  **Python 3.11+** 
2.  **MySQL Server** (Se recomienda usar XAMPP o MySQL Server standalone). 
3.  **MySQL Workbench** (Opcional, para gestión visual de la DB).

### Pasos de Instalación [cite: 93]

1.  **Clonar o descargar el proyecto.** 
2.  **Instalar el conector de MySQL:**
    ```bash
    pip install mysql-connector-python
    ```
3.  **Crear la Base de Datos:**
    * Abre MySQL Workbench.
    * Ejecuta la siguiente sentencia para crear el esquema:
        ```sql
        CREATE DATABASE Minimarket_FullStack_B; 
        ```

### Configuración Inicial de la DB 

Ejecuta el siguiente script en MySQL Workbench para crear la tabla de usuarios e insertar credenciales de prueba: 

```sql
CREATE DATABASE IF NOT EXISTS Minimarket_FullStack_B;
USE Minimarket_FullStack_B;

CREATE TABLE categorias(
	id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50),
    descripcion TEXT
)ENGINE = InnoDB;

CREATE TABLE proveedores (
	id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    ubicacion VARCHAR(80),
    contacto VARCHAR(50)
)ENGINE = InnoDB;

CREATE TABLE usuarios (
	id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50),
    email VARCHAR(100) NOT NULL UNIQUE,
    rol ENUM('admin', 'empleado') DEFAULT 'empleado' 
)ENGINE = InnoDB;

CREATE TABLE productos (
	id_productos INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL, 
    id_categoria INT,
    id_proveedor INT,
	FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL, 
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT
)ENGINE = InnoDB;

CREATE TABLE movimientos_inventario (
	id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT,
    tipo ENUM('Entrada', 'Salida') NOT NULL, 
    cantidad INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP, 
    id_usuario INT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_productos) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE SET NULL
)ENGINE = InnoDB;
```

## ▶️ Cómo Ejecutar

1.  Abre la terminal en la carpeta raíz del proyecto. 
2.  Ejecuta el archivo principal:
    ```bash
    python main.py 
    ```
3.  La ventana de **Login** aparecerá. Utiliza estas credenciales de prueba para el primer acceso (el script de configuración de DB ya las incluye):
    * **Email (Admin):** `agus@minimarket.com` 
    * **Rol:** `admin`

## 📸 Capturas de Pantalla


| Login | Menú Principal | Gestión de Productos |
| :---: | :---: | :---: |
| ! (assets/login.png) | ! (assets/menu.png) | ! (assets/productos.png) |

---

## 👥 Autor

* Mignani Agustina
* Proyecto Integrador Bases de Datos II - Diseños y Arquitectura de Despliegue 1 
* Universidad Provincial de Córdoba (UPC) 
* Año Lectivo: 2025 