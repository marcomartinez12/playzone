-- Productos adicionales
INSERT INTO productos (codigo, nombre, categoria, precio, cantidad, descripcion, imagen_url) VALUES
('VJ-PS5-001', 'God of War Ragnarok', 'videojuego', 250000, 15, 'Aventura mitologica', 'https://via.placeholder.com/150'),
('VJ-PS5-002', 'Horizon Forbidden West', 'videojuego', 220000, 12, 'Mundo abierto', 'https://via.placeholder.com/150'),
('VJ-PS5-003', 'Spider-Man 2', 'videojuego', 280000, 10, 'Aventura superheroes', 'https://via.placeholder.com/150'),
('VJ-XB-001', 'Halo Infinite', 'videojuego', 210000, 14, 'Shooter', 'https://via.placeholder.com/150'),
('VJ-NS-001', 'Zelda Tears Kingdom', 'videojuego', 270000, 18, 'Aventura', 'https://via.placeholder.com/150'),
('VJ-NS-002', 'Mario Kart 8', 'videojuego', 220000, 25, 'Carreras', 'https://via.placeholder.com/150'),
('CON-007', 'PS5 Standard', 'consola', 2500000, 5, 'Consola Sony', 'https://via.placeholder.com/150'),
('CON-008', 'Xbox Series X', 'consola', 2400000, 6, 'Consola Microsoft', 'https://via.placeholder.com/150'),
('CON-009', 'Nintendo Switch', 'consola', 1800000, 10, 'Consola Nintendo', 'https://via.placeholder.com/150'),
('ACC-009', 'DualSense', 'accesorio', 280000, 30, 'Control PS5', 'https://via.placeholder.com/150'),
('ACC-010', 'Mouse RGB', 'accesorio', 180000, 22, 'Mouse gaming', 'https://via.placeholder.com/150'),
('ACC-011', 'Teclado RGB', 'accesorio', 320000, 18, 'Teclado mecanico', 'https://via.placeholder.com/150'),
('ACC-012', 'Headset', 'accesorio', 450000, 15, 'Audifonos gaming', 'https://via.placeholder.com/150'),
('ACC-013', 'Webcam HD', 'accesorio', 220000, 12, 'Camara streaming', 'https://via.placeholder.com/150'),
('ACC-014', 'Silla Gaming', 'accesorio', 850000, 6, 'Silla ergonomica', 'https://via.placeholder.com/150');

-- Insertar venta y obtener su ID
DO $$
DECLARE
    venta_id1 INT;
    venta_id2 INT;
    venta_id3 INT;
BEGIN
    -- Venta 1
    INSERT INTO ventas (id_usuario, id_cliente, total)
    VALUES (2, 64, 470000) RETURNING id_venta INTO venta_id1;

    INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario) VALUES
    (venta_id1, 7, 1, 250000),
    (venta_id1, 8, 1, 220000);

    -- Venta 2
    INSERT INTO ventas (id_usuario, id_cliente, total)
    VALUES (2, 65, 280000) RETURNING id_venta INTO venta_id2;

    INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario) VALUES
    (venta_id2, 16, 1, 280000);

    -- Venta 3
    INSERT INTO ventas (id_usuario, id_cliente, total)
    VALUES (2, 66, 2500000) RETURNING id_venta INTO venta_id3;

    INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario) VALUES
    (venta_id3, 13, 1, 2500000);
END $$;

-- Servicios
INSERT INTO servicios (id_usuario, id_cliente, consola, descripcion, estado, costo) VALUES
(2, 70, 'PlayStation 4', 'No enciende', 'En reparacion', 150000),
(2, 71, 'Xbox One', 'Lector danado', 'En reparacion', 180000),
(2, 72, 'Nintendo Switch', 'Pantalla rota', 'Listo', 250000),
(2, 73, 'PS5', 'Sobrecalentamiento', 'En reparacion', 200000),
(2, 74, 'Xbox Series S', 'No WiFi', 'Listo', 120000);
