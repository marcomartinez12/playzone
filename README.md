# 🎮 PlayZone - Sistema de Gestión de Inventario

Sistema integral de gestión de inventario desarrollado para **Universidad Popular del Cesar**, especializado en la administración de videojuegos, consolas y accesorios.

---

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso del Sistema](#-uso-del-sistema)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Funcionalidades Implementadas](#-funcionalidades-implementadas)
- [API Endpoints](#-api-endpoints)
- [Contribución](#-contribución)

---

## ✨ Características Principales

### 🎯 Gestión de Inventario
- ✅ CRUD completo de productos (Consolas, Juegos, Accesorios)
- ✅ Búsqueda automática de imágenes con IA:
  - **Videojuegos:** RAWG API (base de datos especializada)
  - **Consolas y Accesorios:** Serper.dev (Google Images)
- ✅ Botón de búsqueda manual 🔍 para encontrar imágenes
- ✅ Alertas de stock bajo (< 10 unidades)
- ✅ Filtros avanzados por categoría, precio y stock
- ✅ Generación automática de códigos únicos

### 💰 Sistema de Ventas
- ✅ Carrito de compras interactivo
- ✅ Búsqueda de clientes por documento
- ✅ Registro automático de nuevos clientes
- ✅ Actualización automática de stock post-venta
- ✅ Historial completo de ventas

### 🔧 Gestión de Servicios
- ✅ Control de reparaciones de consolas
- ✅ Estados: En Reparación, Listo, Entregado
- ✅ Seguimiento de días en servicio
- ✅ Registro de clientes y costos

### 📊 Dashboard en Tiempo Real
- ✅ Total de productos en inventario
- ✅ Productos con stock bajo
- ✅ Ventas del día
- ✅ Servicios en reparación
- ✅ Ingresos del mes
- ✅ Producto más vendido
- ✅ Actualización automática sin refrescar

### 📱 Accesibilidad Móvil (RF-12)
- ✅ Diseño 100% responsive
- ✅ Touch targets optimizados (44x44px mínimo)
- ✅ Carrito colapsable en móviles
- ✅ Menú lateral adaptativo
- ✅ Meta tags para PWA

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido para construir APIs con Python. Validación automática de datos y documentación interactiva.
- **PostgreSQL** - Sistema de base de datos relacional robusto y escalable para almacenar productos, ventas, servicios y clientes.
- **JWT + Refresh Tokens** - Sistema de autenticación de doble token. Access tokens (30 min) para acceso y refresh tokens (30 días) para sesiones persistentes.
- **Bcrypt** - Hashing seguro de contraseñas con salt. Migración automática de contraseñas antiguas en texto plano.
- **ReportLab** - Generación profesional de reportes PDF con branding de PlayZone.
- **psycopg2** - Adaptador PostgreSQL para Python que permite ejecutar consultas SQL y obtener resultados como diccionarios.
- **CORS Middleware** - Permite que el frontend haga peticiones al backend desde diferentes puertos de forma segura.

### Frontend
- **HTML5 + CSS3** - Estructura y estilos puros sin preprocesadores. Diseño responsive adaptado a móviles y tablets.
- **JavaScript ES6+** - Lógica del cliente sin frameworks. Comunicación asíncrona con el backend vía Fetch API.
- **EventBus** - Sistema personalizado de eventos para comunicación desacoplada entre componentes (ej: Dashboard se actualiza cuando se crea un producto).
- **RAWG API** - Base de datos de +800,000 videojuegos con imágenes, descripciones y metadatos para búsqueda automática.
- **Serper API** - Servicio de búsqueda de Google Images para encontrar imágenes de consolas y accesorios gaming.

### Arquitectura
- **MVC** - Separación de capas: Models (datos), Views (interfaz), Controllers (lógica de negocio).
- **REST API** - Comunicación cliente-servidor mediante endpoints HTTP estándar (GET, POST, PUT, DELETE).
- **Event-Driven** - Actualización en tiempo real sin refrescar página usando eventos personalizados.
- **Puerto Único** - Backend sirve tanto la API como los archivos estáticos del frontend en puerto 8000.

---

## 📦 Requisitos Previos

- **Python:** 3.10 o superior
- **PostgreSQL:** 14 o superior
- **pip:** Gestor de paquetes de Python
- **Navegador:** Chrome/Firefox/Edge (versiones recientes)

---

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/playzone.git
cd playzone
```

### 2. Configurar el Backend

#### Crear entorno virtual
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar la Base de Datos

#### Crear base de datos PostgreSQL
```sql
CREATE DATABASE playzone_db;
CREATE USER playzone_user WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE playzone_db TO playzone_user;
```

#### Ejecutar scripts de inicialización
```bash
# 1. Crear tablas base
psql -U playzone_user -d playzone_db -f database/init.sql

# 2. Aplicar características de seguridad
psql -U playzone_user -d playzone_db -f backend/migrations/001_security_enhancements.sql
```

O desde **Supabase SQL Editor**:
1. Copiar contenido de `backend/migrations/001_security_enhancements.sql`
2. Pegar en SQL Editor
3. Click en **Run**

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la carpeta `backend/`:

```env
# Database
DATABASE_URL=postgresql://playzone_user:tu_contraseña@localhost:5432/playzone_db

# JWT
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000
```

### 5. Configurar APIs de Imágenes

Editar `frontend/assets/js/config.js`:

```javascript
// RAWG API - Para videojuegos (https://rawg.io/apidocs)
const RAWG_API_KEY = 'tu_api_key_rawg_aqui';

// Serper API - Para consolas y accesorios (https://serper.dev)
const SERPER_API_KEY = 'tu_api_key_serper_aqui';
```

**Notas:**
- **RAWG:** 100,000 requests/mes gratis
- **Serper:** 2,500 búsquedas gratis, luego $50/5k búsquedas

---

## ⚙️ Configuración

### Iniciar el Servidor

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

El sistema estará disponible en:
- **Frontend:** http://localhost:8000/login
- **API Docs:** http://localhost:8000/docs

---

## 📖 Uso del Sistema

### Inicio de Sesión
1. Acceder a `http://localhost:8000/login`
2. Ingresar credenciales
3. El sistema redirige al dashboard

### Agregar Producto
1. Ir a sección **Productos**
2. Click en **Agregar Nuevo Producto**
3. Completar formulario:
   - **Nombre:** Escribe el nombre del producto (ej: "FIFA 23", "PlayStation 5")
   - **Categoría:** Selecciona tipo (Videojuegos/Consolas/Accesorios)
   - **Precio:** Ingresa el precio
   - **Stock:** Cantidad disponible
   - **Imagen:** Haz clic en el botón 🔍 para buscar imágenes automáticamente
4. Seleccionar imagen de las opciones encontradas (hasta 5 resultados)
5. Guardar

**Búsqueda de Imágenes:**
- 🎮 Videojuegos: Busca en RAWG (base de datos especializada)
- 🕹️ Consolas: Busca en Google Images vía Serper
- 🎧 Accesorios: Busca en Google Images vía Serper

### Registrar Venta
1. Ir a sección **Registrar Ventas**
2. Agregar productos al carrito
3. Click en **Guardar Venta**
4. Ingresar documento del cliente:
   - Si existe: Datos se autocompletan
   - Si no existe: Registrar nuevo cliente
5. Confirmar venta

### Gestionar Servicios
1. Ir a sección **Servicios**
2. Click en **Nuevo Servicio**
3. Completar:
   - Datos del cliente
   - Consola a reparar
   - Descripción del problema
   - Costo estimado
4. Actualizar estado según progreso

---

## 📂 Estructura del Proyecto

```
playzone/
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   └── database.py          # Conexión a PostgreSQL
│   │   ├── controllers/
│   │   │   ├── auth_controller.py   # Autenticación JWT
│   │   │   ├── producto_controller.py
│   │   │   ├── venta_controller.py
│   │   │   ├── servicio_controller.py
│   │   │   └── cliente_controller.py
│   │   ├── middleware/
│   │   │   └── auth.py              # Middleware de autenticación
│   │   ├── models/
│   │   │   └── *.py                 # Modelos Pydantic
│   │   └── routes/
│   │       └── *.py                 # Rutas FastAPI
│   ├── main.py                      # Punto de entrada
│   └── requirements.txt
│
├── frontend/
│   ├── assets/
│   │   ├── css/
│   │   │   ├── home.css            # Estilos principales
│   │   │   ├── login.css
│   │   │   ├── product.css
│   │   │   ├── services.css
│   │   │   └── addsales.css
│   │   ├── js/
│   │   │   ├── config.js           # Configuración API
│   │   │   ├── notifications.js    # Sistema de notificaciones
│   │   │   ├── utils/
│   │   │   │   ├── eventBus.js     # Sistema de eventos
│   │   │   │   └── imageSearch.js  # Búsqueda de imágenes
│   │   │   ├── controllers/
│   │   │   │   ├── NavigationController.js
│   │   │   │   └── VentaController.js
│   │   │   └── views/
│   │   │       ├── DashboardView.js
│   │   │       ├── ProductoView.js
│   │   │       ├── VentasView.js
│   │   │       └── ServiciosView.js
│   │   └── images/
│   ├── pages/
│   │   └── home.html               # Aplicación principal
│   └── index.html                  # Login
│
├── database/
│   └── init.sql                    # Script de inicialización
│
└── README.md
```

---

## 🎯 Funcionalidades Implementadas

### Requerimientos Funcionales

| RF | Funcionalidad | Estado |
|----|--------------|--------|
| RF-01 | Registro de Productos | ✅ |
| RF-02 | Gestión de Inventario | ✅ |
| RF-03 | Registro de Ventas | ✅ |
| RF-04 | Confirmación de Operaciones | ✅ |
| RF-05 | Gestión de Servicios | ✅ |
| RF-06 | Actualización de Estados | ✅ |
| RF-07 | Datos Básicos de Clientes | ✅ |
| RF-08 | Autenticación de Usuarios | ✅ |
| RF-09 | Filtros y Búsqueda | ✅ |
| RF-10 | Historial de Transacciones | ✅ |
| RF-11 | Alertas de Stock Bajo | ✅ |
| RF-12 | Accesibilidad Móvil | ✅ |
| RF-13 | Actualización en Tiempo Real | ✅ |
| RF-14 | Búsqueda de Clientes | ✅ |
| RF-15 | Imágenes Automáticas | ✅ |

---

## 🔌 API Endpoints

### Autenticación
```http
POST /api/auth/login              # Login con rate limiting
POST /api/auth/register           # Registrar usuario
POST /api/auth/refresh            # Refrescar access token
POST /api/auth/logout             # Cerrar sesión
POST /api/auth/logout-all         # Cerrar todas las sesiones

# Ejemplo de login
{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

### Productos
```http
GET    /api/productos/              # Listar productos
POST   /api/productos/              # Crear producto
GET    /api/productos/{id}          # Obtener producto
PUT    /api/productos/{id}          # Actualizar producto
DELETE /api/productos/{id}          # Eliminar producto
```

### Ventas
```http
GET    /api/ventas/                 # Listar ventas
POST   /api/ventas/                 # Registrar venta
GET    /api/ventas/{id}             # Obtener venta
GET    /api/ventas/reporte/pdf      # Descargar reporte PDF profesional
```

### Servicios
```http
GET    /api/servicios/              # Listar servicios
POST   /api/servicios/              # Crear servicio
PUT    /api/servicios/{id}          # Actualizar servicio
DELETE /api/servicios/{id}          # Eliminar servicio
```

### Clientes
```http
GET    /api/clientes/               # Listar clientes
POST   /api/clientes/               # Crear cliente
GET    /api/clientes/buscar/{doc}  # Buscar por documento
GET    /api/clientes/{id}           # Obtener cliente
PUT    /api/clientes/{id}           # Actualizar cliente
DELETE /api/clientes/{id}           # Eliminar cliente
```

---

## 🎨 Características Técnicas

### Sistema de Eventos (EventBus)
```javascript
// Emitir evento
EventBus.emit(Events.PRODUCTO_CREADO, productoData);

// Escuchar evento
EventBus.on(Events.PRODUCTO_CREADO, (data) => {
    console.log('Nuevo producto:', data);
    actualizarDashboard();
});
```

### Búsqueda Automática de Imágenes
- **Búsqueda inteligente por categoría:**
  - Videojuegos: RAWG Video Games Database API
  - Consolas y Accesorios: Serper.dev (Google Images)
- **Botón manual 🔍** para búsqueda bajo demanda
- **Hasta 5 opciones** de imágenes por producto
- **Preview visual** antes de seleccionar
- **Selección con un clic** directamente desde los resultados
- **Fallback automático** a placeholders por categoría
- **Prevención XSS** con escape de HTML en nombres e URLs

### Actualización en Tiempo Real
- Sin necesidad de refrescar la página
- Dashboard se actualiza automáticamente
- Sincronización entre secciones
- EventBus para comunicación desacoplada

---

## 🔒 Seguridad

### Autenticación y Acceso
- ✅ **JWT + Refresh Tokens** - Access tokens (30 min) + Refresh tokens (30 días)
- ✅ **Rate Limiting** - Máx 5 intentos fallidos por usuario, 10 por IP
- ✅ **Bloqueo Temporal** - 15 minutos después de alcanzar el límite
- ✅ **Roles y Permisos** - ADMIN, VENDEDOR, CAJERO con permisos granulares
- ✅ **Auditoría Completa** - Log de todos los logins y acciones críticas
- ✅ **Logout Seguro** - Revocación de tokens individuales o todas las sesiones

### Protección de Datos
- ✅ **Contraseñas Hasheadas** - Bcrypt con salt automático
- ✅ **Migración Automática** - Actualiza contraseñas en texto plano a bcrypt
- ✅ **Soft Delete** - Borrado lógico, datos preservados
- ✅ **Validación de Inputs** - Prevención SQL injection y XSS
- ✅ **Sanitización** - Escape HTML automático
- ✅ **CORS Configurado** - Orígenes permitidos específicos

### Reportes y Auditoría
- ✅ **Generación PDF Profesional** - Reportes con branding PlayZone
- ✅ **Tracking de Sesiones** - IP, user agent, timestamps
- ✅ **Logs de Cambios** - Datos anteriores y nuevos en auditoría

---

## 📱 Acceso Móvil

### Opción 1: Red Local
1. Obtener IP del servidor: `ipconfig` (Windows) / `ifconfig` (Linux/Mac)
2. Acceder desde móvil: `http://IP_SERVIDOR:8000/login`

### Opción 2: Túnel ngrok
```bash
# Descargar ngrok desde https://ngrok.com
ngrok http 8000
```
Usar la URL proporcionada (ej: `https://abc123.ngrok-free.app`)

### Opción 3: Port Forwarding VSCode
1. En VSCode, abrir panel **PORTS**
2. Agregar puerto 8000
3. Hacer público
4. Compartir URL generada

---

## 🐛 Solución de Problemas

### El servidor no inicia
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Verificar puerto 8000 disponible
netstat -an | findstr 8000
```

### Error de conexión a base de datos
- Verificar credenciales en `.env`
- Verificar que la base de datos existe
- Verificar permisos del usuario PostgreSQL

### Imágenes no se cargan
- Verificar API keys en `config.js`:
  - RAWG_API_KEY (para videojuegos)
  - SERPER_API_KEY (para consolas/accesorios)
- Verificar cuota de API no excedida
- Verificar conexión a internet
- Revisar consola del navegador para errores CORS
- Para videojuegos: Verificar que RAWG API esté funcionando
- Para consolas/accesorios: Verificar que Serper API esté activa

### Token expirado
- Cerrar sesión y volver a iniciar
- Tokens expiran cada 30 minutos por seguridad

---

## 👥 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

## 📝 Licencia

Este proyecto fue desarrollado como parte del programa académico de la **Universidad Popular del Cesar**.

---

## 👨‍💻 Desarrollado por

**Universidad Popular del Cesar**
Proyecto: Sistema de Gestión de Inventario PlayZone
Año: 2025

---

## 🙏 Agradecimientos

- **RAWG API** - Por proporcionar la base de datos de videojuegos
- **Serper.dev** - Por el acceso a Google Images para consolas y accesorios
- **FastAPI** - Por el excelente framework
- **PostgreSQL** - Por la robusta base de datos
- **Claude Code** - Asistente de desarrollo IA

---

## 📞 Soporte

Para reportar bugs o solicitar features:
- Abrir un issue en GitHub
- Contactar al equipo de desarrollo

---

**¡Gracias por usar PlayZone! 🎮**
