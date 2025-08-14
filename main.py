from fastapi import FastAPI

app = FastAPI()

@app.get("/wplace/")
async def root():
    return {"message": "Hello, FastAPI!"}
