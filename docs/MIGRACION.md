# Guía de Migración a Base de Datos Unificada

## Resumen de Cambios

GameStock ahora utiliza una **base de datos unificada** con relaciones FK (Foreign Keys) entre tablas.

### Antes (2 bases de datos separadas):
- `data/usuarios.db` - Autenticación
- `data/inventario.db` - Productos

### Después (1 base de datos unificada):
- `data/gamestock.db` - Todo integrado con relaciones

---

## Nueva Estructura de Base de Datos

### Tablas Principales

1. **usuarios** - Gestión de usuarios
   - Roles: admin / usuario
   - Estado: activo / inactivo

2. **categorias** - Categorías de productos tecnológicos
   - 7 categorías predefinidas (Celulares, Computadores, Consolas, Gaming, Periféricos, Audio, Wearables)

3. **productos** - Inventario de productos
   - FK → categorias
   - FK → usuarios (creador)

4. **historial_cambios** - Auditoría completa
   - FK → usuarios
   - FK → productos
   - Registra: CREAR, ACTUALIZAR, ELIMINAR

### Relaciones

```
usuarios (1) ──┬─→ (N) productos (creador)
               └─→ (N) historial_cambios

categorias (1) ──→ (N) productos

productos (1) ──→ (N) historial_cambios
```

---

## Pasos para Migrar

### Paso 1: Ejecutar el Script de Migración

```bash
cd /Users/kevinmanotas/Desktop/Game_stock
python migrar_db.py
```

Este script:
- ✓ Crea la nueva estructura de base de datos
- ✓ Migra todos los usuarios existentes
- ✓ Migra todos los productos existentes
- ✓ Crea categorías por defecto
- ✓ Crea backups de bases antiguas
- ✓ Verifica la integridad de los datos

### Paso 2: Verificar la Migración

El script mostrará:
- Total de usuarios migrados
- Total de productos migrados
- Estado de foreign keys
- Ubicación de backups

### Paso 3: Actualizar el Código

Necesitas actualizar los imports en los siguientes archivos:

#### main.py
```python
# ANTES
from gui.login import VentanaLogin

# DESPUÉS (sin cambios, pero usa auth_unified internamente)
from gui.login import VentanaLogin
```

#### gui/login.py
```python
# ANTES
from database import auth

# DESPUÉS
from database import auth_unified as auth
```

#### gui/interfaz.py
```python
# ANTES
from database import db as database

# DESPUÉS
from database import db_unified as database
```

#### chat/gemini_chat.py
```python
# ANTES
from database import db

# DESPUÉS
from database import db_unified as db
```

---

## Nuevas Funcionalidades

### 1. Categorías de Productos

```python
# Obtener todas las categorías
categorias = database.obtener_categorias()
# Resultado: [(1, 'Celulares', 'Dispositivos móviles y smartphones'), ...]

# Agregar producto con categoría
database.agregar_producto(
    nombre="iPhone 15",
    cantidad=10,
    precio=4000000,
    categoria_id=1,  # Celulares
    usuario_id=1
)

# Filtrar productos por categoría (si está implementado)
productos = database.obtener_productos_por_categoria(categoria_id=1)
```

### 2. Auditoría / Historial

```python
# Obtener historial completo
historial = database.obtener_historial(limit=50)

# Historial de un usuario específico
historial = database.obtener_historial(usuario_id=1)

# Historial de un producto específico
historial = database.obtener_historial(producto_id=5)
```

### 3. Estadísticas Avanzadas

```python
stats = database.obtener_estadisticas()
# Resultado:
# {
#     'total_productos': 25,
#     'valor_total': 50000000.00,
#     'por_categoria': [('Celulares', 10), ('Computadores', 8), ...],
#     'bajo_stock': 3
# }
```

### 4. Roles de Usuario

```python
# Cambiar rol de usuario
auth.cambiar_rol_usuario(usuario_id=2, nuevo_rol='admin')

# Desactivar usuario
auth.desactivar_usuario(usuario_id=3)

# Obtener todos los usuarios
usuarios = auth.obtener_usuarios()
```

---

## Cambios en Firmas de Funciones

### db_unified.py

```python
# Agregar producto (NUEVA FIRMA)
agregar_producto(nombre, cantidad, precio, categoria_id=None, usuario_id=None)

# Actualizar producto (NUEVA FIRMA)
actualizar_producto(id_producto, nombre, cantidad, precio, categoria_id=None, usuario_id=None)

# Eliminar producto (NUEVA FIRMA)
eliminar_producto(id_producto, usuario_id=None)

# Obtener productos (CAMBIADA ESTRUCTURA DE RETORNO)
# Ahora incluye: (id, nombre, cantidad, precio, categoria_nombre, fecha_creacion)
obtener_productos()
```

### auth_unified.py

```python
# Registrar usuario (NUEVA FIRMA)
registrar_usuario(usuario, password, nombre_completo="", rol="usuario")

# Verificar login (CAMBIADA ESTRUCTURA DE RETORNO)
# Ahora incluye: {'id', 'usuario', 'nombre_completo', 'rol'}
verificar_login(usuario, password)
```

---

## Actualizar Interfaz para Usar Categorías

### Ejemplo: Agregar Dropdown de Categorías

```python
# En gui/interfaz.py

# 1. Obtener categorías al inicializar
categorias = database.obtener_categorias()

# 2. Crear dropdown
dropdown_categoria = ctk.CTkComboBox(
    frame_izquierdo,
    values=[cat[1] for cat in categorias],  # Nombres de categorías
    width=280
)
dropdown_categoria.pack(pady=10)

# 3. Al guardar producto
def guardar_producto():
    nombre = entrada_nombre.get()
    cantidad = int(entrada_cantidad.get())
    precio = float(entrada_precio.get())
    
    # Obtener ID de categoría seleccionada
    categoria_nombre = dropdown_categoria.get()
    categoria_id = next((cat[0] for cat in categorias if cat[1] == categoria_nombre), None)
    
    # Agregar con categoría y usuario
    database.agregar_producto(
        nombre=nombre,
        cantidad=cantidad,
        precio=precio,
        categoria_id=categoria_id,
        usuario_id=usuario_actual['id']
    )
```

---

## Actualizar Tabla para Mostrar Categorías

```python
# En obtener_productos()
productos = database.obtener_productos()

# La tabla ahora tiene 6 columnas en lugar de 4:
# (id, nombre, cantidad, precio, categoria, fecha_creacion)

tabla_productos.heading("Categoria", text="Categoría")
tabla_productos.column("Categoria", width=120)

for producto in productos:
    tabla_productos.insert("", "end", values=(
        producto[0],  # id
        producto[1],  # nombre
        producto[2],  # cantidad
        f"${producto[3]:,.0f}",  # precio
        producto[4] or "Sin categoría",  # categoria
    ))
```

---

## Ventajas de la Nueva Estructura

### 1. Integridad Referencial
- Foreign Keys aseguran consistencia
- No se pueden eliminar usuarios con productos asociados (a menos que se especifique CASCADE)

### 2. Auditoría Completa
- Registro de quién creó/modificó/eliminó cada producto
- Trazabilidad completa de cambios

### 3. Organización
- Productos organizados por categorías
- Filtros y búsquedas más eficientes

### 4. Estadísticas
- Reportes por categoría
- Análisis de inventario mejorado
- Valor total calculado automáticamente

### 5. Roles y Permisos
- Sistema de roles (admin/usuario)
- Base para implementar permisos granulares

---

## Rollback (Volver Atrás)

Si necesitas volver a las bases de datos antiguas:

```bash
# 1. Renombrar la base unificada
mv data/gamestock.db data/gamestock_unified_backup.db

# 2. Las bases antiguas siguen ahí (no se eliminan en la migración)
# usuarios.db e inventario.db están intactas

# 3. Revertir imports en el código
# Cambiar db_unified → db
# Cambiar auth_unified → auth
```

---

## Troubleshooting

### Error: "FOREIGN KEY constraint failed"
**Causa**: Intentando insertar con FK inválida
**Solución**: Verifica que categoria_id y usuario_id existan en sus tablas

### Error: "no such table: historial_cambios"
**Causa**: Migración incompleta
**Solución**: Ejecuta `python migrar_db.py` nuevamente

### Error: "database is locked"
**Causa**: Múltiples conexiones abiertas
**Solución**: Asegúrate de cerrar todas las conexiones con `conexion.close()`

### Productos sin categoría
**Causa**: categoria_id = NULL
**Solución**: Asignar categoría "Otros" por defecto:
```python
categoria_id = categoria_id or 9  # 9 = Otros
```

---

## Checklist de Migración

- [ ] Hacer backup de datos actuales
- [ ] Ejecutar `python migrar_db.py`
- [ ] Verificar que usuarios y productos se migraron
- [ ] Actualizar imports en todos los archivos
- [ ] Probar funcionalidad de login
- [ ] Probar CRUD de productos
- [ ] Verificar que las categorías funcionan
- [ ] Revisar logs para errores
- [ ] Probar todas las funciones principales

---

## Soporte

Si encuentras problemas durante la migración:

1. Revisa los logs: `python ver_historial_logs.py | grep ERROR`
2. Verifica foreign keys: `sqlite3 data/gamestock.db "PRAGMA foreign_key_check"`
3. Consulta la documentación del MER: `docs/MER.md`

---

## Siguiente Paso

Una vez completada la migración, actualiza el MER:

```bash
# El MER.md necesita actualizarse para reflejar la nueva estructura
# con relaciones FK, categorías e historial
```
