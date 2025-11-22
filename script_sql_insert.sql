-- =============================================
-- SCRIPT DE DATOS DE PRUEBA - SISTEMA LOGICO
-- =============================================
-- Base de datos: MySQL 8.0
-- Proyecto: LogiCo - Sistema de Gestión Logística
-- Empresa: Discopro Ltda.
-- Cliente: Cruz Verde
-- =============================================

-- Desactivar restricciones de claves foráneas temporalmente
SET FOREIGN_KEY_CHECKS = 0;

-- =============================================
-- 1. LIMPIAR TABLAS EXISTENTES (OPCIONAL)
-- =============================================
/*
TRUNCATE TABLE movimiento_reenvio;
TRUNCATE TABLE movimiento_traslado;
TRUNCATE TABLE movimiento_receta;
TRUNCATE TABLE movimiento_directo;
TRUNCATE TABLE bitacora_movimiento;
TRUNCATE TABLE movimiento;
TRUNCATE TABLE estados_movimiento;
TRUNCATE TABLE asignacion_farmacia;
TRUNCATE TABLE asignacion_moto;
TRUNCATE TABLE motorista;
TRUNCATE TABLE moto;
TRUNCATE TABLE farmacia;
*/

-- =============================================
-- 2. INSERTAR FARMACIAS (10 registros)
-- =============================================
INSERT INTO farmacia (IdFarmacia, nombre, direccion, comuna, provincia, region, apertura, cierre, telefono, latitud, longitud, activo, creado_por_id, fecha_creacion, modificado_por_id, fecha_modificacion) VALUES
-- Santiago Centro
('FARM001', 'Cruz Verde Ahumada', 'Av. Bernardo O''Higgins 123', 'Santiago', 'Santiago', 'Metropolitana', '08:00:00', '22:00:00', '+56223456789', -33.450000, -70.666667, 1, 1, NOW(), 1, NOW()),
('FARM002', 'Cruz Verde Moneda', 'Calle Moneda 456', 'Santiago', 'Santiago', 'Metropolitana', '08:30:00', '21:30:00', '+56223456790', -33.437869, -70.650450, 1, 1, NOW(), 1, NOW()),

-- Providencia
('FARM003', 'Cruz Verde Providencia', 'Av. Providencia 789', 'Providencia', 'Santiago', 'Metropolitana', '09:00:00', '22:00:00', '+56223456791', -33.431580, -70.623350, 1, 1, NOW(), 1, NOW()),
('FARM004', 'Cruz Verde Los Leones', 'Av. Los Leones 101', 'Providencia', 'Santiago', 'Metropolitana', '08:00:00', '21:00:00', '+56223456792', -33.425000, -70.610000, 1, 1, NOW(), 1, NOW()),

-- Las Condes
('FARM005', 'Cruz Verde Apoquindo', 'Av. Apoquindo 234', 'Las Condes', 'Santiago', 'Metropolitana', '08:30:00', '22:30:00', '+56223456793', -33.408330, -70.575000, 1, 1, NOW(), 1, NOW()),
('FARM006', 'Cruz Verde Alonso de Córdova', 'Av. Alonso de Córdova 567', 'Las Condes', 'Santiago', 'Metropolitana', '09:00:00', '21:00:00', '+56223456794', -33.415000, -70.585000, 1, 1, NOW(), 1, NOW()),

-- Ñuñoa
('FARM007', 'Cruz Verde Irarrázaval', 'Av. Irarrázaval 890', 'Ñuñoa', 'Santiago', 'Metropolitana', '08:00:00', '22:00:00', '+56223456795', -33.455000, -70.590000, 1, 1, NOW(), 1, NOW()),
('FARM008', 'Cruz Verde Plaza Ñuñoa', 'Av. José Pedro Alessandri 112', 'Ñuñoa', 'Santiago', 'Metropolitana', '08:30:00', '21:30:00', '+56223456796', -33.460000, -70.595000, 1, 1, NOW(), 1, NOW()),

-- Maipú
('FARM009', 'Cruz Verde Maipú Centro', 'Av. Pajaritos 1314', 'Maipú', 'Santiago', 'Metropolitana', '08:00:00', '22:00:00', '+56223456797', -33.510000, -70.760000, 1, 1, NOW(), 1, NOW()),
('FARM010', 'Cruz Verde Plaza Maipú', 'Av. Cinco de Abril 1516', 'Maipú', 'Santiago', 'Metropolitana', '09:00:00', '21:00:00', '+56223456798', -33.520000, -70.770000, 1, 1, NOW(), 1, NOW());

-- =============================================
-- 3. INSERTAR MOTOS (20 registros)
-- =============================================
INSERT INTO moto (patente, marca, modelo, año, color, numChasis, motor, propietario, permisoCirculacion, seguro, revisionTecnica, activo, creado_por_id, fecha_creacion, modificado_por_id, fecha_modificacion) VALUES
-- Motos con documentación VIGENTE (12 motos)
('AB123CD', 'Yamaha', 'NMAX', 2023, 'Negro', 'YAM123456789', 'YMZ123456', 'EMPRESA', 'permiso_vigente_1.pdf', 'seguro_vigente_1.pdf', 'revision_vigente_1.pdf', 1, 1, NOW(), 1, NOW()),
('CD456EF', 'Honda', 'PCX', 2023, 'Blanco', 'HON123456789', 'HND123456', 'EMPRESA', 'permiso_vigente_2.pdf', 'seguro_vigente_2.pdf', 'revision_vigente_2.pdf', 1, 1, NOW(), 1, NOW()),
('EF789GH', 'Yamaha', 'NMAX', 2022, 'Azul', 'YAM987654321', 'YMZ987654', 'EMPRESA', 'permiso_vigente_3.pdf', 'seguro_vigente_3.pdf', 'revision_vigente_3.pdf', 1, 1, NOW(), 1, NOW()),
('GH012IJ', 'Honda', 'PCX', 2022, 'Rojo', 'HON987654321', 'HND987654', 'EMPRESA', 'permiso_vigente_4.pdf', 'seguro_vigente_4.pdf', 'revision_vigente_4.pdf', 1, 1, NOW(), 1, NOW()),
('IJ345KL', 'Suzuki', 'Address', 2023, 'Gris', 'SUZ123456789', 'SUZ123456', 'EMPRESA', 'permiso_vigente_5.pdf', 'seguro_vigente_5.pdf', 'revision_vigente_5.pdf', 1, 1, NOW(), 1, NOW()),
('KL678MN', 'Yamaha', 'NMAX', 2023, 'Negro', 'YAM456789123', 'YMZ456789', 'EMPRESA', 'permiso_vigente_6.pdf', 'seguro_vigente_6.pdf', 'revision_vigente_6.pdf', 1, 1, NOW(), 1, NOW()),
('MN901OP', 'Honda', 'PCX', 2022, 'Blanco', 'HON456789123', 'HND456789', 'EMPRESA', 'permiso_vigente_7.pdf', 'seguro_vigente_7.pdf', 'revision_vigente_7.pdf', 1, 1, NOW(), 1, NOW()),
('OP234QR', 'Yamaha', 'NMAX', 2023, 'Azul', 'YAM789123456', 'YMZ789123', 'EMPRESA', 'permiso_vigente_8.pdf', 'seguro_vigente_8.pdf', 'revision_vigente_8.pdf', 1, 1, NOW(), 1, NOW()),
('QR567ST', 'Honda', 'PCX', 2022, 'Rojo', 'HON789123456', 'HND789123', 'EMPRESA', 'permiso_vigente_9.pdf', 'seguro_vigente_9.pdf', 'revision_vigente_9.pdf', 1, 1, NOW(), 1, NOW()),
('ST890UV', 'Suzuki', 'Address', 2023, 'Gris', 'SUZ456789123', 'SUZ456789', 'EMPRESA', 'permiso_vigente_10.pdf', 'seguro_vigente_10.pdf', 'revision_vigente_10.pdf', 1, 1, NOW(), 1, NOW()),
('UV123WX', 'Yamaha', 'NMAX', 2023, 'Negro', 'YAM159753456', 'YMZ159753', 'EMPRESA', 'permiso_vigente_11.pdf', 'seguro_vigente_11.pdf', 'revision_vigente_11.pdf', 1, 1, NOW(), 1, NOW()),
('WX456YZ', 'Honda', 'PCX', 2022, 'Blanco', 'HON159753456', 'HND159753', 'EMPRESA', 'permiso_vigente_12.pdf', 'seguro_vigente_12.pdf', 'revision_vigente_12.pdf', 1, 1, NOW(), 1, NOW()),

-- Motos con documentación VENCIDA (8 motos)
('YZ789AB', 'Yamaha', 'NMAX', 2021, 'Azul', 'YAM357159456', 'YMZ357159', 'EMPRESA', 'permiso_vencido_1.pdf', 'seguro_vencido_1.pdf', 'revision_vencida_1.pdf', 1, 1, NOW(), 1, NOW()),
('BC012CD', 'Honda', 'PCX', 2021, 'Rojo', 'HON357159456', 'HND357159', 'EMPRESA', 'permiso_vencido_2.pdf', 'seguro_vencido_2.pdf', 'revision_vencida_2.pdf', 1, 1, NOW(), 1, NOW()),
('DE345EF', 'Suzuki', 'Address', 2021, 'Gris', 'SUZ357159456', 'SUZ357159', 'EMPRESA', 'permiso_vencido_3.pdf', 'seguro_vencido_3.pdf', 'revision_vencida_3.pdf', 1, 1, NOW(), 1, NOW()),
('FG678GH', 'Yamaha', 'NMAX', 2020, 'Negro', 'YAM753159456', 'YMZ753159', 'EMPRESA', 'permiso_vencido_4.pdf', 'seguro_vencido_4.pdf', 'revision_vencida_4.pdf', 1, 1, NOW(), 1, NOW()),
('HI901IJ', 'Honda', 'PCX', 2020, 'Blanco', 'HON753159456', 'HND753159', 'EMPRESA', 'permiso_vencido_5.pdf', 'seguro_vencido_5.pdf', 'revision_vencida_5.pdf', 1, 1, NOW(), 1, NOW()),
('JK234KL', 'Yamaha', 'NMAX', 2021, 'Azul', 'YAM852456123', 'YMZ852456', 'EMPRESA', 'permiso_vencido_6.pdf', 'seguro_vencido_6.pdf', 'revision_vencida_6.pdf', 1, 1, NOW(), 1, NOW()),
('LM567MN', 'Honda', 'PCX', 2021, 'Rojo', 'HON852456123', 'HND852456', 'EMPRESA', 'permiso_vencido_7.pdf', 'seguro_vencido_7.pdf', 'revision_vencida_7.pdf', 1, 1, NOW(), 1, NOW()),
('NO890OP', 'Suzuki', 'Address', 2020, 'Gris', 'SUZ852456123', 'SUZ852456', 'EMPRESA', 'permiso_vencido_8.pdf', 'seguro_vencido_8.pdf', 'revision_vencida_8.pdf', 1, 1, NOW(), 1, NOW());

-- =============================================
-- 4. INSERTAR MOTORISTAS (15 registros)
-- =============================================
INSERT INTO motorista (rut, nombre, apellidoPaterno, apellidoMaterno, fechaNacimiento, direccion, comuna, provincia, region, telefono, correo, moto, archivo, fechaUltControl, fechaControl, fechaVencimiento, parentesco, telefonoEmergencia, nombreContacto, apellidoContacto, direccionContacto, activo, creado_por_id, fecha_creacion, modificado_por_id, fecha_modificacion) VALUES
-- Motoristas ACTIVOS (12 motoristas)
('12345678-9', 'Juan Carlos', 'Pérez', 'González', '1990-05-15', 'Av. Matta 123', 'Santiago', 'Santiago', 'Metropolitana', '+56912345678', 'juan.perez@logico.com', 'NO', 'licencia_juan.pdf', '2024-01-15', '2024-07-15', '2025-01-15', 'PADRE', '+56987654321', 'Carlos', 'Pérez', 'Av. Matta 123', 1, 1, NOW(), 1, NOW()),
('23456789-0', 'María José', 'López', 'Martínez', '1992-08-20', 'Av. Providencia 456', 'Providencia', 'Santiago', 'Metropolitana', '+56923456789', 'maria.lopez@logico.com', 'NO', 'licencia_maria.pdf', '2024-02-20', '2024-08-20', '2025-02-20', 'MADRE', '+56976543210', 'Ana', 'López', 'Av. Providencia 456', 1, 1, NOW(), 1, NOW()),
('34567890-1', 'Pedro Antonio', 'García', 'Silva', '1988-12-10', 'Av. Las Condes 789', 'Las Condes', 'Santiago', 'Metropolitana', '+56934567890', 'pedro.garcia@logico.com', 'NO', 'licencia_pedro.pdf', '2024-03-10', '2024-09-10', '2025-03-10', 'HERMANO', '+56965432109', 'Luis', 'García', 'Av. Las Condes 789', 1, 1, NOW(), 1, NOW()),
('45678901-2', 'Ana Isabel', 'Rodríguez', 'Fernández', '1991-03-25', 'Av. Irarrázaval 101', 'Ñuñoa', 'Santiago', 'Metropolitana', '+56945678901', 'ana.rodriguez@logico.com', 'NO', 'licencia_ana.pdf', '2024-01-25', '2024-07-25', '2025-01-25', 'HERMANA', '+56954321098', 'Carmen', 'Rodríguez', 'Av. Irarrázaval 101', 1, 1, NOW(), 1, NOW()),
('56789012-3', 'Carlos Andrés', 'Martínez', 'Hernández', '1989-07-30', 'Av. Pajaritos 112', 'Maipú', 'Santiago', 'Metropolitana', '+56956789012', 'carlos.martinez@logico.com', 'NO', 'licencia_carlos.pdf', '2024-04-30', '2024-10-30', '2025-04-30', 'PADRE', '+56943210987', 'Andrés', 'Martínez', 'Av. Pajaritos 112', 1, 1, NOW(), 1, NOW()),
('67890123-4', 'Laura Patricia', 'González', 'Ramírez', '1993-11-05', 'Av. Apoquindo 131', 'Las Condes', 'Santiago', 'Metropolitana', '+56967890123', 'laura.gonzalez@logico.com', 'NO', 'licencia_laura.pdf', '2024-02-05', '2024-08-05', '2025-02-05', 'MADRE', '+56932109876', 'Patricia', 'González', 'Av. Apoquindo 131', 1, 1, NOW(), 1, NOW()),
('78901234-5', 'Roberto José', 'Sánchez', 'Díaz', '1990-09-18', 'Av. Los Leones 415', 'Providencia', 'Santiago', 'Metropolitana', '+56978901234', 'roberto.sanchez@logico.com', 'NO', 'licencia_roberto.pdf', '2024-03-18', '2024-09-18', '2025-03-18', 'HERMANO', '+56921098765', 'José', 'Sánchez', 'Av. Los Leones 415', 1, 1, NOW(), 1, NOW()),
('89012345-6', 'Claudia Andrea', 'Torres', 'Morales', '1994-02-14', 'Av. José Pedro Alessandri 167', 'Ñuñoa', 'Santiago', 'Metropolitana', '+56989012345', 'claudia.torres@logico.com', 'NO', 'licencia_claudia.pdf', '2024-01-14', '2024-07-14', '2025-01-14', 'HERMANA', '+56910987654', 'Andrea', 'Torres', 'Av. José Pedro Alessandri 167', 1, 1, NOW(), 1, NOW()),
('90123456-7', 'Miguel Ángel', 'Castillo', 'Vargas', '1987-06-22', 'Av. Cinco de Abril 189', 'Maipú', 'Santiago', 'Metropolitana', '+56990123456', 'miguel.castillo@logico.com', 'NO', 'licencia_miguel.pdf', '2024-04-22', '2024-10-22', '2025-04-22', 'PADRE', '+56909876543', 'Ángel', 'Castillo', 'Av. Cinco de Abril 189', 1, 1, NOW(), 1, NOW()),
('11223344-5', 'Fernanda Alejandra', 'Castro', 'Rojas', '1992-04-08', 'Av. Bernardo O''Higgins 210', 'Santiago', 'Santiago', 'Metropolitana', '+56911223344', 'fernanda.castro@logico.com', 'NO', 'licencia_fernanda.pdf', '2024-02-08', '2024-08-08', '2025-02-08', 'MADRE', '+56998765432', 'Alejandra', 'Castro', 'Av. Bernardo O''Higgins 210', 1, 1, NOW(), 1, NOW()),
('22334455-6', 'Diego Alejandro', 'Fuentes', 'Mendoza', '1991-10-12', 'Calle Moneda 311', 'Santiago', 'Santiago', 'Metropolitana', '+56922334455', 'diego.fuentes@logico.com', 'NO', 'licencia_diego.pdf', '2024-03-12', '2024-09-12', '2025-03-12', 'HERMANO', '+56987654321', 'Alejandro', 'Fuentes', 'Calle Moneda 311', 1, 1, NOW(), 1, NOW()),
('33445566-7', 'Camila Ignacia', 'Ortega', 'Pizarro', '1993-12-03', 'Av. Providencia 512', 'Providencia', 'Santiago', 'Metropolitana', '+56933445566', 'camila.ortega@logico.com', 'NO', 'licencia_camila.pdf', '2024-01-03', '2024-07-03', '2025-01-03', 'HERMANA', '+56976543210', 'Ignacia', 'Ortega', 'Av. Providencia 512', 1, 1, NOW(), 1, NOW()),

-- Motoristas INACTIVOS (3 motoristas)
('44556677-8', 'Patricio Andrés', 'Navarro', 'Salazar', '1986-08-17', 'Av. Las Condes 613', 'Las Condes', 'Santiago', 'Metropolitana', '+56944556677', 'patricio.navarro@logico.com', 'NO', 'licencia_patricio.pdf', '2024-02-17', '2024-08-17', '2025-02-17', 'PADRE', '+56965432109', 'Andrés', 'Navarro', 'Av. Las Condes 613', 0, 1, NOW(), 1, NOW()),
('55667788-9', 'Valentina Paz', 'Miranda', 'López', '1995-01-28', 'Av. Irarrázaval 714', 'Ñuñoa', 'Santiago', 'Metropolitana', '+56955667788', 'valentina.miranda@logico.com', 'NO', 'licencia_valentina.pdf', '2024-03-28', '2024-09-28', '2025-03-28', 'MADRE', '+56954321098', 'Paz', 'Miranda', 'Av. Irarrázaval 714', 0, 1, NOW(), 1, NOW()),
('66778899-0', 'Francisco Javier', 'Sepúlveda', 'Cáceres', '1988-05-09', 'Av. Pajaritos 815', 'Maipú', 'Santiago', 'Metropolitana', '+56966778899', 'francisco.sepulveda@logico.com', 'NO', 'licencia_francisco.pdf', '2024-04-09', '2024-10-09', '2025-04-09', 'HERMANO', '+56943210987', 'Javier', 'Sepúlveda', 'Av. Pajaritos 815', 0, 1, NOW(), 1, NOW());