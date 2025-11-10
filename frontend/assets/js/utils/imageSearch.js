// ============================================
// BÚSQUEDA AUTOMÁTICA DE IMÁGENES
// ============================================

/**
 * Buscar múltiples imágenes en RAWG API (para videojuegos)
 * @param {string} nombreProducto - Nombre del producto
 * @param {string} categoria - Categoría del producto
 * @returns {Promise<Array>} - Array de objetos con url y nombre
 */
async function buscarImagenesMultiples(nombreProducto, categoria) {
    // Si es consola o accesorio, usar Serper
    if (categoria === 'consola' || categoria === 'accesorio') {
        return await buscarImagenesSerper(nombreProducto, categoria);
    }

    // Para videojuegos, usar RAWG
    if (!RAWG_API_KEY || RAWG_API_KEY === 'TU_API_KEY_AQUI') {
        console.warn('RAWG API key no configurada correctamente');
        return [];
    }

    try {
        // Limpiar el nombre del producto para la búsqueda
        const searchQuery = limpiarNombreParaBusqueda(nombreProducto);

        // Buscar en RAWG API - obtener hasta 5 resultados
        const url = `${RAWG_API_URL}/games?key=${RAWG_API_KEY}&search=${encodeURIComponent(searchQuery)}&page_size=5`;

        const response = await fetch(url);

        if (!response.ok) {
            console.warn('Error en RAWG API:', response.status);
            return [];
        }

        const data = await response.json();

        // Retornar array de opciones de imágenes
        if (data.results && data.results.length > 0) {
            return data.results
                .filter(game => game.background_image) // Solo juegos con imagen
                .map(game => ({
                    url: game.background_image,
                    nombre: game.name,
                    relevancia: game.rating || 0
                }))
                .sort((a, b) => b.relevancia - a.relevancia); // Ordenar por rating
        }

        return [];
    } catch (error) {
        console.error('Error al buscar imágenes:', error);
        return [];
    }
}

/**
 * Buscar imágenes usando Serper.dev (para consolas y accesorios)
 * @param {string} nombreProducto - Nombre del producto
 * @param {string} categoria - Categoría del producto
 * @returns {Promise<Array>} - Array de objetos con url y nombre
 */
async function buscarImagenesSerper(nombreProducto, categoria) {
    if (!SERPER_API_KEY || SERPER_API_KEY === 'TU_API_KEY_AQUI') {
        console.warn('Serper API key no configurada correctamente');
        return [];
    }

    try {
        // Construir query de búsqueda
        const query = categoria === 'consola'
            ? `${nombreProducto} gaming console`
            : `${nombreProducto} gaming accessory`;

        const response = await fetch(SERPER_API_URL, {
            method: 'POST',
            headers: {
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                q: query,
                num: 5
            })
        });

        if (!response.ok) {
            console.warn('Error en Serper API:', response.status);
            return [];
        }

        const data = await response.json();

        // Retornar array de imágenes
        if (data.images && data.images.length > 0) {
            return data.images.map((img, index) => ({
                url: img.imageUrl,
                nombre: img.title || `${nombreProducto} ${index + 1}`,
                relevancia: index
            }));
        }

        return [];
    } catch (error) {
        console.error('Error al buscar imágenes con Serper:', error);
        return [];
    }
}

/**
 * Limpiar nombre del producto para mejorar la búsqueda
 * @param {string} nombre - Nombre del producto
 * @returns {string} - Nombre limpio
 */
function limpiarNombreParaBusqueda(nombre) {
    // Remover palabras comunes que interfieren con la búsqueda
    let limpio = nombre.toLowerCase();

    // Remover palabras como "juego", "videojuego", "para", etc.
    const palabrasRemover = ['juego', 'videojuego', 'para', 'de', 'el', 'la', 'los', 'las'];
    palabrasRemover.forEach(palabra => {
        limpio = limpio.replace(new RegExp(`\\b${palabra}\\b`, 'g'), '');
    });

    // Limpiar espacios extras
    limpio = limpio.trim().replace(/\s+/g, ' ');

    return limpio;
}

/**
 * Obtener imagen placeholder según categoría
 * @param {string} categoria - Categoría del producto
 * @returns {string} - URL de imagen placeholder
 */
function obtenerImagenPlaceholder(categoria) {
    const placeholders = {
        'consola': 'https://images.unsplash.com/photo-1486401899868-0e435ed85128?w=400',
        'juego': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400',
        'accesorio': 'https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=400'
    };

    return placeholders[categoria] || 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400';
}

/**
 * Obtener URL de imagen para un producto
 * Prioridad: URL manual > Búsqueda automática > Placeholder
 * @param {string} nombreProducto - Nombre del producto
 * @param {string} categoria - Categoría del producto
 * @param {string} urlManual - URL manual (opcional)
 * @returns {Promise<string>} - URL de la imagen
 */
async function obtenerImagenProducto(nombreProducto, categoria, urlManual = '') {
    // 1. Si hay URL manual, usarla
    if (urlManual && urlManual.trim() !== '') {
        return urlManual.trim();
    }

    // 2. Intentar búsqueda automática solo para juegos y consolas
    if (categoria === 'juego' || categoria === 'consola') {
        const imagenAutomatica = await buscarImagenAutomatica(nombreProducto, categoria);
        if (imagenAutomatica) {
            return imagenAutomatica;
        }
    }

    // 3. Usar placeholder por categoría
    return obtenerImagenPlaceholder(categoria);
}
