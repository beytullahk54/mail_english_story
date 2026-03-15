import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import config
from database import Base, engine
from modules.subscriber.router import router as subscriber_router
from modules.story.router import router as story_router
from modules.mailer.router import router as mailer_router

# Auto migrate: create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subscriber_router, prefix="/api/v1")
app.include_router(story_router, prefix="/api/v1")
app.include_router(mailer_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(config.SERVER_PORT), reload=True)
