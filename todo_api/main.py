from fastapi import FastAPI
from routes import router

app = FastAPI(
    title="To-Do API",
    description="Simple To-Do management system",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "To-Do API is running"}