"""
PlayZone Inventory System - Backend API
Sistema de gestion de inventario y servicios de reparacion de consolas
Desarrollado para la tienda Play Zone
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from app.config.settings import settings
from app.config.database import test_connection

# Importar rutas
from app.routes import auth, productos, ventas, clientes, servicios


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos del ciclo de vida de la aplicacion"""
    # Startup
    print(f"Iniciando {settings.app_name} v{settings.app_version}")
    print(f"Modo Debug: {settings.debug}")
    print(f"Puerto: {settings.port}")
    print("Probando conexion a la base de datos...")
    test_connection()
    yield
    # Shutdown
    print("Apagando servidor...")


# Crear instancia de FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API REST para gestion de inventario, ventas y servicios de mantenimiento de consolas",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Configurar CORS - RF-12: Accesibilidad desde navegador web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Endpoint raiz - verificacion de salud de la API"""
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "status": "online"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """RF-15: Verificacion de estado del sistema"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


@app.get("/api", tags=["Health"])
async def api_info():
    """Informacion de la API"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "auth": "/api/auth",
            "productos": "/api/productos",
            "ventas": "/api/ventas",
            "clientes": "/api/clientes",
            "servicios": "/api/servicios"
        }
    }


# Registrar rutas
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticacion"])
app.include_router(productos.router, prefix="/api/productos", tags=["Productos"])
app.include_router(ventas.router, prefix="/api/ventas", tags=["Ventas"])
app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(servicios.router, prefix="/api/servicios", tags=["Servicios"])


# Servir archivos estáticos del frontend
frontend_path = Path(__file__).parent.parent / "frontend"

# Montar carpeta de assets (CSS, JS, images)
app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")

# Ruta para servir index.html en la raíz
@app.get("/login")
async def serve_login():
    """Servir página de login"""
    return FileResponse(str(frontend_path / "index.html"))

# Ruta para servir home.html
@app.get("/home")
async def serve_home():
    """Servir página principal"""
    return FileResponse(str(frontend_path / "pages" / "home.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
