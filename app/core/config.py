from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseModel):
    neo4j_uri: str = os.getenv("NEO4J_URI")
    neo4j_user: str = os.getenv("NEO4J_USER")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD")
    neo4j_database: str = os.getenv("NEO4J_DATABASE")
    initialize_graph_on_startup: bool = os.getenv(
        "INITIALIZE_GRAPH_ON_STARTUP", "true"
    ).lower() == "true"
    cypher_dir: Path = BASE_DIR / "cypher"


settings = Settings()
print(
    f"[config] uri={settings.neo4j_uri}, user={settings.neo4j_user}, "
    f"db={settings.neo4j_database}"
)
