"""
Main entry point for the backend.
Creates the FastAPI app and includes all routers.
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from STT import router as stt_router
from instagram import router as instagram_router

app = FastAPI()

# CORS is the web browser security mechanism that restricts/allows selected requests. For local development, we allow all origins. In production, we will restrict to the frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Making the frontend files available from the backend...
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# ...so that when we access the backend URL from the browser (http://localhost:8001/), it serves the frontend page (in production, the frontend would be served separately and this wouldn't be necessary)
@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Include routers from all backend modules
app.include_router(stt_router)
app.include_router(instagram_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
