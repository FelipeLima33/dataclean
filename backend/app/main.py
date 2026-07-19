from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health
from app.api.routes import clean
from app.api.routes import resolve_ambiguous
from app.api.routes import apply_decisions_route
from app.api.routes import charts_route
from app.api.routes import narrative_route
from app.api.routes import storage_route

app = FastAPI(title="DataClean API")

# Configuração de CORS (permitir chamadas do frontend em desenvolvimento local)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrando rotas
app.include_router(health.router, prefix="/api")
app.include_router(clean.router, prefix="/api")
app.include_router(resolve_ambiguous.router, prefix="/api")
app.include_router(apply_decisions_route.router, prefix="/api")
app.include_router(charts_route.router, prefix="/api")
app.include_router(narrative_route.router, prefix="/api")
app.include_router(storage_route.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "DataClean Backend API is running!"}
