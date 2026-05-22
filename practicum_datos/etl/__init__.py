# ==========================================
# ETL Package para AMIE
# ==========================================

# Este paquete contiene los módulos necesarios para realizar el proceso de ETL (Extract, Transform, Load) para el proyecto AMIE.
from .extract import extraer_datos
from .transform import (
    construir_dim_ubicacion,
    construir_dim_institucion,
    construir_fact_matricula,
)
from .load import conectar_bd, cargar_tabla
from .pipeline import main

__all__ = [
    "extraer_datos",
    "construir_dim_ubicacion",
    "construir_dim_institucion",
    "construir_fact_matricula",
    "conectar_bd",
    "cargar_tabla",
    "main",
]
