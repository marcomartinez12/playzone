/**
 * Utilidades para formatear números y moneda
 */

/**
 * Formatea un número como moneda colombiana (COP)
 * Ejemplo: 100000 -> $100.000
 * @param {number} value - Valor a formatear
 * @param {boolean} includeDecimals - Si debe incluir decimales (default: false)
 * @returns {string} Valor formateado
 */
function formatCurrency(value, includeDecimals = false) {
    const num = parseFloat(value) || 0;

    const options = {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: includeDecimals ? 2 : 0,
        maximumFractionDigits: includeDecimals ? 2 : 0
    };

    return new Intl.NumberFormat('es-CO', options).format(num);
}

/**
 * Formatea un número con separadores de miles (sin símbolo de moneda)
 * Ejemplo: 100000 -> 100.000
 * @param {number} value - Valor a formatear
 * @param {boolean} includeDecimals - Si debe incluir decimales (default: false)
 * @returns {string} Valor formateado
 */
function formatNumber(value, includeDecimals = false) {
    const num = parseFloat(value) || 0;

    const options = {
        minimumFractionDigits: includeDecimals ? 2 : 0,
        maximumFractionDigits: includeDecimals ? 2 : 0
    };

    return new Intl.NumberFormat('es-CO', options).format(num);
}
