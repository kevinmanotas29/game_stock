# Modelo Entidad-Relación (MER) - GameStock

## Descripción General

GameStock utiliza **dos bases de datos SQLite** independientes para separar la lógica de autenticación de la gestión de inventario.

## 1. Base de Datos: usuarios.db

### Ubicación
```
data/usuarios.db
```

### Entidad: usuarios

```
┌─────────────────────────────────────────┐
│              USUARIOS                    │
├─────────────────────────────────────────┤
│ PK  id                  INTEGER          │
│ UK  usuario             TEXT             │
│     password            TEXT             │
│     nombre_completo     TEXT             │
│     fecha_registro      TIMESTAMP        │
└─────────────────────────────────────────┘

PK = Primary Key (Clave Primaria)
UK = Unique Key (Clave Única)
```

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id** | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único del usuario |
| **usuario** | TEXT | UNIQUE, NOT NULL | Nombre de usuario (login) |
| **password** | TEXT | NOT NULL | Contraseña encriptada (SHA-256) |
| **nombre_completo** | TEXT | NULL | Nombre completo del usuario |
| **fecha_registro** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación de la cuenta |

### Restricciones

- **Clave Primaria**: `id`
- **Clave Única**: `usuario` (no puede haber usuarios duplicados)
- **No nulos**: `usuario`, `password`

### Operaciones CRUD

```python
# CREATE
registrar_usuario(usuario, password, nombre_completo)

# READ
verificar_login(usuario, password)
obtener_total_usuarios()

# UPDATE
No implementado actualmente

# DELETE
No implementado actualmente
```

---

## 2. Base de Datos: inventario.db

### Ubicación
```
data/inventario.db
```

### Entidad: productos

```
┌─────────────────────────────────────────┐
│              PRODUCTOS                   │
├─────────────────────────────────────────┤
│ PK  id                  INTEGER          │
│     nombre              TEXT             │
│     cantidad            INTEGER          │
│     precio              REAL             │
└─────────────────────────────────────────┘

PK = Primary Key (Clave Primaria)
```

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id** | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único del producto |
| **nombre** | TEXT | NOT NULL | Nombre del videojuego/producto |
| **cantidad** | INTEGER | NOT NULL | Stock disponible (unidades) |
| **precio** | REAL | NOT NULL | Precio unitario en COP |

### Restricciones

- **Clave Primaria**: `id`
- **No nulos**: `nombre`, `cantidad`, `precio`
- **Tipos**: `cantidad` debe ser entero, `precio` puede tener decimales

### Operaciones CRUD

```python
# CREATE
agregar_producto(nombre, cantidad, precio)

# READ
obtener_productos()

# UPDATE
actualizar_producto(id_producto, nombre, cantidad, precio)

# DELETE
eliminar_producto(id_producto)
```

---

## Diagrama Entidad-Relación Completo

```
┌────────────────────────────────┐
│  Base de Datos: usuarios.db    │
│                                 │
│  ┌──────────────────────────┐  │
│  │      USUARIOS            │  │
│  ├──────────────────────────┤  │
│  │ PK  id                   │  │
│  │ UK  usuario              │  │
│  │     password (SHA-256)   │  │
│  │     nombre_completo      │  │
│  │     fecha_registro       │  │
│  └──────────────────────────┘  │
│                                 │
└────────────────────────────────┘


┌────────────────────────────────┐
│ Base de Datos: inventario.db   │
│                                 │
│  ┌──────────────────────────┐  │
│  │      PRODUCTOS           │  │
│  ├──────────────────────────┤  │
│  │ PK  id                   │  │
│  │     nombre               │  │
│  │     cantidad             │  │
│  │     precio               │  │
│  └──────────────────────────┘  │
│                                 │
└────────────────────────────────┘

Nota: No hay relación directa entre las tablas
      ya que están en bases de datos separadas.
```

---

## Relaciones entre Entidades

### Relación Implícita

Aunque las tablas están en bases de datos separadas, existe una **relación implícita** a nivel de aplicación:

```
USUARIOS (1) ───── (N) PRODUCTOS
```

- Un **usuario** puede gestionar **muchos productos**
- Un **producto** es gestionado por **uno o más usuarios** (implícitamente a través de sesiones)

**NOTA**: Esta relación NO está implementada a nivel de base de datos mediante llaves foráneas. Es manejada por la lógica de la aplicación (sesiones de usuario).

---

## Decisiones de Diseño

### 1. Bases de Datos Separadas

**Razón**: Separación de responsabilidades
- `usuarios.db`: Autenticación y gestión de usuarios
- `inventario.db`: Lógica de negocio (inventario)

**Ventajas**:
- Mejor organización del código
- Facilita el mantenimiento
- Permite escalabilidad futura
- Aislamiento de datos sensibles

### 2. Sin Relaciones FK (Foreign Keys)

**Razón**: Simplicidad y bases de datos independientes

**Consideración futura**: Si se requiere auditoría (quién modificó qué producto), se podría:
1. Unificar en una sola base de datos
2. Agregar tabla `historial_cambios` con FK a `usuarios` y `productos`

### 3. Encriptación de Contraseñas

**Método**: SHA-256
- Contraseñas nunca se almacenan en texto plano
- Hash unidireccional
- Seguridad básica implementada

---

## Esquema SQL Completo

### usuarios.db

```sql
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nombre_completo TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsquedas rápidas por usuario
CREATE INDEX IF NOT EXISTS idx_usuario ON usuarios(usuario);
```

### inventario.db

```sql
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio REAL NOT NULL
);

-- Índice para búsquedas por nombre
CREATE INDEX IF NOT EXISTS idx_nombre ON productos(nombre);
```

---

## Consultas SQL Comunes

### Autenticación

```sql
-- Registrar usuario
INSERT INTO usuarios (usuario, password, nombre_completo)
VALUES (?, ?, ?);

-- Verificar login
SELECT id, nombre_completo 
FROM usuarios
WHERE usuario = ? AND password = ?;

-- Contar usuarios
SELECT COUNT(*) FROM usuarios;
```

### Inventario

```sql
-- Agregar producto
INSERT INTO productos (nombre, cantidad, precio)
VALUES (?, ?, ?);

-- Obtener todos los productos
SELECT * FROM productos;

-- Actualizar producto
UPDATE productos
SET nombre=?, cantidad=?, precio=?
WHERE id=?;

-- Eliminar producto
DELETE FROM productos WHERE id = ?;

-- Buscar por nombre
SELECT * FROM productos WHERE nombre LIKE '%?%';

-- Calcular valor total
SELECT SUM(cantidad * precio) as valor_total FROM productos;

-- Productos con bajo stock
SELECT * FROM productos WHERE cantidad < 5;
```

---

## Normalización

### usuarios.db

**Forma Normal**: 3FN (Tercera Forma Normal)
- No hay dependencias transitivas
- Todos los atributos dependen de la clave primaria
- No hay redundancia de datos

### inventario.db

**Forma Normal**: 3FN (Tercera Forma Normal)
- Tabla simple y normalizada
- Sin redundancia
- Cada producto es una entidad única

---

## Mejoras Futuras Sugeridas

### 1. Unificar Bases de Datos

```sql
-- Nueva estructura unificada
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nombre_completo TEXT,
    rol TEXT DEFAULT 'usuario',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio REAL NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creador_id INTEGER,
    FOREIGN KEY (usuario_creador_id) REFERENCES usuarios(id)
);

CREATE TABLE historial_cambios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    accion TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalle TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);
```

### 2. Agregar Categorías

```sql
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

ALTER TABLE productos ADD COLUMN categoria_id INTEGER;
ALTER TABLE productos ADD FOREIGN KEY (categoria_id) REFERENCES categorias(id);
```

### 3. Sistema de Roles

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    permisos TEXT
);

ALTER TABLE usuarios ADD COLUMN rol_id INTEGER;
ALTER TABLE usuarios ADD FOREIGN KEY (rol_id) REFERENCES roles(id);
```

---

## Diagrama de Secuencia: Flujo de Autenticación

```
Usuario → GUI (Login) → auth.py → usuarios.db
   |          |            |           |
   |---login->|            |           |
   |          |--verificar_login()---->|
   |          |            |--SELECT-->|
   |          |            |<-result---|
   |          |<--usuario_data---------|
   |<-sesión--|            |           |
```

## Diagrama de Secuencia: Flujo CRUD Productos

```
Usuario → GUI (Interfaz) → db.py → inventario.db
   |          |              |          |
   |--crear-->|              |          |
   |          |--agregar_producto()---->|
   |          |              |--INSERT->|
   |          |              |<-OK------|
   |<-refresh-|              |          |
```

---

## Respaldo y Migración

### Respaldo

```bash
# Respaldar usuarios
cp data/usuarios.db backup/usuarios_$(date +%Y%m%d).db

# Respaldar inventario
cp data/inventario.db backup/inventario_$(date +%Y%m%d).db
```

### Exportar a SQL

```bash
# Exportar usuarios
sqlite3 data/usuarios.db .dump > usuarios.sql

# Exportar inventario
sqlite3 data/inventario.db .dump > inventario.sql
```

### Restaurar

```bash
# Restaurar desde SQL
sqlite3 data/usuarios.db < usuarios.sql
sqlite3 data/inventario.db < inventario.sql
```

---

## Referencias

- **SQLite Documentation**: https://www.sqlite.org/docs.html
- **Normalización de Bases de Datos**: https://en.wikipedia.org/wiki/Database_normalization
- **Python sqlite3**: https://docs.python.org/3/library/sqlite3.html
