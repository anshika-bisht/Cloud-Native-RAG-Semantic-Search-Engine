from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Centralized configuration management.
    Validates environment variables at startup, preventing missing config errors during runtime.
    """
    
    # API Settings
    PROJECT_NAME: str = "Cloud-Native RAG API"
    API_V1_STR: str = "/api/v1"
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Standard logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    
    # Database Settings
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/rag_db")
    
    # Vector Store
    VECTOR_STORE_PROVIDER: str = Field(default="qdrant", description="'qdrant' or 'faiss'")
    FAISS_INDEX_PATH: str = Field(default="./data/faiss_index.bin")
    
    QDRANT_HOST: str = Field(default="localhost")
    QDRANT_PORT: int = Field(default=6333)
    QDRANT_API_KEY: str = Field(default="")
    QDRANT_COLLECTION_NAME: str = Field(default="rag_documents")

    # LLM Providers
    LLM_PROVIDER: str = Field(default="groq", description="'groq', 'gemini', or 'ollama'")
    
    # API Keys
    GROQ_API_KEY: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")

    # Models
    GROQ_MODEL_NAME: str = Field(default="llama3-8b-8192")
    GEMINI_MODEL_NAME: str = Field(default="gemini-1.5-flash")
    OLLAMA_MODEL_NAME: str = Field(default="llama3")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")

    # RAG Settings
    CHUNK_SIZE_TOKENS: int = Field(default=512)
    CHUNK_OVERLAP_PERCENTAGE: float = Field(default=0.15)
    MAX_FILE_SIZE_MB: int = Field(default=50)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extraneous environment variables
    )

settings = Settings()
