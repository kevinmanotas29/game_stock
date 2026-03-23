# Modelo Entidad-Relación (MER) - GameStock

## Descripción General

GameStock utiliza **una sola base de datos SQLite unificada** (`gamestock.db`) con **4 tablas relacionadas mediante Foreign Keys (FK)** para gestionar usuarios, productos, categorías y auditoría de cambios.

---

## Base de Datos Unificada: gamestock.db

### Ubicación
```
data/gamestock.db
```

### Características
- Base de datos relacional con **FOREIGN KEYS habilitadas**
- **4 tablas principales** con relaciones definidas
- **Auditoría completa** de todas las operaciones
- **7 categorías** de productos tecnológicos predefinidas
- **Integridad referencial** garantizada

---

## Diagrama de Relaciones

```
┌─────────────────┐         ┌──────────────────┐
│    USUARIOS     │         │   CATEGORIAS     │
├─────────────────┤         ├──────────────────┤
│ PK id           │         │ PK id            │
│ UK usuario      │         │ UK nombre        │
│    password     │         │    descripcion   │
│    nombre_com.. │         │    fecha_creac.. │
│    rol          │         └──────────────────┘
│    fecha_reg..  │                │
│    activo       │                │
└─────────────────┘                │
        │                          │
        │ 1:N                      │ 1:N
        │                          │
        ▼                          ▼
┌──────────────────────────────────────────┐
│              PRODUCTOS                    │
├──────────────────────────────────────────┤
│ PK  id                  INTEGER           │
│     nombre              TEXT              │
│     cantidad            INTEGER           │
│     precio              REAL              │
│ FK  categoria_id        INTEGER  ───────►│
│ FK  usuario_creador_id  INTEGER  ───────►│
│     fecha_creacion      TIMESTAMP         │
│     fecha_actualizacion TIMESTAMP         │
└──────────────────────────────────────────┘
        │
        │ 1:N
        │
        ▼
┌─────────────────────────────────────────┐
│       HISTORIAL_CAMBIOS                 │
├─────────────────────────────────────────┤
│ PK  id                  INTEGER          │
│ FK  usuario_id          INTEGER  ───────►│
│ FK  producto_id         INTEGER  ───────►│
│     accion              TEXT             │
│     detalle             TEXT             │
│     fecha               TIMESTAMP        │
└─────────────────────────────────────────┘

PK = Primary Key (Clave Primaria)
UK = Unique Key (Clave Única)
FK = Foreign Key (Clave Foránea)
```

---

## 1. Tabla: usuarios

### Propósito
Gestiona la autenticación y perfiles de usuarios del sistema.

### Estructura

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nombre_completo TEXT,
    rol TEXT DEFAULT 'usuario' CHECK(rol IN ('admin', 'usuario')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo INTEGER DEFAULT 1
)
```

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id** | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único del usuario |
| **usuario** | TEXT | UNIQUE, NOT NULL | Nombre de usuario (login) |
| **password** | TEXT | NOT NULL | Contraseña encriptada (SHA-256) |
| **nombre_completo** | TEXT | NULL | Nombre completo del usuario |
| **rol** | TEXT | DEFAULT 'usuario', CHECK | Rol del usuario (admin o usuario) |
| **fecha_registro** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación de la cuenta |
| **activo** | INTEGER | DEFAULT 1 | Estado del usuario (1=activo, 0=inactivo) |

### Restricciones
- **Clave Primaria**: `id`
- **Clave Única**: `usuario`
- **Check**: `rol` debe ser 'admin' o 'usuario'
- **Índice**: `idx_usuario` en campo `usuario`

### Operaciones

```python
# CREATE
registrar_usuario(usuario, password, nombre_completo)

# READ
verificar_login(usuario, password)
obtener_total_usuarios()

# UPDATE
No implementado

# DELETE
No implementado
```

---

## 2. Tabla: categorias

### Propósito
Define las categorías de productos tecnológicos disponibles en el inventario.

### Estructura

```sql
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id** | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único de la categoría |
| **nombre** | TEXT | UNIQUE, NOT NULL | Nombre de la categoría |
| **descripcion** | TEXT | NULL | Descripción detallada |
| **fecha_creacion** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación |

### Categorías Predefinidas

| ID | Nombre | Descripción |
|----|--------|-------------|
| 1 | Celulares | Dispositivos móviles y smartphones |
| 2 | Computadores | Computadores portátiles y de escritorio |
| 3 | Consolas | Consolas de videojuegos |
| 4 | Gaming | Equipos y accesorios para videojuegos |
| 5 | Perifericos | Dispositivos de entrada y salida |
| 6 | Audio | Equipos de sonido y audifonos |
| 7 | Wearables | Dispositivos tecnologicos portables |

### Operaciones

```python
# READ
obtener_categorias()  # Obtiene todas las categorías

# CREATE/UPDATE/DELETE
Manual mediante DBeaver o SQL directo
```

---

## 3. Tabla: productos

### Propósito
Almacena el inventario de productos tecnológicos con relación a categorías y usuarios.

### Estructura

```sql
CREATE TABLE productos (
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
```

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id** | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único del producto |
| **nombre** | TEXT | NOT NULL | Nombre del producto tecnológico |
| **cantidad** | INTEGER | NOT NULL, CHECK >= 0 | Stock disponible (unidades) |
| **precio** | REAL | NOT NULL, CHECK >= 0 | Precio unitario en COP |
| **categoria_id** | INTEGER | FK → categorias(id) | Categoría del producto |
| **usuario_creador_id** | INTEGER | FK → usuarios(id) | Usuario que creó el producto |
| **fecha_creacion** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación |
| **fecha_actualizacion** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Última actualización |

### Restricciones
- **Clave Primaria**: `id`
- **Foreign Keys**:
  - `categoria_id` → `categorias(id)` (ON DELETE SET NULL)
  - `usuario_creador_id` → `usuarios(id)` (ON DELETE SET NULL)
- **Check**: `cantidad >= 0`, `precio >= 0`
- **Índices**:
  - `idx_producto_nombre` en `nombre`
  - `idx_producto_categoria` en `categoria_id`

### Operaciones

```python
# CREATE
agregar_producto(nombre, cantidad, precio, categoria_id, usuario_id)

# READ
obtener_productos()
obtener_producto_por_id(producto_id)

# UPDATE
actualizar_producto(producto_id, nombre, cantidad, precio, categoria_id, usuario_id)

# DELETE
eliminar_producto(producto_id, usuario_id)
```

---

## 4. Tabla: historial_cambios

### Propósito
Auditoría completa de todas las operaciones CRUD realizadas sobre productos.

### Estructura

```sql
CREATE TABLE historial_cambios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    producto_id INTEGER,
    accion TEXT NOT NULL CHECK(accion IN ('CREAR', 'ACTUALIZAR', 'ELIMINAR')),
    detalle TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
)
```

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id** | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único del cambio |
| **usuario_id** | INTEGER | FK → usuarios(id), NOT NULL | Usuario que realizó la acción |
| **producto_id** | INTEGER | FK → productos(id) | Producto afectado (puede ser NULL si fue eliminado) |
| **accion** | TEXT | NOT NULL, CHECK | Tipo de operación realizada |
| **detalle** | TEXT | NULL | Descripción detallada del cambio |
| **fecha** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora del cambio |

### Restricciones
- **Clave Primaria**: `id`
- **Foreign Keys**:
  - `usuario_id` → `usuarios(id)` (ON DELETE CASCADE)
  - `producto_id` → `productos(id)` (ON DELETE SET NULL)
- **Check**: `accion` debe ser 'CREAR', 'ACTUALIZAR' o 'ELIMINAR'
- **Índices**:
  - `idx_historial_usuario` en `usuario_id`
  - `idx_historial_producto` en `producto_id`

### Tipos de Acciones

| Acción | Descripción | Detalle Ejemplo |
|--------|-------------|-----------------|
| **CREAR** | Se agregó un nuevo producto | "Producto 'iPhone 15' creado con 10 unidades a $4000000" |
| **ACTUALIZAR** | Se modificó un producto existente | "Producto 'iPhone 15' actualizado: cantidad 10→15" |
| **ELIMINAR** | Se eliminó un producto | "Producto 'iPhone 15' eliminado (10 unidades, $4000000)" |

### Operaciones

```python
# CREATE (automático)
registrar_cambio(usuario_id, producto_id, accion, detalle)

# READ
obtener_historial_producto(producto_id)
obtener_historial_usuario(usuario_id)
obtener_historial_reciente(limite=10)
```

---

## Relaciones Entre Tablas

### 1. usuarios → productos (1:N)
- **Relación**: Un usuario puede crear múltiples productos
- **FK**: `productos.usuario_creador_id` → `usuarios.id`
- **Comportamiento**: Si se elimina un usuario, `usuario_creador_id` se pone en NULL

### 2. categorias → productos (1:N)
- **Relación**: Una categoría puede tener múltiples productos
- **FK**: `productos.categoria_id` → `categorias.id`
- **Comportamiento**: Si se elimina una categoría, `categoria_id` se pone en NULL

### 3. usuarios → historial_cambios (1:N)
- **Relación**: Un usuario puede tener múltiples registros de cambios
- **FK**: `historial_cambios.usuario_id` → `usuarios.id`
- **Comportamiento**: Si se elimina un usuario, se eliminan sus registros de historial (CASCADE)

### 4. productos → historial_cambios (1:N)
- **Relación**: Un producto puede tener múltiples cambios registrados
- **FK**: `historial_cambios.producto_id` → `productos.id`
- **Comportamiento**: Si se elimina un producto, `producto_id` se pone en NULL (se mantiene el historial)

---

## Integridad Referencial

### ON DELETE Behaviors

| Tabla Origen | Tabla Destino | Comportamiento | Razón |
|--------------|---------------|----------------|-------|
| usuarios → productos | SET NULL | Mantener productos aunque el usuario se elimine |
| categorias → productos | SET NULL | Mantener productos aunque la categoría se elimine |
| usuarios → historial | CASCADE | Eliminar historial si el usuario se elimina |
| productos → historial | SET NULL | Mantener historial aunque el producto se elimine |

---

## Consultas Útiles

### Ver productos con sus categorías
```sql
SELECT 
    p.id,
    p.nombre,
    p.cantidad,
    p.precio,
    c.nombre as categoria,
    u.usuario as creador
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id
LEFT JOIN usuarios u ON p.usuario_creador_id = u.id;
```

### Ver historial de un producto
```sql
SELECT 
    h.fecha,
    u.usuario,
    h.accion,
    h.detalle
FROM historial_cambios h
JOIN usuarios u ON h.usuario_id = u.id
WHERE h.producto_id = 1
ORDER BY h.fecha DESC;
```

### Productos por categoría
```sql
SELECT 
    c.nombre as categoria,
    COUNT(p.id) as total_productos
FROM categorias c
LEFT JOIN productos p ON c.id = p.categoria_id
GROUP BY c.id, c.nombre
ORDER BY total_productos DESC;
```

### Productos con bajo stock
```sql
SELECT 
    p.nombre,
    p.cantidad,
    c.nombre as categoria
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id
WHERE p.cantidad < 5
ORDER BY p.cantidad ASC;
```

---

## Migración de Bases de Datos Antiguas

Si tienes las bases de datos antiguas (`usuarios.db` e `inventario.db`), estas **ya fueron migradas** a `gamestock.db`.

### Proceso de Migración
1. Crear tabla `usuarios` y migrar datos
2. Crear tabla `categorias` con categorías predefinidas
3. Crear tabla `productos` y migrar datos (sin categorías asignadas)
4. Crear tabla `historial_cambios` (vacía inicialmente)
5. Verificar integridad de datos

Las bases de datos antiguas fueron eliminadas después de la migración exitosa.

---

## Herramientas Recomendadas

### DBeaver (Recomendado)
- **Visualización gráfica** del diagrama ER
- **Navegación** intuitiva entre tablas
- **Edición** de datos con interfaz visual
- **Ejecución** de consultas SQL

### SQLite CLI
```bash
# Abrir base de datos
sqlite3 data/gamestock.db

# Ver tablas
.tables

# Ver estructura de una tabla
.schema productos

# Ejecutar consultas
SELECT * FROM productos;
```

---

## Mantenimiento

### Backup
```bash
# Backup manual
cp data/gamestock.db data/gamestock_backup_$(date +%Y%m%d).db

# Backup con SQLite
sqlite3 data/gamestock.db ".backup data/gamestock_backup.db"
```

### Vacío y Optimización
```sql
-- Recuperar espacio no utilizado
VACUUM;

-- Analizar estadísticas para optimizar consultas
ANALYZE;
```

---

## Resumen

| Elemento | Cantidad | Descripción |
|----------|----------|-------------|
| **Bases de datos** | 1 | `gamestock.db` (unificada) |
| **Tablas** | 4 | usuarios, categorias, productos, historial_cambios |
| **Foreign Keys** | 4 | Relaciones entre tablas |
| **Índices** | 6 | Para optimización de consultas |
| **Categorías** | 7 | Predefinidas para productos tecnológicos |
| **Integridad** | ✓ | FK habilitadas, CHECK constraints |
| **Auditoría** | ✓ | Historial completo de cambios |

---

## Contacto y Soporte

Para más información sobre la estructura de la base de datos o problemas técnicos, consulta:
- **README.md**: Documentación general del proyecto
- **LOGGING.md**: Sistema de logs y debugging
- **GEMINI_LIMITS.md**: Límites de la API de IA
