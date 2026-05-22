# ==========================================
# MÓDULO: TRANSFORMACIÓN
# Construcción de dimensiones y tabla de hechos
# ==========================================

import pandas as pd
import numpy as np

# Este módulo se encarga de la transformación de los datos crudos extraídos del Excel en tablas de dimensiones y hechos listas para cargar en PostgreSQL.
def construir_dim_ubicacion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la tabla de dimensión de ubicaciones geográficas.
    
    Args:
        df (pd.DataFrame): DataFrame crudo con los datos AMIE
        
    Returns:
        pd.DataFrame: Tabla dim_ubicacion con id_ubicacion como PK
    """
    columnas_geograficas = [
        "Provincia", "Cod_Provincia", "Canton", "Cod_Canton",
        "Parroquia", "Cod_Parroquia", "Zona", "Regimen_Escolar"
    ]
    
    # Extrar, eliminar duplicados y resetear índice
    df_ubicacion = df[columnas_geograficas].drop_duplicates().reset_index(drop=True)
    
    # Crear clave primaria id_ubicacion
    df_ubicacion['id_ubicacion'] = df_ubicacion.index + 1
    
    # Convertir nombres de columnas a minúsculas para PostgreSQL
    df_ubicacion.columns = df_ubicacion.columns.str.lower()
    
    return df_ubicacion


def construir_dim_institucion(df: pd.DataFrame, dim_ubicacion: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la tabla de dimensión de instituciones educativas.
    
    Args:
        df (pd.DataFrame): DataFrame crudo con los datos AMIE
        dim_ubicacion (pd.DataFrame): Tabla de ubicaciones (ya con minúsculas de id_ubicacion)
        
    Returns:
        pd.DataFrame: Tabla dim_institucion con cod_amie como PK
    """
    columnas_geograficas = [
        "Provincia", "Cod_Provincia", "Canton", "Cod_Canton",
        "Parroquia", "Cod_Parroquia", "Zona", "Regimen_Escolar"
    ]
    
    columnas_institucion = [
        "Codigo_Institucion", "Nombre_Institucion", "Tipo_Educacion",
        "Sostenimiento", "Area", "Jurisdiccion", "id_ubicacion"
    ]
    
    # Preparar dim_ubicacion para el merge: restaurar nombres originales (excepto id_ubicacion)
    df_ubicacion_para_merge = dim_ubicacion.copy()
    # Renombrar de minúsculas a mayúsculas para que coincida con df original
    rename_dict = {
        'provincia': 'Provincia',
        'cod_provincia': 'Cod_Provincia',
        'canton': 'Canton',
        'cod_canton': 'Cod_Canton',
        'parroquia': 'Parroquia',
        'cod_parroquia': 'Cod_Parroquia',
        'zona': 'Zona',
        'regimen_escolar': 'Regimen_Escolar'
    }
    df_ubicacion_para_merge = df_ubicacion_para_merge.rename(columns=rename_dict)
    
    # Hacer merge con df original para agregar id_ubicacion
    df_con_ubicacion = df.merge(
        df_ubicacion_para_merge[columnas_geograficas + ['id_ubicacion']],
        on=columnas_geograficas,
        how="left"
    )
    
    # Extraer columnas de institución
    df_institucion = df_con_ubicacion[columnas_institucion].copy()
    
    # Normalizar case-sensitivity del Codigo_Institucion ANTES de eliminar duplicados
    # Esto previene que '09H02009' y '09h02009' se consideren valores diferentes
    df_institucion['Codigo_Institucion'] = df_institucion['Codigo_Institucion'].str.lower()
    
    # Eliminar duplicados por Codigo_Institucion (clave primaria)
    df_institucion = df_institucion.drop_duplicates(
        subset=['Codigo_Institucion'],
        keep='first'
    ).reset_index(drop=True)
    
    # Renombrar Codigo_Institucion a cod_amie
    df_institucion = df_institucion.rename(
        columns={"Codigo_Institucion": "cod_amie"}
    )
    
    # Convertir nombres de columnas a minúsculas para PostgreSQL
    df_institucion.columns = df_institucion.columns.str.lower()
    
    return df_institucion


def construir_fact_matricula(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la tabla de hechos con datos de matrícula por año lectivo.
    
    Args:
        df (pd.DataFrame): DataFrame crudo con los datos AMIE
        
    Returns:
        pd.DataFrame: Tabla fact_matricula con id_matricula como PK
    """
    columnas_matricula = [
        "Periodo", "Codigo_Institucion", "Estudiantes_Femenino",
        "Estudiantes_Masculino", "Total_Estudiantes", "Docentes_Femenino",
        "Docentes_Masculino", "Total_Docentes"
    ]
    
    # Seleccionar columnas necesarias
    df_matricula = df[columnas_matricula].copy()
    
    # Renombrar Periodo y Codigo_Institucion
    df_matricula = df_matricula.rename(columns={
        "Periodo": "anio_lectivo",
        "Codigo_Institucion": "cod_amie"
    })
    
    # Normalizar case-sensitivity de cod_amie para coincidir con dim_institucion
    # (debe ser minúscula para FK correcta)
    df_matricula['cod_amie'] = df_matricula['cod_amie'].str.lower()
    
    # Calcular ratio estudiantes/docentes ANTES de convertir a minúsculas
    # (evitando división por cero)
    df_matricula['ratio_est_docente'] = np.where(
        df_matricula['Total_Docentes'] == 0,
        None,
        round(df_matricula['Total_Estudiantes'] / df_matricula['Total_Docentes'], 1)
    )
    
    # Insertar id_matricula como primera columna
    df_matricula.insert(0, 'id_matricula', range(1, len(df_matricula) + 1))
    
    # Convertir nombres de columnas a minúsculas para PostgreSQL
    df_matricula.columns = df_matricula.columns.str.lower()
    
    return df_matricula
