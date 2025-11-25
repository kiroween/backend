"""
TimeGrave API - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TimeGrave API",
    description="디지털 타임캡슐 관리 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": 200,
        "data": {
            "result": {
                "message": "TimeGrave API is running",
                "version": "1.0.0"
            }
        }
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database and scheduler on startup"""
    print("🚀 TimeGrave API starting up...")
    # TODO: Initialize database
    # TODO: Start scheduler


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 TimeGrave API shutting down...")
    # TODO: Cleanup resources
