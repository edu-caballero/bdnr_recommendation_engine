from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.graph_initializer import initialize_graph
from app.core.neo4j_client import close_driver
from app.api import routes_events, routes_health, routes_admin, routes_recommendations

app = FastAPI(
    title="Duolingo Recommender Service",
    description="Servicio de recomendaciones basado en Neo4j",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    if settings.initialize_graph_on_startup:
        initialize_graph()


@app.on_event("shutdown")
def on_shutdown():
    close_driver()


app.include_router(routes_health.router)
app.include_router(routes_events.router)
app.include_router(routes_admin.router)
app.include_router(routes_recommendations.router)