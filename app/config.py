"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # Google Sheets base URL
    sheets_base_url: str = "https://docs.google.com/spreadsheets/d"
    
    # Individual Sheet IDs
    sheet_id_articles: str = ""
    sheet_id_boutique: str = ""
    sheet_id_church_info: str = ""
    sheet_id_contact: str = ""
    sheet_id_events: str = ""
    sheet_id_home_groups: str = ""
    sheet_id_pastoral_team: str = ""
    sheet_id_services: str = ""
    sheet_id_vision: str = ""
    
    # Cache settings
    cache_ttl_seconds: int = 600  # 10 minutes
    
    # Language settings
    default_language: str = "fr"
    supported_languages: list[str] = ["fr", "en"]
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def get_sheet_csv_url(self, sheet_id: str, tab_name: str | None = None) -> str:
        """Generate the public CSV export URL for a Google Sheet."""
        url = f"{self.sheets_base_url}/{sheet_id}/gviz/tq?tqx=out:csv"
        if tab_name:
            url += f"&sheet={tab_name}"
        return url
    
    @staticmethod
    def get_doc_html_url(doc_id: str) -> str:
        """Generate the public HTML export URL for a Google Doc."""
        return f"https://docs.google.com/document/d/{doc_id}/export?format=html"
    
    @staticmethod
    def extract_doc_id(doc_url: str) -> str | None:
        """Extract document ID from a Google Docs URL."""
        # Handles URLs like:
        # https://docs.google.com/document/d/ABC123/edit
        # https://docs.google.com/document/d/ABC123/view
        # https://docs.google.com/document/d/ABC123
        if not doc_url or "docs.google.com/document/d/" not in doc_url:
            return None
        try:
            # Split by /d/ and get the ID part
            parts = doc_url.split("/d/")[1].split("/")
            return parts[0]
        except (IndexError, AttributeError):
            return None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
