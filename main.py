from fastapi import FastAPI

app = FastAPI()

@app.get("/wplace/")
async def root():
    return {"message": "Vika loh"}
