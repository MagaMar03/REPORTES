-- ============================================================================
-- SCRIPT DE OPTIMIZACIÓN: ÍNDICES PARA MEJORAR RENDIMIENTO
-- ============================================================================
-- Este script crea índices en la base de datos para acelerar las consultas
-- más frecuentes de la aplicación CODIGOweb.PY
--
-- EJECUCIÓN: Ejecutar este script en MySQL/MariaDB antes de usar la aplicación
-- Tiempo estimado: 1-5 minutos dependiendo del tamaño de las tablas
-- ============================================================================

USE mi_base;

-- ============================================================================
-- TABLA: fiscalizaciones1 (OF - Órdenes de Fiscalización)
-- ============================================================================

-- Índice para filtros por Estado (muy usado en COUNT y WHERE)
CREATE INDEX IF NOT EXISTS idx_estado ON fiscalizaciones1(Estado);

-- Índice para filtros por COD_TIPACT (usado en gráficos determinativas/no determinativas)
CREATE INDEX IF NOT EXISTS idx_cod_tipact ON fiscalizaciones1(COD_TIPACT);

-- Índice para filtros por Anio_Termino (muy usado en filtros de año)
CREATE INDEX IF NOT EXISTS idx_anio_termino ON fiscalizaciones1(Anio_Termino);

-- Índice para filtros por Anio_Emis (usado en filtros de año de emisión)
CREATE INDEX IF NOT EXISTS idx_anio_emis ON fiscalizaciones1(Anio_Emis);

-- Índice compuesto para consultas frecuentes (Estado + COD_TIPACT + Anio_Termino)
CREATE INDEX IF NOT EXISTS idx_estado_tipact_anio ON fiscalizaciones1(Estado, COD_TIPACT, Anio_Termino);

-- Índice para NOMBRE_SUPERVISOR (usado en GROUP BY para gráficos)
CREATE INDEX IF NOT EXISTS idx_nombre_supervisor ON fiscalizaciones1(NOMBRE_SUPERVISOR);

-- Índice para NUM_ORD_FI (clave primaria probable, verificar)
CREATE INDEX IF NOT EXISTS idx_num_ord_fi ON fiscalizaciones1(NUM_ORD_FI);

-- ⚡ CRÍTICO: Índice para NUM_DOCSEL (usado en JOINs con detracciones y mypes)
-- Este índice es MUY IMPORTANTE para el dashboard de Control Saldo Detracciones
CREATE INDEX IF NOT EXISTS idx_num_docsel ON fiscalizaciones1(NUM_DOCSEL);

-- Índice para des_cod (usado en filtros de detracciones)
CREATE INDEX IF NOT EXISTS idx_des_cod ON fiscalizaciones1(des_cod);

-- ============================================================================
-- TABLA: fiscalizaciones2 (OFR - Recaudación)
-- ============================================================================

-- Índices similares para fiscalizaciones2
CREATE INDEX IF NOT EXISTS idx_f2_estado ON fiscalizaciones2(Estado);
CREATE INDEX IF NOT EXISTS idx_f2_cod_tipact ON fiscalizaciones2(COD_TIPACT);
CREATE INDEX IF NOT EXISTS idx_f2_anio ON fiscalizaciones2(Anio_Emis);

-- ============================================================================
-- TABLA: fiscalizaciones3 (AIs - Acciones Inductivas)
-- ============================================================================

-- Índices para fiscalizaciones3
CREATE INDEX IF NOT EXISTS idx_f3_estado ON fiscalizaciones3(Estado);
CREATE INDEX IF NOT EXISTS idx_f3_sip ON fiscalizaciones3(SIP_DESCRIPCION);

-- ============================================================================
-- TABLA: fiscalizaciones4 (DTR - Detracciones)
-- ⚡ CRÍTICO para Control Saldo Detracciones
-- ============================================================================

-- Índices para fiscalizaciones4
CREATE INDEX IF NOT EXISTS idx_f4_estado ON fiscalizaciones4(Estado);

-- ⚡ CRÍTICO: Índice para num_ruc (usado en JOINs con fiscalizaciones1)
-- Este índice es FUNDAMENTAL para el dashboard de Control Saldo Detracciones
CREATE INDEX IF NOT EXISTS idx_f4_num_ruc ON fiscalizaciones4(num_ruc);

-- Índice para mto_saldo (usado en agregaciones SUM)
CREATE INDEX IF NOT EXISTS idx_f4_mto_saldo ON fiscalizaciones4(mto_saldo);

-- ============================================================================
-- TABLA: fiscalizaciones5 (AIR - Recaudación)
-- ============================================================================

-- Índices para fiscalizaciones5
CREATE INDEX IF NOT EXISTS idx_f5_estado ON fiscalizaciones5(Estado);
CREATE INDEX IF NOT EXISTS idx_f5_sip ON fiscalizaciones5(SIP_DESCRIPCION);

-- ============================================================================
-- TABLA: mypes
-- ⚡ CRÍTICO para Control Saldo Detracciones (cruce con padrón MYPE)
-- ============================================================================

-- ⚡ CRÍTICO: Índice para ruc (usado en JOINs con fiscalizaciones1)
-- Este índice es FUNDAMENTAL para el cruce con padrón MYPE
CREATE INDEX IF NOT EXISTS idx_mypes_ruc ON mypes(ruc);

-- ============================================================================
-- ANÁLISIS Y OPTIMIZACIÓN DE TABLAS
-- ============================================================================

-- Analizar tablas para actualizar estadísticas
ANALYZE TABLE fiscalizaciones1;
ANALYZE TABLE fiscalizaciones2;
ANALYZE TABLE fiscalizaciones3;
ANALYZE TABLE fiscalizaciones4;
ANALYZE TABLE fiscalizaciones5;
ANALYZE TABLE mypes;

-- Optimizar tablas para desfragmentar
OPTIMIZE TABLE fiscalizaciones1;
OPTIMIZE TABLE fiscalizaciones2;
OPTIMIZE TABLE fiscalizaciones3;
OPTIMIZE TABLE fiscalizaciones4;
OPTIMIZE TABLE fiscalizaciones5;
OPTIMIZE TABLE mypes;

-- ============================================================================
-- VERIFICACIÓN DE ÍNDICES CREADOS
-- ============================================================================

-- Ver todos los índices de fiscalizaciones1
SHOW INDEX FROM fiscalizaciones1;

-- ============================================================================
-- NOTAS IMPORTANTES
-- ============================================================================
-- 1. Ejecutar este script en horario de bajo uso si las tablas son grandes
-- 2. Los índices mejoran SELECT pero pueden hacer más lentos los INSERT/UPDATE
-- 3. Monitorear el tamaño de la base de datos después de crear índices
-- 4. Si alguna columna no existe en tu base, comenta esa línea
-- ============================================================================

SELECT 'Índices creados exitosamente! ✅' as Mensaje;
