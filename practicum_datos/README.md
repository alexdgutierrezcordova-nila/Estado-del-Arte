# Proyecto AMIE — ETL con PostgreSQL

## Descripción

Proceso ETL (Extract, Transform, Load) modular que extrae datos del registro administrativo histórico AMIE del Ministerio de Educación del Ecuador desde un archivo Excel (2009-2025), los transforma en dimensiones y tabla de hechos, y los carga directamente en PostgreSQL mediante inserciones por lotes. El sistema previene la duplicación de registros existentes usando `ON CONFLICT DO NOTHING`.

## Estructura del proyecto

```
practicum_datos/
├── .env                      # Variables de entorno (credenciales PostgreSQL)
├── config.py                 # Constantes globales (BATCH_SIZE, ruta Excel)
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
├── etl/
│   ├── __init__.py          # Inicializador del paquete
│   ├── extract.py           # Lectura del archivo Excel
│   ├── transform.py         # Construcción de dimensiones y tabla de hechos
│   ├── load.py              # Conexión y inserción en PostgreSQL
│   └── pipeline.py          # Orquestador principal
└── sql/
    └── create_tables.sql    # Consultas DDL y consultas analíticas de la rúbrica
```

### Descripción de archivos

- **config.py**: Define constantes como `BATCH_SIZE` y la ruta del archivo Excel
- **.env**: Variables de entorno con credenciales de PostgreSQL (debe ser configurado manualmente)
- **requirements.txt**: Listado de dependencias Python necesarias
- **etl/extract.py**: Función `extraer_datos()` que lee el Excel desde la hoja 'Historico_Inicio' con openpyxl
- **etl/transform.py**: Funciones para construir `dim_ubicacion`, `dim_institucion` y `fact_matricula` con normalización de case-sensitivity
- **etl/load.py**: Funciones para conectar a PostgreSQL e insertar datos con ON CONFLICT
- **etl/pipeline.py**: Función `main()` que orquesta todo el flujo ETL
- **sql/create_tables.sql**: DDL (CREATE TABLE, relaciones FK, índices) + consultas analíticas para validación y análisis

## Requisitos

- Python 3.8+
- PostgreSQL (base de datos `amie_db` ya creada con las tablas)
- pip (gestor de paquetes Python)

## Configuración

### 1. Instalar dependencias

```bash
cd practicum_datos
pip install -r requirements.txt
```

### 2. Configurar credenciales en .env

Abre el archivo `.env` y reemplaza `tu_password_aqui` con tu contraseña de PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=amie_db
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_REAL
```

⚠️ **Importante**: No subas el archivo `.env` a control de versiones (agrégalo a `.gitignore`)

## Ejecución

```bash
python etl/pipeline.py
```

El script realizará automáticamente:
1. ✓ Lectura del archivo Excel
2. ✓ Creación de dimensiones y tabla de hechos
3. ✓ Conexión a PostgreSQL
4. ✓ Inserción de datos por lotes (1000 registros a la vez)
5. ✓ Mostrar resumen final

## Modelo relacional

### dim_ubicacion
Datos geográficos únicos (provincias, cantones, parroquias, zonas)

**Campos principales**:
- `id_ubicacion` (PK)
- `provincia`, `cod_provincia`
- `canton`, `cod_canton`
- `parroquia`, `cod_parroquia`
- `zona`, `regimen_escolar`

### dim_institucion
Datos de las instituciones educativas (escuelas, colegios, etc.)

**Campos principales**:
- `cod_amie` (PK) — Código único AMIE
- `nombre_institucion`
- `tipo_educacion`, `sostenimiento`
- `area`, `jurisdiccion`
- `id_ubicacion` (FK → dim_ubicacion)

### fact_matricula
Tabla de hechos con matrícula por año lectivo

**Campos principales**:
- `id_matricula` (PK)
- `anio_lectivo`
- `cod_amie` (FK → dim_institucion)
- `estudiantes_femenino`, `estudiantes_masculino`, `total_estudiantes`
- `docentes_femenino`, `docentes_masculino`, `total_docentes`
- `ratio_est_docente` — Relación estudiantes/docentes

## Fuente de datos

Dataset AMIE — Registro Administrativo Histórico 2009-2025 del Ministerio de Educación del Ecuador

Archivo: `registro-administrativo-historico_2009-2024-inicio.xlsx`

**Estructura del archivo:**
- Hoja 1: "VERDADEDRO" - 290,313 filas (datos 2009-2023)
- Hoja 2: "Historico_Inicio" - 442,717 filas (datos 2009-2025) ← Utilizada para la carga

## Cambios implementados

### extract.py — Renombrado de columnas y selección de hoja correcta
Se actualizó la función `extraer_datos()` para:
1. Leer la hoja **'Historico_Inicio'** (la hoja con datos completos 2009-2025)
2. Aplicar renombrado de columnas para compatibilidad con transform.py:
```python
df = df.rename(columns={
    "Anio_lectivo": "Periodo",
    "AMIE":         "Codigo_Institucion"
})
```

**Nota importante**: El Excel tiene 2 hojas:
- "VERDADEDRO": 290,313 filas (datos 2009-2023)
- "Historico_Inicio": 442,717 filas (datos 2009-2025) ← Usada ahora

### transform.py — Funciones completadas
✅ **construir_dim_institucion**: Merge con `dim_ubicacion` por columnas geográficas para obtener `id_ubicacion`, eliminación de duplicados y conversión a snake_case
✅ **construir_fact_matricula**: Cálculo de `ratio_est_docente` con manejo de división por cero (usando `np.where`)

## Resultados de ejecución

Pipeline ejecutado exitosamente con el dataset completo (2009-2025):

| Tabla | Registros | Estado |
|-------|-----------|--------|
| dim_ubicacion | 1,690 | ✓ Insertados |
| dim_institucion | 31,531 | ✓ Insertados |
| fact_matricula | 322,602 | ✓ Insertados |

**Datos origen**: 322,602 filas × 27 columnas del archivo Excel histórico 2009-2025
**Cobertura**: 16 años escolares (2009-2010 hasta 2024-2025)

## Notas importantes

- **ON CONFLICT DO NOTHING**: Los INSERT están configurados para ignorar registros duplicados sin romper los datos existentes
- **Sin archivos intermedios**: Todos los datos fluyen directamente a PostgreSQL, sin pasos CSV intermedios
- **Sin consultas SQL generadas**: La lógica DDL (CREATE TABLE, ALTER TABLE) debe gestionarse directamente en pgAdmin o psql
- **Inserciones por lotes**: Se utilizan lotes de 1000 registros para optimizar el rendimiento
- **Manejo de NaN**: Los valores NaN se convierten a None para compatibilidad con PostgreSQL
- **Ratio estudiantes/docentes**: Se redondea a 1 decimal y devuelve None cuando total_docentes es 0
