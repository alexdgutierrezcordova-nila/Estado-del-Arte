# ==========================================
# MÓDULO: EXTRACCIÓN
# Lectura del archivo Excel con datos AMIE
# ==========================================

# Este módulo se encarga de la extracción de datos desde el archivo Excel proporcionado por el Ministerio de Educación.
import pandas as pd

# Función para extraer datos desde el archivo Excel
def extraer_datos(ruta: str) -> pd.DataFrame:
    """
    Lee el archivo Excel con engine='openpyxl'.
    Lee la hoja 'Historico_Inicio' que contiene el dataset más completo (2009-2025).
    
    Args:
        ruta (str): Ruta al archivo Excel
        
    Returns:
        pd.DataFrame: DataFrame crudo con todos los registros
    """
    print("Cargando el archivo Excel (esto puede tomar unos minutos)...")
    
    # Leer la hoja 'Historico_Inicio' que tiene todos los años (2009-2025)
    df = pd.read_excel(ruta, sheet_name='Historico_Inicio')
    
    # Renombrar columnas para compatibilidad con transform.py
    df = df.rename(columns={
        "Anio_lectivo": "Periodo",
        "AMIE":         "Codigo_Institucion"
    })
    
    print(f"Archivo cargado: {len(df)} filas, {len(df.columns)} columnas")
    print(f"Columnas disponibles: {list(df.columns)}")
    
    return df
