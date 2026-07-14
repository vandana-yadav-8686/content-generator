from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import settings as settings_router
from app.routers import repurpose as repurpose_router
from app.routers import generate as generate_router

app = FastAPI(
    title="AI Content Repurposer",
    description="LangGraph multi-provider content repurposing API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(settings_router.router)
app.include_router(repurpose_router.router)
app.include_router(generate_router.router)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "AI Content Repurposer API",
        "health": "/api/health",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "langgraph": True}
