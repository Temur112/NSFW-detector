from fastapi import FastAPI
from src.routes.detection import detector_router

app = FastAPI(title="NSFW detector", version="0.1.0")


#include routes
app.include_router(detector_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
