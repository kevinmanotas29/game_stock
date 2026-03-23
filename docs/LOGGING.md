# Sistema de Logging de GameStock

## Descripción

GameStock ahora cuenta con un sistema de logging completo que registra **todas las acciones** que ocurren en la aplicación, incluyendo:

- Inicio y cierre de la aplicación
- Login de usuarios
- Operaciones de base de datos (agregar, actualizar, eliminar productos)
- Mensajes enviados y recibidos de Gemini AI
- Errores y excepciones
- Inicialización de componentes
- Estados de conexión

## Ubicación de los logs

Los archivos de log se guardan en:
```
Game_stock/logs/gamestock_YYYYMMDD.log
```

Ejemplo: `logs/gamestock_20260304.log`

Se crea un archivo nuevo cada día automáticamente.

## Cómo usar el sistema de logging

### Opción 1: Ver logs en tiempo real

Abre una terminal y ejecuta:

```bash
cd /Users/kevinmanotas/Desktop/Game_stock
python ver_logs.py
```

Esto mostrará los logs **en tiempo real** mientras usas la aplicación. Perfecto para debugging.

### Opción 2: Ver historial completo

Para ver todo el historial de logs de hoy:

```bash
cd /Users/kevinmanotas/Desktop/Game_stock
python ver_historial_logs.py
```

### Opción 3: Ver logs directamente

También puedes abrir el archivo directamente:

```bash
cd /Users/kevinmanotas/Desktop/Game_stock
cat logs/gamestock_$(date +%Y%m%d).log
```

O con `tail` para seguir en tiempo real:

```bash
tail -f logs/gamestock_$(date +%Y%m%d).log
```

## Formato de los logs

Cada línea de log sigue este formato:

```
FECHA HORA | NIVEL    | MÓDULO              | MENSAJE
2026-03-04 10:30:15 | INFO     | main                | Iniciando GameStock...
2026-03-04 10:30:16 | INFO     | gui.interfaz        | Inicializando interfaz principal...
2026-03-04 10:30:17 | INFO     | chat.gemini_chat    | Gemini AI inicializado correctamente
2026-03-04 10:30:20 | INFO     | gui.interfaz        | Usuario envía mensaje: hola
2026-03-04 10:30:22 | INFO     | chat.gemini_chat    | Respuesta recibida de Gemini (150 caracteres)
```

### Niveles de log:

- **DEBUG**: Información muy detallada (desarrollo)
- **INFO**: Información general de operaciones normales
- **WARNING**: Advertencias que no son errores pero requieren atención
- **ERROR**: Errores que impiden una operación específica
- **CRITICAL**: Errores críticos que pueden detener la aplicación

## Qué se registra

### Módulo `main.py`
- Inicio y cierre de la aplicación
- Login exitoso o cancelado
- Carga de la interfaz principal

### Módulo `gui/interfaz.py`
- Inicialización de la interfaz
- Conexión a base de datos
- Mensajes enviados al chat
- Respuestas recibidas de Gemini
- Operaciones CRUD (crear, leer, actualizar, eliminar productos)

### Módulo `database/db.py`
- Conexiones a la base de datos
- Operaciones de productos (agregar, actualizar, eliminar)
- Consultas SQL

### Módulo `chat/gemini_chat.py`
- Inicialización del cliente de Gemini
- Mensajes enviados a la IA
- Respuestas recibidas
- Detección de acciones (agregar, eliminar, actualizar productos)
- Errores de API

## Ejemplos de uso

### Ejemplo 1: Debugging de errores

Si la aplicación falla, revisa los logs para ver exactamente dónde ocurrió el error:

```bash
python ver_historial_logs.py | grep ERROR
```

### Ejemplo 2: Ver solo mensajes de Gemini

```bash
python ver_historial_logs.py | grep "gemini_chat"
```

### Ejemplo 3: Ver operaciones de base de datos

```bash
python ver_historial_logs.py | grep "database.db"
```

### Ejemplo 4: Seguir logs mientras pruebas

Terminal 1 (logs en tiempo real):
```bash
python ver_logs.py
```

Terminal 2 (ejecutar aplicación):
```bash
python main.py
```

## Configuración avanzada

Si quieres modificar el nivel de logging, edita `utils/logger.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a INFO, WARNING, ERROR según necesidad
    ...
)
```

## Notas

- Los logs se guardan tanto en archivo como en consola
- Los archivos de log incluyen encoding UTF-8 para soportar emojis
- Un nuevo archivo se crea cada día automáticamente
- Los logs antiguos no se borran automáticamente (debes limpiarlos manualmente si lo deseas)

## Beneficios del sistema de logging

1. **Debugging más fácil**: Ve exactamente qué está pasando en cada momento
2. **Trazabilidad**: Sigue el flujo completo de una operación
3. **Monitoreo**: Detecta problemas antes de que afecten al usuario
4. **Auditoría**: Registro de todas las operaciones realizadas
5. **Desarrollo**: Entiende mejor cómo funciona tu aplicación
