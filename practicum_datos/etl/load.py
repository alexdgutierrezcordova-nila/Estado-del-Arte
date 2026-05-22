# ==========================================
# MÓDULO: CARGA
# Inserción en PostgreSQL con manejo de conflictos
# ==========================================

import os
import psycopg2
import pandas as pd
from psycopg2 import sql
from dotenv import load_dotenv

from config import BATCH_SIZE


def conectar_bd() -> psycopg2.extensions.connection:
    """
    Establece conexión a PostgreSQL usando credenciales desde .env
    
    Returns:
        psycopg2.extensions.connection: Conexión a la BD o None si falla
    """
    # Cargar variables de entorno desde .env
    load_dotenv()
    
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            client_encoding='UTF8'
        )
        print(f"✓ Conectado a {DB_NAME}")
        return conn
    except psycopg2.Error as e:
        print(f"Error conectando a PostgreSQL: {e}")
        return None


def cargar_tabla(conn: psycopg2.extensions.connection,
                nombre_tabla: str,
                df: pd.DataFrame) -> bool:
    """
    Inserta un DataFrame en una tabla de PostgreSQL usando ON CONFLICT DO NOTHING
    para evitar romper registros existentes.
    
    Args:
        conn (psycopg2.extensions.connection): Conexión a PostgreSQL
        nombre_tabla (str): Nombre de la tabla destino
        df (pd.DataFrame): DataFrame a insertar
        
    Returns:
        bool: True si la inserción fue exitosa, False si hubo error
    """
    try:
        cursor = conn.cursor()
        
        # Reemplazar NaN con None para PostgreSQL
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].where(pd.notna(df[col]), None)
        
        # Preparar columnas y placeholders
        columnas = list(df.columns)
        valores_placeholder = ','.join(['%s'] * len(columnas))
        
        # Construir INSERT con ON CONFLICT DO NOTHING
        insert_sql = f"""
        INSERT INTO {nombre_tabla} ({','.join(columnas)})
        VALUES ({valores_placeholder})
        ON CONFLICT DO NOTHING
        """
        
        # Convertir DataFrame a lista de tuplas
        datos = [tuple(row) for row in df.itertuples(index=False, name=None)]
        
        print(f"  Insertando {nombre_tabla}... ({len(datos)} registros)")
        
        # Insertar en lotes de BATCH_SIZE
        for i in range(0, len(datos), BATCH_SIZE):
            batch = datos[i:i + BATCH_SIZE]
            cursor.executemany(insert_sql, batch)
            conn.commit()
            print(f"    {min(i + BATCH_SIZE, len(datos))}/{len(datos)}", end='\r')
        
        print(f"  ✓ {nombre_tabla}: {len(datos)} registros insertados        ")
        cursor.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Error insertando en {nombre_tabla}: {e}")
        conn.rollback()
        return False
