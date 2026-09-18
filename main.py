from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router

app = FastAPI(
    title="Student Planner API",
    description="API для мобільного застосунку планування навчальної діяльності студента",
    version="1.0.0"
)

# Налаштування CORS (щоб клієнт міг робити запити)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # У продакшені варто замінити на конкретні домени
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Student Planner API. Go to /docs for Swagger UI"}
