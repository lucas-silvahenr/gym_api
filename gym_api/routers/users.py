from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_session
from gym_api.models import User
from gym_api.schemas import (
    Message,
    UserPublic,
    UserSchema,
)
from gym_api.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])
AnnotatedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=UserPublic, status_code=HTTPStatus.CREATED)
async def create_user(user: UserSchema, session: AnnotatedSession):
    if not user.password:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Password cannot be empty',
        )
    if not user.username:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Username cannot be empty',
        )
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, email=user.email, password=hashed_password
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.put('/{user_id}', response_model=UserPublic, status_code=HTTPStatus.OK)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)
        await session.commit()
        await session.refresh(current_user)
        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


@router.delete('/{user_id}', response_model=Message, status_code=HTTPStatus.OK)
async def delete_user(
    user_id: int,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    user_to_delete = await session.scalar(
        select(User).where(User.id == user_id)
    )
    if not user_to_delete:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to delete this user',
        )
    await session.delete(user_to_delete)
    await session.commit()

    return {'message': 'User deleted'}
