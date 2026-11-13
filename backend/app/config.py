import os
from pydantic import BaseModel

class Settings(BaseModel):
    PORT: int = int(os.getenv("PORT", "8000"))
    INSIGHTBI_DB: str = os.getenv("INSIGHTBI_DB", "insightbi.db")

settings = Settings()
