from google import genai
import os
import sys
from dotenv import load_dotenv  # noqa: F401
from database import db_unified as db

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

# Mapeo de nombres de funciones a las funciones reales (declarado primero)
available_functions = {}

# Configurar cliente de Gemini con la nueva API
def get_gemini_client():
    """Obtiene o crea el cliente de Gemini de forma lazy"""
    logger.info("Creando cliente de Gemini...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("✗ No se encontró GOOGLE_API_KEY en .env")
        raise ValueError("No se encontró GOOGLE_API_KEY en el archivo .env")
    logger.info("API key encontrada, creando cliente...")
    return genai.Client(api_key=api_key)

# Funciones que el modelo puede llamar
def obtener_productos_chat():
    """Obtiene todos los productos del inventario"""
    productos = db.obtener_productos()
    if not productos:
        return "No hay productos en el inventario."
    
    resultado = "Productos en inventario:\n\n"
    for p in productos:
        resultado += f"- ID: {p[0]} | {p[1]} | Stock: {p[2]} unidades | Precio: ${p[3]}\n"
    return resultado

def agregar_producto_chat(nombre: str, cantidad: int, precio: float):
    """Agrega un nuevo producto al inventario"""
    try:
        db.agregar_producto(nombre, cantidad, precio)
        return f"✓ Producto '{nombre}' agregado exitosamente: {cantidad} unidades a ${precio} cada una."
    except Exception as e:
        return f"✗ Error al agregar producto: {str(e)}"

def actualizar_producto_chat(id_producto: int, nombre: str, cantidad: int, precio: float):
    """Actualiza un producto existente"""
    try:
        db.actualizar_producto(id_producto, nombre, cantidad, precio)
        return f"✓ Producto ID {id_producto} actualizado: {nombre}, {cantidad} unidades, ${precio}"
    except Exception as e:
        return f"✗ Error al actualizar producto: {str(e)}"

def eliminar_producto_chat(id_producto: int):
    """Elimina un producto del inventario"""
    try:
        db.eliminar_producto(id_producto)
        return f"✓ Producto ID {id_producto} eliminado del inventario."
    except Exception as e:
        return f"✗ Error al eliminar producto: {str(e)}"

def calcular_valor_total():
    """Calcula el valor total del inventario"""
    productos = db.obtener_productos()
    if not productos:
        return "El inventario está vacío. Valor total: $0"
    
    total = sum(p[2] * p[3] for p in productos)
    return f"Valor total del inventario: ${total:,.2f}"

# Declaraciones de funciones para Gemini
tools = [
    {
        "function_declarations": [
            {
                "name": "obtener_productos_chat",
                "description": "Obtiene la lista completa de productos del inventario con sus detalles (ID, nombre, cantidad, precio)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                }
            },
            {
                "name": "agregar_producto_chat",
                "description": "Agrega un nuevo producto al inventario",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre": {
                            "type": "string",
                            "description": "Nombre del producto a agregar"
                        },
                        "cantidad": {
                            "type": "integer",
                            "description": "Cantidad en stock del producto"
                        },
                        "precio": {
                            "type": "number",
                            "description": "Precio unitario del producto"
                        }
                    },
                    "required": ["nombre", "cantidad", "precio"]
                }
            },
            {
                "name": "actualizar_producto_chat",
                "description": "Actualiza un producto existente en el inventario",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id_producto": {
                            "type": "integer",
                            "description": "ID del producto a actualizar"
                        },
                        "nombre": {
                            "type": "string",
                            "description": "Nuevo nombre del producto"
                        },
                        "cantidad": {
                            "type": "integer",
                            "description": "Nueva cantidad en stock"
                        },
                        "precio": {
                            "type": "number",
                            "description": "Nuevo precio unitario"
                        }
                    },
                    "required": ["id_producto", "nombre", "cantidad", "precio"]
                }
            },
            {
                "name": "eliminar_producto_chat",
                "description": "Elimina un producto del inventario por su ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id_producto": {
                            "type": "integer",
                            "description": "ID del producto a eliminar"
                        }
                    },
                    "required": ["id_producto"]
                }
            },
            {
                "name": "calcular_valor_total",
                "description": "Calcula el valor monetario total del inventario (suma de cantidad × precio de todos los productos)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                }
            }
        ]
    }
]

# Mapeo de nombres de funciones a las funciones reales
available_functions = {
    "obtener_productos_chat": obtener_productos_chat,
    "agregar_producto_chat": agregar_producto_chat,
    "actualizar_producto_chat": actualizar_producto_chat,
    "eliminar_producto_chat": eliminar_producto_chat,
    "calcular_valor_total": calcular_valor_total,
}

class GeminiChat:
    def __init__(self):
        logger.info("Inicializando GeminiChat...")
        # Usar Gemini 2.5 Flash con la nueva API
        self.model_name = 'gemini-2.5-flash'
        self.chat_history = []
        self.client = None  # Inicializar en None
        logger.info(f"GeminiChat creado con modelo {self.model_name} (cliente lazy loading)")
        
    def _get_client(self):
        """Obtiene el cliente de Gemini de forma lazy (solo cuando se necesita)"""
        if self.client is None:
            logger.info("Primera llamada a Gemini, creando cliente...")
            self.client = get_gemini_client()
            logger.info("Cliente de Gemini creado")
        return self.client
        
    def send_message(self, message):
        """Envía un mensaje al modelo y obtiene la respuesta"""
        logger.info(f"Mensaje recibido: '{message[:100]}{'...' if len(message) > 100 else ''}'")
        try:
            # Primero, intentar detectar y ejecutar acciones
            mensaje_lower = message.lower()
            
            # ELIMINAR PRODUCTO
            if any(palabra in mensaje_lower for palabra in ['eliminar', 'elimina', 'borra', 'borrar', 'quitar']):
                logger.info("Detectada acción: ELIMINAR producto")
                # Buscar ID del producto
                import re
                match_id = re.search(r'\bid[:\s]*(\d+)', mensaje_lower) or re.search(r'\b(\d+)\b', mensaje_lower)
                
                if match_id:
                    id_producto = int(match_id.group(1))
                    try:
                        eliminar_producto_chat(id_producto)
                        return f"✓ Producto con ID {id_producto} eliminado exitosamente del inventario."
                    except Exception as e:
                        return f"✗ Error al eliminar producto: {str(e)}"
                else:
                    # Buscar por nombre
                    productos = db.obtener_productos()
                    for p in productos:
                        if p[1].lower() in mensaje_lower:
                            try:
                                eliminar_producto_chat(p[0])
                                return f"✓ Producto '{p[1]}' (ID: {p[0]}) eliminado exitosamente."
                            except Exception as e:
                                return f"✗ Error al eliminar producto: {str(e)}"
                    return "Para eliminar un producto, especifica el ID o el nombre exacto. Ejemplo: 'Elimina el producto con ID 5' o 'Elimina Celular'"
            
            # AGREGAR PRODUCTO - Usar Gemini para entender lenguaje natural
            if any(palabra in mensaje_lower for palabra in ['agregar', 'agrega', 'añadir', 'añade', 'crear', 'nuevo']):
                logger.info("Detectada acción: AGREGAR producto")
                
                # Usar Gemini para extraer los datos del mensaje natural
                prompt_extraccion = f"""Analiza este mensaje y extrae la información del producto que el usuario quiere agregar al inventario:

"{message}"

IMPORTANTE: Responde SOLO con este formato JSON exacto (sin comentarios ni texto adicional):
{{"nombre": "nombre del producto", "cantidad": numero, "precio": numero}}

Reglas:
- nombre: El nombre del producto tecnológico
- cantidad: Un número entero (cuántas unidades)
- precio: Un número (precio en pesos colombianos, sin puntos ni comas)
- Si mencionan "mil" o "k", convertir a número (ej: "50 mil" = 50000)
- Si falta algún dato, usa null

Ejemplo mensaje: "Agrega 10 iPhone 15 a 4 millones"
Respuesta: {{"nombre": "iPhone 15", "cantidad": 10, "precio": 4000000}}"""

                try:
                    # Llamar a Gemini para extraer los datos
                    respuesta_gemini = self._get_client().models.generate_content(
                        model=self.model_name,
                        contents=prompt_extraccion
                    )
                    
                    # Limpiar la respuesta y parsear JSON
                    import json
                    respuesta_texto = respuesta_gemini.text.strip()
                    
                    # Quitar markdown si existe
                    if '```' in respuesta_texto:
                        respuesta_texto = respuesta_texto.split('```')[1]
                        if respuesta_texto.startswith('json'):
                            respuesta_texto = respuesta_texto[4:]
                    
                    datos = json.loads(respuesta_texto.strip())
                    
                    nombre = datos.get('nombre')
                    cantidad = datos.get('cantidad')
                    precio = datos.get('precio')
                    
                    # Validar que tengamos todos los datos
                    if nombre and cantidad is not None and precio is not None:
                        # Agregar el producto
                        agregar_producto_chat(nombre, int(cantidad), float(precio))
                        return f"✓ Producto '{nombre}' agregado exitosamente:\n   • Cantidad: {cantidad} unidades\n   • Precio: ${precio:,.0f} COP"
                    else:
                        # Preguntar qué falta
                        faltantes = []
                        if not nombre: faltantes.append("nombre del producto")
                        if cantidad is None: faltantes.append("cantidad")
                        if precio is None: faltantes.append("precio")
                        
                        return f"⚠️ Me falta información para agregar el producto:\n   • {', '.join(faltantes)}\n\nEjemplo: 'Agrega 10 iPhone 15 a 4000000'"
                        
                except json.JSONDecodeError:
                    logger.error(f"Error al parsear JSON de Gemini: {respuesta_gemini.text}")
                    return "⚠️ No pude entender el formato. Intenta algo como: 'Agrega 10 iPhone 15 a 4000000'"
                except Exception as e:
                    logger.error(f"Error al procesar con Gemini: {e}")
                    return f"⚠️ Error al procesar: {str(e)}"
            
            # ACTUALIZAR PRODUCTO
            if any(palabra in mensaje_lower for palabra in ['actualizar', 'actualiza', 'modificar', 'modifica', 'cambiar', 'cambia', 'editar']):
                import re
                
                # Buscar ID del producto
                match_id = re.search(r'\bid[:\s]*(\d+)', mensaje_lower) or re.search(r'producto[:\s]*(\d+)', mensaje_lower)
                
                if match_id:
                    id_producto = int(match_id.group(1))
                    
                    # Extraer nuevos valores
                    cantidad_match = re.search(r'(?:cantidad|stock)[\s:]*(\d+)', mensaje_lower)
                    precio_match = re.search(r'(?:precio)[\s:]*\$?\s*(\d+(?:\.\d+)?)', mensaje_lower) or \
                                  re.search(r'\$\s*(\d+(?:\.\d+)?)', mensaje_lower)
                    
                    # Buscar nombre (palabras entre comillas o después de "nombre")
                    nombre_match = re.search(r'nombre[\s:]*["\']?([^,"\']+)["\']?', message, re.IGNORECASE)
                    
                    # Obtener producto actual
                    productos = db.obtener_productos()
                    producto_actual = None
                    for p in productos:
                        if p[0] == id_producto:
                            producto_actual = p
                            break
                    
                    if producto_actual:
                        nombre = nombre_match.group(1).strip() if nombre_match else producto_actual[1]
                        cantidad = int(cantidad_match.group(1)) if cantidad_match else producto_actual[2]
                        precio = float(precio_match.group(1)) if precio_match else producto_actual[3]
                        
                        try:
                            actualizar_producto_chat(id_producto, nombre, cantidad, precio)
                            return f"✓ Producto ID {id_producto} actualizado: {nombre}, {cantidad} unidades, ${precio}"
                        except Exception as e:
                            return f"✗ Error al actualizar producto: {str(e)}"
                    else:
                        return f"✗ No se encontró el producto con ID {id_producto}"
                
                return "Para actualizar un producto, especifica el ID y los nuevos valores. Ejemplo: 'Actualiza producto 3: nombre iPhone 14, cantidad 20, precio 3500000'"
            
            # CONSULTAS - Usar Gemini AI
            # Agregar contexto del inventario al mensaje
            productos = db.obtener_productos()
            contexto = f"\nInventario actual:\n"
            for p in productos:
                contexto += f"ID: {p[0]} | {p[1]} | Stock: {p[2]} | Precio: ${p[3]}\n"
            
            mensaje_completo = f"""Eres un asistente para GameStock, un sistema de inventario de productos tecnológicos (celulares, computadores, consolas, gaming, periféricos, audio, wearables).
{contexto}

Usuario pregunta: {message}

Responde en español de forma natural y amigable. Proporciona la información solicitada basándote en el inventario mostrado arriba."""

            response = self._get_client().models.generate_content(
                model=self.model_name,
                contents=mensaje_completo
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error en Gemini: {error_str}")
            
            # Detectar error de cuota excedida
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                import re
                # Intentar extraer el tiempo de espera
                retry_match = re.search(r'retry in (\d+(?:\.\d+)?)', error_str)
                if retry_match:
                    segundos = float(retry_match.group(1))
                    minutos = int(segundos / 60)
                    return f"Has alcanzado el límite de consultas gratuitas de Gemini API.\n\n" \
                           f"Límite: 20 solicitudes por día (plan gratuito)\n" \
                           f"Intenta nuevamente en: {minutos} minutos\n\n" \
                           f"Mientras tanto, puedes:\n" \
                           f"• Agregar productos manualmente con el formulario\n" \
                           f"• Ver el inventario actual en la tabla\n" \
                           f"• Consultar: https://ai.google.dev/gemini-api/docs/rate-limits"
                else:
                    return f" Has alcanzado el límite de consultas gratuitas de Gemini API.\n\n" \
                           f" Límite: 20 solicitudes por día\n" \
                           f" Espera unas horas e intenta nuevamente\n\n" \
                           f" Mientras tanto, usa el formulario manual para gestionar productos."
            
            # Otros errores
            return f" Error al comunicarse con Gemini: {error_str}"
    
    def reset_chat(self):
        """Reinicia la conversación"""
        self.chat_history = []
