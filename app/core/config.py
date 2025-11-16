from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Información del proyecto
    PROJECT_NAME: str = "Cangrejo Azul API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para gestión de usuarios"
    
    # Base de datos
    DATABASE_URL: str
    
    # Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
