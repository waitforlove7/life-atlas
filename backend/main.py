from fastapi import FastAPI

app = FastAPI(
    title="Life Atlas API"
)


@app.get("/")
def root():
    return {"message": "Life Atlas API running"}
