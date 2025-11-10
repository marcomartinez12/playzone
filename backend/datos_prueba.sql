-- ============================================================
-- DATOS DE PRUEBA EXTENSOS - 50+ REGISTROS
-- ============================================================

-- Insertar 20 clientes adicionales
INSERT INTO clientes (nombre, documento, telefono, email) VALUES
('Sofia Martinez', '1011121314', '3201234567', 'sofia.m@example.com'),
('Diego Torres', '1112131415', '3112345678', 'diego.t@example.com'),
('Valentina Ruiz', '1213141516', '3223456789', 'valentina.r@example.com'),
('Sebastian Gomez', '1314151617', '3134567890', 'sebastian.g@example.com'),
('Isabella Castro', '1415161718', '3045678901', 'isabella.c@example.com'),
('Mateo Vargas', '1516171819', '3156789012', 'mateo.v@example.com'),
('Camila Moreno', '1617181920', '3267890123', 'camila.m@example.com'),
('Lucas Herrera', '1718192021', '3178901234', 'lucas.h@example.com'),
('Mariana Jimenez', '1819202122', '3089012345', 'mariana.j@example.com'),
('Daniel Rojas', '1920212223', '3190123456', 'daniel.r@example.com'),
('Salome Mendez', '2021222324', '3201234560', 'salome.m@example.com'),
('Samuel Ortiz', '2122232425', '3112345670', 'samuel.o@example.com'),
('Gabriela Silva', '2223242526', '3223456780', 'gabriela.s@example.com'),
('Nicolas Ramirez', '2324252627', '3134567891', 'nicolas.r@example.com'),
('Lucia Fernandez', '2425262728', '3045678902', 'lucia.f@example.com'),
('Andres Sanchez', '2526272829', '3156789023', 'andres.s@example.com'),
('Emma Diaz', '2627282930', '3267890134', 'emma.d@example.com'),
('Felipe Garcia', '2728293031', '3178901245', 'felipe.g@example.com'),
('Antonella Lopez', '2829303132', '3089012356', 'antonella.l@example.com'),
('Martin Alvarez', '2930313233', '3190123467', 'martin.a@example.com');

-- Insertar 30 productos variados
INSERT INTO productos (codigo, nombre, categoria, precio, cantidad, descripcion, imagen_url) VALUES
-- Videojuegos PS5
('VJ-PS5-001', 'God of War Ragnarok', 'videojuego', 250000, 15, 'Aventura mitologica nordica', 'https://via.placeholder.com/150'),
('VJ-PS5-002', 'Horizon Forbidden West', 'videojuego', 220000, 12, 'Mundo abierto post-apocaliptico', 'https://via.placeholder.com/150'),
('VJ-PS5-003', 'Spider-Man 2', 'videojuego', 280000, 10, 'Aventura de superheroes', 'https://via.placeholder.com/150'),
('VJ-PS5-004', 'The Last of Us Part II', 'videojuego', 200000, 8, 'Survival horror', 'https://via.placeholder.com/150'),
('VJ-PS5-005', 'Ratchet & Clank', 'videojuego', 180000, 20, 'Plataformas y accion', 'https://via.placeholder.com/150'),

-- Videojuegos Xbox
('VJ-XB-001', 'Halo Infinite', 'videojuego', 210000, 14, 'Shooter de ciencia ficcion', 'https://via.placeholder.com/150'),
('VJ-XB-002', 'Forza Horizon 5', 'videojuego', 230000, 11, 'Carreras mundo abierto', 'https://via.placeholder.com/150'),
('VJ-XB-003', 'Starfield', 'videojuego', 260000, 9, 'RPG espacial', 'https://via.placeholder.com/150'),
('VJ-XB-004', 'Gears of War 5', 'videojuego', 190000, 16, 'Shooter tercera persona', 'https://via.placeholder.com/150'),

-- Videojuegos Nintendo Switch
('VJ-NS-001', 'Zelda Tears of Kingdom', 'videojuego', 270000, 18, 'Aventura y exploracion', 'https://via.placeholder.com/150'),
('VJ-NS-002', 'Mario Kart 8 Deluxe', 'videojuego', 220000, 25, 'Carreras multijugador', 'https://via.placeholder.com/150'),
('VJ-NS-003', 'Super Smash Bros', 'videojuego', 240000, 15, 'Pelea multijugador', 'https://via.placeholder.com/150'),
('VJ-NS-004', 'Animal Crossing', 'videojuego', 200000, 20, 'Simulacion de vida', 'https://via.placeholder.com/150'),
('VJ-NS-005', 'Pokemon Escarlata', 'videojuego', 230000, 12, 'RPG de captura', 'https://via.placeholder.com/150'),

-- Videojuegos PC
('VJ-PC-001', 'Elden Ring', 'videojuego', 180000, 22, 'RPG souls-like', 'https://via.placeholder.com/150'),
('VJ-PC-002', 'Cyberpunk 2077', 'videojuego', 160000, 10, 'RPG futurista', 'https://via.placeholder.com/150'),
('VJ-PC-003', 'Red Dead Redemption 2', 'videojuego', 170000, 14, 'Western mundo abierto', 'https://via.placeholder.com/150'),

-- Consolas
('CON-001', 'PlayStation 5 Standard', 'consola', 2500000, 5, 'Consola next-gen Sony', 'https://via.placeholder.com/150'),
('CON-002', 'PlayStation 5 Digital', 'consola', 2200000, 4, 'Version sin lector de discos', 'https://via.placeholder.com/150'),
('CON-003', 'Xbox Series X', 'consola', 2400000, 6, 'Consola Microsoft 4K', 'https://via.placeholder.com/150'),
('CON-004', 'Xbox Series S', 'consola', 1600000, 8, 'Version compacta Xbox', 'https://via.placeholder.com/150'),
('CON-005', 'Nintendo Switch OLED', 'consola', 1800000, 10, 'Switch con pantalla OLED', 'https://via.placeholder.com/150'),
('CON-006', 'Nintendo Switch Lite', 'consola', 1200000, 12, 'Version portatil', 'https://via.placeholder.com/150'),

-- Accesorios
('ACC-001', 'Control DualSense PS5', 'accesorio', 280000, 30, 'Control inalambrico PS5', 'https://via.placeholder.com/150'),
('ACC-002', 'Control Xbox Wireless', 'accesorio', 250000, 25, 'Control inalambrico Xbox', 'https://via.placeholder.com/150'),
('ACC-003', 'Joy-Con Nintendo Switch', 'accesorio', 350000, 20, 'Controles desmontables', 'https://via.placeholder.com/150'),
('ACC-004', 'Headset Pulse 3D', 'accesorio', 450000, 15, 'Audifonos gaming PS5', 'https://via.placeholder.com/150'),
('ACC-005', 'Teclado Mecanico RGB', 'accesorio', 320000, 18, 'Teclado gaming switches blue', 'https://via.placeholder.com/150'),
('ACC-006', 'Mouse Gaming RGB', 'accesorio', 180000, 22, 'Mouse 16000 DPI', 'https://via.placeholder.com/150'),
('ACC-007', 'Webcam HD 1080p', 'accesorio', 220000, 12, 'Camara para streaming', 'https://via.placeholder.com/150'),
('ACC-008', 'Silla Gaming Pro', 'accesorio', 850000, 6, 'Silla ergonomica reclinable', 'https://via.placeholder.com/150');

-- Insertar algunas ventas de prueba
INSERT INTO ventas (id_usuario, id_cliente, total) VALUES
(2, 4, 500000),
(2, 5, 280000),
(2, 6, 1800000),
(2, 7, 450000),
(2, 8, 730000);

-- Insertar detalles de ventas
INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario) VALUES
-- Venta 1
(1, 1, 1, 250000),
(1, 2, 1, 250000),
-- Venta 2
(2, 25, 1, 280000),
-- Venta 3
(3, 17, 1, 1800000),
-- Venta 4
(4, 28, 1, 450000),
-- Venta 5
(5, 9, 2, 220000),
(5, 29, 1, 320000);

-- Insertar servicios de reparacion
INSERT INTO servicios (id_usuario, id_cliente, consola, descripcion, estado, costo) VALUES
(2, 4, 'PlayStation 4', 'No enciende, posible fuente danada', 'En reparacion', 150000),
(2, 5, 'Xbox One', 'Lector de discos no funciona', 'En reparacion', 180000),
(2, 6, 'Nintendo Switch', 'Pantalla rota', 'Listo', 250000),
(2, 7, 'PlayStation 5', 'Sobrecalentamiento', 'En reparacion', 200000),
(2, 8, 'Xbox Series S', 'No conecta WiFi', 'Listo', 120000),
(2, 9, 'Nintendo Switch', 'Joy-Con con drift', 'Entregado', 80000),
(2, 10, 'PlayStation 4 Pro', 'Ruido excesivo ventilador', 'En reparacion', 100000),
(2, 11, 'Xbox One X', 'Error de actualizacion', 'Listo', 90000);
