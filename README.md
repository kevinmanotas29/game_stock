# GameStock - Sistema de Inventario con IA

Aplicación de escritorio moderna desarrollada en Python con CustomTkinter, SQLite y Google Gemini AI.  
Gestiona inventarios de productos tecnológicos (celulares, computadores, consolas, gaming, periféricos, audio, wearables) con CRUD completo, categorías, chat inteligente integrado y sistema de auditoría avanzado.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Características Principales

### Sistema de Autenticación
- Login y registro de usuarios
- Contraseñas encriptadas con SHA-256
- Sesiones de usuario persistentes
- Botón de cerrar sesión con limpieza de callbacks

### Interfaz Moderna
- Diseño oscuro profesional con CustomTkinter
- Componentes visuales pulidos y responsivos
- Tabla de productos con formato COP
- Chat IA integrado con burbujas estilo WhatsApp
- Animaciones suaves y transiciones

### Gestión de Inventario
- Agregar productos con categorías
- Categorías: Celulares, Computadores, Consolas, Gaming, Periféricos, Audio, Wearables
- Listar productos en tabla dinámica
- Actualizar productos (seleccionar de tabla)
- Eliminar productos
- Validación de datos en tiempo real
- Formato de moneda colombiana (COP)
- Base de datos unificada con relaciones FK

### Chat con IA (Gemini 2.5 Flash)
- Consultar inventario en lenguaje natural
- Agregar productos mediante lenguaje natural ("Agrega 10 iPhone 15 a 4 millones")
- Extracción inteligente de datos (nombre, cantidad, precio)
- Actualizar productos con texto natural
- Eliminar productos por ID o nombre
- Calcular valor total del inventario
- Consultar por categorías
- Respuestas inteligentes contextuales en español
- Detección automática de acciones
- Manejo inteligente de errores de cuota

### Sistema de Logging Avanzado
- Registro completo de todas las operaciones
- Logs estructurados por módulo y nivel
- Archivo de logs diario automático
- Scripts para visualización en tiempo real
- Debugging facilitado con trazabilidad completa

### Base de Datos Unificada
- **gamestock.db**: Una sola base de datos SQLite con relaciones FK
- **4 Tablas principales**:
  - `usuarios`: Autenticación y perfiles de usuario
  - `categorias`: 7 categorías de productos tecnológicos
  - `productos`: Inventario con relación a categorías y usuarios
  - `historial_cambios`: Auditoría completa de todas las operaciones CRUD
- **Categorías disponibles**:
  - Celulares
  - Computadores
  - Consolas
  - Gaming
  - Periféricos
  - Audio
  - Wearables
- Ver documentación completa en `docs/MER.md`

---

## Estructura del Proyecto

```
Game_stock/
│
├── main.py                    # Punto de entrada principal
│
├── gui/
│   ├── login.py               # Ventana de login y registro
│   └── interfaz.py            # Interfaz principal con CustomTkinter
│
├── database/
│   ├── auth_unified.py        # Autenticación de usuarios
│   └── db_unified.py          # Operaciones CRUD con SQLite (productos, categorías, historial)
│
├── chat/
│   ├── __init__.py
│   └── gemini_chat.py         # Integración con Google Gemini API
│
├── utils/
│   ├── __init__.py
│   └── logger.py              # Sistema de logging centralizado
│
├── data/
│   └── gamestock.db           # Base de datos unificada (usuarios, productos, categorías, historial)
│
├── logs/
│   └── gamestock_YYYYMMDD.log # Logs diarios automáticos
│
├── docs/
│   ├── MER.md                 # Documentación del modelo ER
│   ├── LOGGING.md             # Documentación del sistema de logging
│   └── GEMINI_LIMITS.md       # Información sobre límites de API
│
├── .env                       # API key de Google (NO SUBIR A GIT)
├── .gitignore                 # Archivos ignorados
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Este archivo
```

---

## Instalación

### 1. Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Conexión a Internet

### 2. Clonar o Descargar el Proyecto
```bash
git clone <tu-repositorio>
cd Game_stock
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

**Dependencias incluidas:**
- `customtkinter` - Interfaz gráfica moderna
- `google-genai` - API de Google Gemini
- `python-dotenv` - Gestión de variables de entorno

### 4. Configurar la API Key de Google

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Crea una nueva API key (gratuita)
4. Crea un archivo `.env` en la raíz del proyecto
5. Agrega tu API key:


## Cómo Ejecutar

### Ejecutar la Aplicación
```bash
python main.py
```

### Ver Logs en Tiempo Real (Opcional)
Abre una segunda terminal para monitorear logs mientras usas la app:

```bash
python ver_logs.py
```

### Ver Historial de Logs
```bash
python ver_historial_logs.py
```

---

## Usar el Chat con IA

### Ejemplos de Comandos

#### Consultar Inventario
```
"¿Cuántos productos tengo?"
"Muéstrame todos los productos"
"¿Qué productos tengo en stock?"
"¿Cuál es el producto más caro?"
"¿Cuántos celulares tengo?"
```

#### Agregar Productos (Lenguaje Natural)
```
"Agrega 10 iPhone 15 a 4 millones"
"Añade 5 MacBook Pro a 8 millones"
"Agrega PS5 con 15 unidades a 2000000"
"Quiero agregar 20 AirPods Pro, valen 800000"
```

#### Actualizar Productos
```
"Actualiza producto 3: nombre iPhone 14, cantidad 20, precio 3500000"
"Cambia el precio del producto 2 a 45000"
"Actualiza el ID 5 con cantidad 8"
```

#### Eliminar Productos
```
"Elimina el producto con ID 5"
"Borra el producto número 3"
"Elimina iPhone 14"
```

#### Estadísticas
```
"¿Cuál es el valor total del inventario?"
"Calcula el valor total de todos los productos"
```

---

## Tecnologías Utilizadas

| Tecnología | Uso |
|------------|-----|
| **Python 3.8+** | Lenguaje de programación principal |
| **CustomTkinter** | Interfaz gráfica moderna y oscura |
| **SQLite3** | Base de datos relacional embebida |
| **Google Gemini 2.5 Flash** | Inteligencia artificial conversacional |
| **python-dotenv** | Gestión segura de configuración |
| **Threading** | Operaciones asíncronas (IA, animaciones) |

---

## Sistema de Logging

El proyecto incluye un **sistema de logging completo** que registra:

- Inicio y cierre de la aplicación  
- Login y autenticación de usuarios  
- Operaciones CRUD (crear, leer, actualizar, eliminar)  
- Mensajes enviados y recibidos de Gemini  
- Errores y excepciones con stack trace  
- Estados de conexión y inicialización  

### Ver Logs

Los logs se guardan automáticamente en `logs/gamestock_YYYYMMDD.log`

```bash
# Ver logs en tiempo real con tail
tail -f logs/gamestock_$(date +%Y%m%d).log

# Ver los últimos 50 registros
tail -50 logs/gamestock_$(date +%Y%m%d).log
```

---

## Seguridad

- Archivo `.env` en `.gitignore` (no se sube a Git)
- API key cargada desde variables de entorno
- Contraseñas encriptadas con SHA-256
- Sesiones de usuario seguras
- Validación de entrada de datos

---

## Límites de la API de Gemini

### Plan Gratuito (Gemini 2.5 Flash)
- **Límite diario:** 20 solicitudes por día
- **Límite por minuto:** 2 solicitudes por minuto

ADVERTENCIA: Si alcanzas el límite, el sistema te mostrará un mensaje claro con:
- Tiempo de espera hasta que se recupere la cuota
- Sugerencias para usar el formulario manual
- Enlace a documentación oficial

CONSEJO: Usa el formulario manual para operaciones simples y reserva el chat de IA para consultas complejas.

Mas información: Lee [GEMINI_LIMITS.md](docs/GEMINI_LIMITS.md) para detalles completos sobre cuotas y alternativas.

---

## Solución de Problemas

### Error: "No module named 'google.genai'"
```bash
pip install google-genai
```

### Error: "API key not valid"
1. Verifica que tu API key en `.env` sea correcta
2. Asegúrate de que no haya espacios extra
3. Comprueba que el archivo `.env` esté en la raíz del proyecto
4. Formato correcto: `GOOGLE_API_KEY=AIzaSy...`

### El chat muestra "Esperando conexión con Gemini..."
1. Espera unos segundos (la primera conexión toma tiempo)
2. Verifica tu conexión a Internet
3. Revisa los logs: `python ver_historial_logs.py | grep ERROR`

### Error: "429 RESOURCE_EXHAUSTED" / "Quota exceeded"
Has alcanzado el límite de 20 solicitudes diarias. Soluciones:
1. **Espera 24 horas** para que se resetee la cuota
2. **Crea otra API key** en un nuevo proyecto de Google AI Studio
3. **Usa el formulario manual** mientras tanto
4. Lee [GEMINI_LIMITS.md](GEMINI_LIMITS.md) para más opciones

### Errores de callbacks de Tkinter
Los errores tipo `invalid command name` han sido solucionados con:
- Cancelación automática de callbacks al cerrar ventanas
- Verificación de existencia de widgets antes de operaciones
- Manejo correcto de variables globales

### Ver logs detallados de errores
```bash
python ver_historial_logs.py | grep -A 5 ERROR
```

---

## Documentación Adicional

- [LOGGING.md](docs/LOGGING.md) - Sistema de logging completo
- [GEMINI_LIMITS.md](docs/GEMINI_LIMITS.md) - Límites de API y soluciones
- [MER.md](docs/MER.md) - Modelo Entidad-Relación de las bases de datos

---

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---


---

## Roadmap Futuro

- [ ] Exportar inventario a Excel/CSV
- [ ] Gráficos de estadísticas
- [ ] Modo claro/oscuro toggle
- [ ] Soporte para imágenes de productos
- [ ] Historial de cambios de inventario
- [ ] Respaldo automático de base de datos
- [ ] Notificaciones de stock bajo
- [ ] Multi-idioma (inglés/español)

---

---

<div align="center">

**Si te gusta este proyecto, dale una estrella!**

</div>
