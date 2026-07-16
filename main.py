from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0.0",
    description="A simple task management API with CRUD operations",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get(
    "/",
    summary="Root endpoint",
    description="Returns API metadata and available endpoints"
)
async def root():
    return {
        "name": "Task API",
        "version": "1.0.0",
        "endpoints": ["/tasks"]
    }

@app.get(
    "/health",
    summary="Health check",
    description="Returns the health status of the API"
)
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)