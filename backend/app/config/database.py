"""
Configuración de la base de datos PostgreSQL con Supabase
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

load_dotenv()

# Configuración de la base de datos
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'db.your-project.supabase.co'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

# Alternativa: usar DATABASE_URL directamente
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    """
    Obtiene una conexión a la base de datos PostgreSQL
    """
    try:
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise


@contextmanager
def get_db_cursor():
    """
    Context manager para obtener un cursor de la base de datos
    Uso:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM productos")
            results = cursor.fetchall()
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def test_connection():
    """
    Prueba la conexión a la base de datos
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Conexion exitosa a PostgreSQL: {version['version']}")
            return True
    except Exception as e:
        print(f"Error de conexion: {e}")
        return False


if __name__ == "__main__":
    test_connection()
