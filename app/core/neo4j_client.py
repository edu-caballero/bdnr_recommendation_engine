from neo4j import GraphDatabase, Driver
from app.core.config import settings

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def run_write(cypher: str, parameters: dict | None = None):
    driver = get_driver()
    with driver.session() as session:
        return session.execute_write(lambda tx: tx.run(cypher, **(parameters or {})))

def run_read(cypher: str, parameters: dict | None = None) -> list[dict]:
    driver = get_driver()
    with driver.session(database=settings.neo4j_database) as session:
        result = session.run(cypher, **(parameters or {}))
        return list(result.data())