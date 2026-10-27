-- Modelo tipo estrella sencillo para poblar la vista vw_dashboard_ventas.
CREATE DATABASE IF NOT EXISTS MiTienda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE MiTienda;
CREATE TABLE IF NOT EXISTS dim_producto (producto_id INT AUTO_INCREMENT PRIMARY KEY, producto VARCHAR(100) NOT NULL, categoria VARCHAR(60) NOT NULL, UNIQUE KEY uq_producto (producto));
CREATE TABLE IF NOT EXISTS dim_metodo_pago (metodo_pago_id INT AUTO_INCREMENT PRIMARY KEY, medio_pago VARCHAR(60) NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS fact_ventas (venta_id BIGINT AUTO_INCREMENT PRIMARY KEY, fecha DATE NOT NULL, producto_id INT NOT NULL, metodo_pago_id INT NOT NULL, unidades INT NOT NULL, precio_unitario DECIMAL(12,2) NOT NULL, total DECIMAL(14,2) NOT NULL, CONSTRAINT fk_venta_producto FOREIGN KEY(producto_id) REFERENCES dim_producto(producto_id), CONSTRAINT fk_venta_pago FOREIGN KEY(metodo_pago_id) REFERENCES dim_metodo_pago(metodo_pago_id), INDEX ix_venta_fecha(fecha));
CREATE OR REPLACE VIEW vw_dashboard_ventas AS
SELECT f.fecha, p.producto, p.categoria, f.unidades, f.precio_unitario, f.total, m.medio_pago
FROM fact_ventas f JOIN dim_producto p ON p.producto_id=f.producto_id JOIN dim_metodo_pago m ON m.metodo_pago_id=f.metodo_pago_id;
-- Cargar ventas_demo.csv en el modelo requiere mapear productos y medios de pago a sus dimensiones,
-- luego insertar las filas en fact_ventas. Consulte LEEME.txt antes de reemplazar la fuente por la BD real.
