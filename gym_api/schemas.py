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


class WorkoutExerciseCreateSchema(BaseModel):
    exercise_id: int
    order: int
    rep: int
    weight: float

    model_config = ConfigDict(from_attributes=True)


class WorkoutExerciseResponseSchema(WorkoutExerciseCreateSchema):
    id: int
    session_id: int


class WorkoutSessionSchema(BaseModel):
    name: str
    exercises: list[WorkoutExerciseCreateSchema] = []
    model_config = ConfigDict(from_attributes=True)


class ResponseWorkoutSessionSchema(BaseModel):
    id: int
    name: str
    exercises: list[WorkoutExerciseCreateSchema] = []
    model_config = ConfigDict(from_attributes=True)


class ResponseWorkoutSessionList(BaseModel):
    sessions: list[ResponseWorkoutSessionSchema]
    model_config = ConfigDict(from_attributes=True)
