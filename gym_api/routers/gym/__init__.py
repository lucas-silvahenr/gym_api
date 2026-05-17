from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_session
from gym_api.models import (
    User,
)
from gym_api.models import (
    WorkoutExercise as WorkoutExercise,
)
from gym_api.models import (
    WorkoutSession as WorkoutSession,
)
from gym_api.schemas import (
    Message as Message,
)
from gym_api.schemas import (
    ResponseWorkoutSessionList as ResponseWorkoutSessionList,
)
from gym_api.security import get_current_user

from .exercise import router as exercise_router
from .workout_exercise import router as workout_exercise_router
from .workout_session import router as workout_session_router

AnnotatedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/gym', tags=['gym'])
router.include_router(exercise_router)
router.include_router(workout_exercise_router)
router.include_router(workout_session_router)
