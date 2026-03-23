import sqlite3
import hashlib
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger(__name__)

# Obtener ruta de la base de datos unificada
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "gamestock.db")

def conectar():
    """Conecta a la base de datos unificada"""
    # Crear carpeta data si no existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Crear tabla de usuarios si no existe
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
    
    conexion.commit()
    conexion.close()
    logger.info(f"Base de datos de autenticación lista: {DB_PATH}")

def encriptar_password(password):
    """Encripta la contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_usuario(usuario, password, nombre_completo="", rol="usuario"):
    """Registra un nuevo usuario en la base de datos"""
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        
        password_encriptada = encriptar_password(password)
        
        cursor.execute("""
            INSERT INTO usuarios (usuario, password, nombre_completo, rol)
            VALUES (?, ?, ?, ?)
        """, (usuario, password_encriptada, nombre_completo, rol))
        
        usuario_id = cursor.lastrowid
        
        conexion.commit()
        conexion.close()
        
        logger.info(f"Usuario registrado: {usuario} (ID: {usuario_id})")
        return True, f"Usuario registrado exitosamente (ID: {usuario_id})"
    except sqlite3.IntegrityError:
        logger.warning(f"Intento de registro con usuario duplicado: {usuario}")
        return False, "El usuario ya existe"
    except Exception as e:
        logger.error(f"Error al registrar usuario: {e}")
        return False, f"Error al registrar: {str(e)}"

def verificar_login(usuario, password):
    """Verifica las credenciales del usuario"""
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        
        password_encriptada = encriptar_password(password)
        
        cursor.execute("""
            SELECT id, nombre_completo, rol, activo FROM usuarios
            WHERE usuario = ? AND password = ?
        """, (usuario, password_encriptada))
        
        resultado = cursor.fetchone()
        conexion.close()
        
        if resultado:
            if resultado[3] == 0:  # Usuario inactivo
                logger.warning(f"Intento de login con usuario inactivo: {usuario}")
                return False, "Usuario desactivado"
            
            logger.info(f"Login exitoso: {usuario}")
            return True, {
                'id': resultado[0],
                'usuario': usuario,
                'nombre_completo': resultado[1],
                'rol': resultado[2]
            }
        else:
            logger.warning(f"Login fallido: {usuario}")
            return False, "Usuario o contraseña incorrectos"
    except Exception as e:
        logger.error(f"Error al verificar login: {e}")
        return False, f"Error al verificar login: {str(e)}"

def obtener_total_usuarios():
    """Obtiene el total de usuarios registrados"""
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
        total = cursor.fetchone()[0]
        conexion.close()
        return total
    except:
        return 0

def obtener_usuarios():
    """Obtiene lista de todos los usuarios"""
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, usuario, nombre_completo, rol, fecha_registro, activo
            FROM usuarios
            ORDER BY fecha_registro DESC
        """)
        usuarios = cursor.fetchall()
        conexion.close()
        return usuarios
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {e}")
        return []

def cambiar_rol_usuario(usuario_id, nuevo_rol):
    """Cambia el rol de un usuario"""
    try:
        if nuevo_rol not in ['admin', 'usuario']:
            return False, "Rol inválido"
        
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE usuarios SET rol = ? WHERE id = ?
        """, (nuevo_rol, usuario_id))
        conexion.commit()
        conexion.close()
        
        logger.info(f"Rol actualizado para usuario ID {usuario_id}: {nuevo_rol}")
        return True, "Rol actualizado exitosamente"
    except Exception as e:
        logger.error(f"Error al cambiar rol: {e}")
        return False, f"Error: {str(e)}"

def desactivar_usuario(usuario_id):
    """Desactiva un usuario (no lo elimina)"""
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))
        conexion.commit()
        conexion.close()
        
        logger.info(f"Usuario desactivado: ID {usuario_id}")
        return True, "Usuario desactivado"
    except Exception as e:
        logger.error(f"Error al desactivar usuario: {e}")
        return False, f"Error: {str(e)}"

# Inicializar base de datos al importar
conectar()
