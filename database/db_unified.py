import sqlite3
import os
import sys

# Agregar el directorio raíz al path para poder importar utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "gamestock.db")

logger.info(f"Base de datos unificada: {DB_PATH}")

def conectar():
    """Crea la estructura completa de la base de datos unificada"""
    logger.info("Conectando a base de datos unificada...")
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # TABLA: usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_completo TEXT,
            rol TEXT DEFAULT 'usuario' CHECK(rol IN ('admin', 'usuario')),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo INTEGER DEFAULT 1
        )
    """)
    
    # TABLA: categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # TABLA: productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL CHECK(cantidad >= 0),
            precio REAL NOT NULL CHECK(precio >= 0),
            categoria_id INTEGER,
            usuario_creador_id INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
            FOREIGN KEY (usuario_creador_id) REFERENCES usuarios(id) ON DELETE SET NULL
        )
    """)
    
    # TABLA: historial_cambios (auditoría)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_cambios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            producto_id INTEGER,
            accion TEXT NOT NULL CHECK(accion IN ('CREAR', 'ACTUALIZAR', 'ELIMINAR')),
            detalle TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
        )
    """)
    
    # Crear índices para mejor rendimiento
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuario ON usuarios(usuario)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_producto_nombre ON productos(nombre)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_producto_categoria ON productos(categoria_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_historial_usuario ON historial_cambios(usuario_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_historial_producto ON historial_cambios(producto_id)")
    
    # Insertar categorías por defecto si no existen
    categorias_default = [
        ('Celulares', 'Dispositivos móviles y smartphones'),
        ('Computadores', 'Computadores portátiles y de escritorio'),
        ('Consolas', 'Consolas de videojuegos'),
        ('Gaming', 'Equipos y accesorios para videojuegos'),
        ('Perifericos', 'Dispositivos de entrada y salida'),
        ('Audio', 'Equipos de sonido y audifonos'),
        ('Wearables', 'Dispositivos tecnologicos portables')
    ]
    
    for nombre, descripcion in categorias_default:
        cursor.execute("""
            INSERT OR IGNORE INTO categorias (nombre, descripcion)
            VALUES (?, ?)
        """, (nombre, descripcion))
    
    conexion.commit()
    conexion.close()
    logger.info("Base de datos unificada lista con relaciones FK")


def agregar_producto(nombre, cantidad, precio, categoria_id=None, usuario_id=None):
    """Agrega un nuevo producto con categoría y usuario creador"""
    logger.info(f"Agregando producto: {nombre} (cantidad: {cantidad}, precio: {precio}, categoria: {categoria_id})")
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.execute("""
        INSERT INTO productos (nombre, cantidad, precio, categoria_id, usuario_creador_id)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, cantidad, precio, categoria_id, usuario_id))
    
    producto_id = cursor.lastrowid
    
    # Registrar en historial
    if usuario_id:
        cursor.execute("""
            INSERT INTO historial_cambios (usuario_id, producto_id, accion, detalle)
            VALUES (?, ?, 'CREAR', ?)
        """, (usuario_id, producto_id, f"Creado producto: {nombre}"))
    
    conexion.commit()
    conexion.close()
    logger.info(f"Producto agregado: {nombre} (ID: {producto_id})")
    return producto_id


def obtener_productos():
    """Obtiene todos los productos con información de categoría"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT 
            p.id,
            p.nombre,
            p.cantidad,
            p.precio,
            c.nombre as categoria,
            p.fecha_creacion
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY p.fecha_creacion DESC
    """)
    
    productos = cursor.fetchall()
    conexion.close()
    return productos


def obtener_productos_por_categoria(categoria_id):
    """Obtiene productos filtrados por categoría"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre, cantidad, precio
        FROM productos
        WHERE categoria_id = ?
        ORDER BY nombre
    """, (categoria_id,))
    
    productos = cursor.fetchall()
    conexion.close()
    return productos


def eliminar_producto(id_producto, usuario_id=None):
    """Elimina un producto y registra en historial"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Obtener nombre del producto antes de eliminar
    cursor.execute("SELECT nombre FROM productos WHERE id = ?", (id_producto,))
    resultado = cursor.fetchone()
    nombre_producto = resultado[0] if resultado else "Desconocido"
    
    # Registrar en historial antes de eliminar
    if usuario_id:
        cursor.execute("""
            INSERT INTO historial_cambios (usuario_id, producto_id, accion, detalle)
            VALUES (?, ?, 'ELIMINAR', ?)
        """, (usuario_id, id_producto, f"Eliminado producto: {nombre_producto}"))
    
    # Eliminar producto
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    
    conexion.commit()
    conexion.close()
    logger.info(f"Producto eliminado: {nombre_producto} (ID: {id_producto})")


def actualizar_producto(id_producto, nombre, cantidad, precio, categoria_id=None, usuario_id=None):
    """Actualiza un producto y registra en historial"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.execute("""
        UPDATE productos
        SET nombre=?, cantidad=?, precio=?, categoria_id=?, fecha_actualizacion=CURRENT_TIMESTAMP
        WHERE id=?
    """, (nombre, cantidad, precio, categoria_id, id_producto))
    
    # Registrar en historial
    if usuario_id:
        cursor.execute("""
            INSERT INTO historial_cambios (usuario_id, producto_id, accion, detalle)
            VALUES (?, ?, 'ACTUALIZAR', ?)
        """, (usuario_id, id_producto, f"Actualizado producto: {nombre} - Cantidad: {cantidad}, Precio: {precio}"))
    
    conexion.commit()
    conexion.close()
    logger.info(f"Producto actualizado: {nombre} (ID: {id_producto})")


def obtener_categorias():
    """Obtiene todas las categorías disponibles"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
    categorias = cursor.fetchall()
    
    conexion.close()
    return categorias


def obtener_historial(usuario_id=None, producto_id=None, limit=50):
    """Obtiene el historial de cambios"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    query = """
        SELECT 
            h.id,
            u.usuario,
            u.nombre_completo,
            h.accion,
            h.detalle,
            h.fecha
        FROM historial_cambios h
        JOIN usuarios u ON h.usuario_id = u.id
        WHERE 1=1
    """
    params = []
    
    if usuario_id:
        query += " AND h.usuario_id = ?"
        params.append(usuario_id)
    
    if producto_id:
        query += " AND h.producto_id = ?"
        params.append(producto_id)
    
    query += " ORDER BY h.fecha DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    historial = cursor.fetchall()
    
    conexion.close()
    return historial


def obtener_estadisticas():
    """Obtiene estadísticas del inventario"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    stats = {}
    
    # Total de productos
    cursor.execute("SELECT COUNT(*) FROM productos")
    stats['total_productos'] = cursor.fetchone()[0]
    
    # Valor total del inventario
    cursor.execute("SELECT SUM(cantidad * precio) FROM productos")
    stats['valor_total'] = cursor.fetchone()[0] or 0
    
    # Productos por categoría
    cursor.execute("""
        SELECT c.nombre, COUNT(p.id) as total
        FROM categorias c
        LEFT JOIN productos p ON c.id = p.categoria_id
        GROUP BY c.id, c.nombre
        ORDER BY total DESC
    """)
    stats['por_categoria'] = cursor.fetchall()
    
    # Productos con bajo stock (menos de 5)
    cursor.execute("SELECT COUNT(*) FROM productos WHERE cantidad < 5")
    stats['bajo_stock'] = cursor.fetchone()[0]
    
    conexion.close()
    return stats



# Inicializar la base de datos al importar el módulo
conectar()

