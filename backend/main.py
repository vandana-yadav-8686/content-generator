from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Content Generator API is running!"
    }

# Your existing routers
app.include_router(...)
