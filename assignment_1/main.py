from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/greet/{username}")
async def greet_user(username: str):
    return {"message": f"Hello {username}! I hope you are doing good"}
