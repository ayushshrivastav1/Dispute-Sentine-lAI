from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dispute_sentinel.db"
    
    # Razorpay
    RAZORPAY_KEY_ID: str = "rzp_test_XXXXXXXXXXXX"
    RAZORPAY_KEY_SECRET: str = "XXXXXXXXXXXXXXXXXXXXXXXX"
    RAZORPAY_WEBHOOK_SECRET: str = "whsec_test"
    
    # LLM
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Auth
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Policy Thresholds
    AUTO_CONTEST_THRESHOLD: float = 0.75
    AUTO_ACCEPT_THRESHOLD: float = 0.40
    MAX_AUTO_CONTEST_AMOUNT: int = 2500000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
