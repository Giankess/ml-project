from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Ollama Settings
    OLLAMA_HOST: str = "http://ollama:11434"
    
    # File Storage Settings
    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"

settings = Settings() 