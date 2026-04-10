from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit,
    auth,
    evaluations,
    feedback,
    insights,
    prompts,
    query,
    settings,
    sources,
    traces,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(sources.router)
api_router.include_router(query.router)
api_router.include_router(prompts.router)
api_router.include_router(evaluations.router)
api_router.include_router(insights.router)
api_router.include_router(feedback.router)
api_router.include_router(audit.router)
api_router.include_router(settings.router)
api_router.include_router(traces.router)
