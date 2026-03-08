from fastapi import FastAPI

from gym_api.routers import auth, users, workout
from gym_api.schemas import Message

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(workout.router)


@app.get('/', response_model=Message)
def read_root():
    return {'message': 'Hello World'}
