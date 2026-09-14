from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "ComercioPro"
    APP_ENV: str = "development"
    SECRET_KEY: str = "cambia-esta-clave"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    DB_ENGINE: str = "sqlite"
    SQLITE_PATH: str = str(BASE_DIR / "comerciopro.db")

    MSSQL_SERVER: str = "localhost"
    MSSQL_PORT: int = 1433
    MSSQL_DATABASE: str = "ComercioPro"
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str = ""
    MSSQL_DRIVER: str = "ODBC Driver 18 for SQL Server"

    DEFAULT_COMPANY_NAME: str = "ComercioPro Demo"
    DEFAULT_BRANCH_NAME: str = "Sucursal Principal"
    DEFAULT_ADMIN_USER: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "Admin123!"
    DEFAULT_TAX_RATE: float = 0.18
    CURRENCY: str = "DOP"
    CURRENCY_SYMBOL: str = "RD$"

    @property
    def database_url(self) -> str:
        if self.DB_ENGINE == "mssql":
            driver = self.MSSQL_DRIVER.replace(" ", "+")
            return (
                f"mssql+pyodbc://{self.MSSQL_USER}:{self.MSSQL_PASSWORD}"
                f"@{self.MSSQL_SERVER}:{self.MSSQL_PORT}/{self.MSSQL_DATABASE}"
                f"?driver={driver}&TrustServerCertificate=yes"
            )
        return f"sqlite:///{self.SQLITE_PATH}"


settings = Settings()
