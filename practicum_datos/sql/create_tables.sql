-- ==========================================
-- DDL PROYECTO AMIE
-- Orden: dim_ubicacion → dim_institucion → fact_matricula
-- ==========================================

DROP TABLE IF EXISTS fact_matricula;
DROP TABLE IF EXISTS dim_institucion;
DROP TABLE IF EXISTS dim_ubicacion;

-- TABLA 1
CREATE TABLE dim_ubicacion (
    id_ubicacion  SERIAL PRIMARY KEY,
    provincia     VARCHAR(100),
    cod_provincia VARCHAR(10),
    canton        VARCHAR(100),
    cod_canton    VARCHAR(10),
    parroquia     VARCHAR(100),
    cod_parroquia VARCHAR(10),
    zona          VARCHAR(20),
    regimen_escolar VARCHAR(50)
);

-- TABLA 2
CREATE TABLE dim_institucion (
    cod_amie           VARCHAR(20) PRIMARY KEY,
    nombre_institucion VARCHAR(200),
    tipo_educacion     VARCHAR(50),
    sostenimiento      VARCHAR(50),
    area               VARCHAR(50),
    jurisdiccion       VARCHAR(50),
    id_ubicacion       INT NOT NULL,
    CONSTRAINT fk_ubicacion
        FOREIGN KEY (id_ubicacion)
        REFERENCES dim_ubicacion(id_ubicacion)
);

-- TABLA 3
CREATE TABLE fact_matricula (
    id_matricula          SERIAL PRIMARY KEY,
    cod_amie              VARCHAR(20) NOT NULL,
    anio_lectivo          VARCHAR(30),
    estudiantes_femenino  INT DEFAULT 0,
    estudiantes_masculino INT DEFAULT 0,
    total_estudiantes     INT DEFAULT 0,
    docentes_femenino     INT DEFAULT 0,
    docentes_masculino    INT DEFAULT 0,
    total_docentes        INT DEFAULT 0,
    ratio_est_docente     NUMERIC(6,1),
    CONSTRAINT fk_institucion
        FOREIGN KEY (cod_amie)
        REFERENCES dim_institucion(cod_amie)
);