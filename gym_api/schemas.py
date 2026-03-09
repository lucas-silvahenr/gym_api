from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class ExerciseSchema(BaseModel):
    name: str
    description: str | None


class ResponseExerciseSchema(ExerciseSchema):
    id: int


class ExerciseList(BaseModel):
    exercises: list[ResponseExerciseSchema]


class WorkoutExerciseSchema(BaseModel):
    exercise_id: int
    session_id: int
    order: int
    rep: int
    weight: float

    model_config = ConfigDict(from_attributes=True)


class WorkoutSessionSchema(BaseModel):
    name: str
    exercises: list[WorkoutExerciseSchema] = []
    model_config = ConfigDict(from_attributes=True)


class ResponseWorkoutSessionList(BaseModel):
    sessions: list[WorkoutSessionSchema]
    model_config = ConfigDict(from_attributes=True)
