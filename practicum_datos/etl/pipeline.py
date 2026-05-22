# ==========================================
# MÓDULO: PIPELINE
# Orquestador principal del ETL
# ==========================================

# Este módulo es el orquestador principal del proceso ETL. Ejecuta las fases en orden: Extracción → Transformación → Carga.
from config import RUTA_EXCEL
from .extract import extraer_datos
from .transform import (
    construir_dim_ubicacion,
    construir_dim_institucion,
    construir_fact_matricula,
)
from .load import conectar_bd, cargar_tabla


def main():
    """
    Orquestador principal del ETL.
    Ejecuta las fases en orden: Extracción → Transformación → Carga
    """
    # Imprimir banner de inicio
    # Esto ayuda a identificar claramente el inicio del proceso ETL en la consola
    print("=" * 60)
    print("INICIANDO ETL AMIE")
    print("=" * 60)
    
    # ==========================================
    # 1. EXTRACCIÓN
    # ==========================================
    print("\n[1/5] EXTRACCIÓN DE DATOS\n")
    df_crudo = extraer_datos(RUTA_EXCEL)
    
    # ==========================================
    # 2. TRANSFORMACIÓN
    # ==========================================
    print("\n[2/5] TRANSFORMACIÓN - Construyendo dim_ubicacion")
    dim_ubicacion_sin_min = construir_dim_ubicacion(df_crudo)
    # dim_ubicacion ya viene con minúsculas para PostgreSQL
    dim_ubicacion = dim_ubicacion_sin_min.copy()
    print(f"  ✓ {len(dim_ubicacion)} ubicaciones únicas")
    
    print("[3/5] TRANSFORMACIÓN - Construyendo dim_institucion")
    # Pasamos dim_ubicacion (con minúsculas) a dim_institucion
    # que se encarga de restaurar los nombres originales para el merge
    dim_institucion = construir_dim_institucion(df_crudo, dim_ubicacion)
    print(f"  ✓ {len(dim_institucion)} instituciones únicas")
    
    print("[4/5] TRANSFORMACIÓN - Construyendo fact_matricula")
    fact_matricula = construir_fact_matricula(df_crudo)
    print(f"  ✓ {len(fact_matricula)} registros de matrícula")
    
    # ==========================================
    # 3. VISTA PREVIA
    # ==========================================
    print("\n--- PRIMERAS 3 FILAS DE DIM_UBICACION ---")
    print(dim_ubicacion.head(3))
    
    print("\n--- PRIMERAS 3 FILAS DE DIM_INSTITUCION ---")
    print(dim_institucion.head(3))
    
    print("\n--- PRIMERAS 3 FILAS DE FACT_MATRICULA ---")
    print(fact_matricula.head(3))
    
    # ==========================================
    # 4. CONEXIÓN A BD
    # ==========================================
    print("\n[5/5] CARGA A POSTGRESQL\n")
    conn = conectar_bd()
    
    if not conn:
        print("\nNo se pudo conectar a PostgreSQL")
        return False
    
    # ==========================================
    # 5. CARGA DE DATOS
    # ==========================================
    print("\nIniciando carga de datos...\n")
    
    resultados = []
    resultados.append(cargar_tabla(conn, 'dim_ubicacion', dim_ubicacion))
    resultados.append(cargar_tabla(conn, 'dim_institucion', dim_institucion))
    resultados.append(cargar_tabla(conn, 'fact_matricula', fact_matricula))
    
    # Cerrar conexión
    conn.close()
    
    # ==========================================
    # 6. RESUMEN FINAL
    # ==========================================
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    print(f"dim_ubicacion:    {len(dim_ubicacion)} registros")
    print(f"dim_institucion:  {len(dim_institucion)} registros")
    print(f"fact_matricula:   {len(fact_matricula)} registros")
    
    if all(resultados):
        print("\nCARGA COMPLETADA EXITOSAMENTE")
        return True
    else:
        print("\nCARGA CON ALGUNOS ERRORES")
        return False


if __name__ == "__main__":
    main()
