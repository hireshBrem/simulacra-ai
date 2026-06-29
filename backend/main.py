from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from api.routes import router
from api.stream import router as stream_router

app = FastAPI(title="Sapiaverse Demo API", description="LLM-powered social simulation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(stream_router, prefix="/api")


@app.get("/")
def root():
    return {"status": "running", "service": "sapiaverse-demo-backend"}
