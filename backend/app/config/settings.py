"""
Configuración general de la aplicación
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Solo cargar .env en desarrollo (no en Render/producción)
# Render usa variables de entorno del dashboard
if not os.getenv("RENDER"):
    load_dotenv()


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Información de la aplicación
    app_name: str = os.getenv("APP_NAME", "PlayZone Inventory System")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "True") == "True"
    port: int = int(os.getenv("PORT", 8000))

    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # Base de datos
    database_url: str = os.getenv("DATABASE_URL", "")
    db_host: str = os.getenv("DB_HOST", "")
    db_name: str = os.getenv("DB_NAME", "postgres")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_port: str = os.getenv("DB_PORT", "5432")

    # Seguridad
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # CORS
    allowed_origins: str = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000"

    # API Keys externas
    rawg_api_key: str = os.getenv("RAWG_API_KEY", "")
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")

    # Email Configuration - Resend
    resend_api_key: str = os.getenv("RESEND_API_KEY", "").strip()
    email_from: str = os.getenv("EMAIL_FROM", "onboarding@resend.dev").strip()
    reset_token_expire_minutes: int = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5500").strip()

    @property
    def origins_list(self):
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"


# Instancia global de settings
settings = Settings()
