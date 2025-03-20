import sqlite3

# Nombre de la base de datos
DB_NAME = "medallas.db"

def create_tables():
    """Crea las tablas si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ✅ Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL
        )
    ''')

    # ✅ Crear tabla de medallas con clave foránea
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medallas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            medalla TEXT NOT NULL,
            replay TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario)
        )
    ''')

    conn.commit()
    conn.close()

# ✅ Insertar un nuevo usuario
def insert_usuario(id_usuario: int, nombre: str) -> bool:
    """Registra un usuario si no existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,))
    if cursor.fetchone():
        conn.close()
        return False  # Usuario ya existe

    cursor.execute("INSERT INTO usuarios (id_usuario, nombre) VALUES (?, ?)", (id_usuario, nombre))
    conn.commit()
    conn.close()
    return True

# ✅ Obtener nombre del usuario
def select_nombre_by_user(id_usuario: int):
    """Devuelve el nombre del usuario si existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuarios WHERE id_usuario = ?", (id_usuario,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# ✅ Seleccionar medallas con el nombre del usuario
def select_medallas_by_user(usuario_id: int):
    """Obtiene todas las medallas de un usuario y su nombre."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.nombre, m.medalla, m.replay
        FROM medallas m
        JOIN usuarios u ON m.usuario_id = u.id_usuario
        WHERE m.usuario_id = ?
    ''', (usuario_id,))
    
    medallas = cursor.fetchall()
    conn.close()
    return medallas  # Devuelve el nombre del usuario junto con las medallas

def insert_medalla(usuario_id: int, medalla: str, replay: str) -> bool:
    """Inserta una nueva medalla en la base de datos solo si el usuario existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar si el usuario existe
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (usuario_id,))
    if not cursor.fetchone():
        conn.close()
        return False  # Usuario no existe

    # Insertar la medalla
    cursor.execute("INSERT INTO medallas (usuario_id, medalla, replay) VALUES (?, ?, ?)", 
                   (usuario_id, medalla, replay))
    conn.commit()
    conn.close()
    return True  # Medalla insertada con éxito

def select_top_usuarios():
    """Devuelve los 10 usuarios con más medallas, ordenados de mayor a menor."""
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()  # ✅ Así creas el cursor correctamente

    
    cursor.execute("""
        SELECT usuarios.nombre, COUNT(medallas.id) as cantidad_medallas
        FROM usuarios
        JOIN medallas ON usuarios.id_usuario = medallas.usuario_id
        GROUP BY usuarios.id_usuario
        ORDER BY cantidad_medallas DESC
        LIMIT 10;
    """)
    
    top_usuarios = cursor.fetchall()
    
    conexion.close()
    return top_usuarios

