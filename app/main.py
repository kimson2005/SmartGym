from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import health_router, users_router, equipments_router, bookings_router, workouts_router

app = FastAPI(title=settings.PROJECT_NAME)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(equipments_router, prefix=settings.API_V1_STR)
app.include_router(bookings_router, prefix=settings.API_V1_STR)
app.include_router(workouts_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to SmartGym API"}
