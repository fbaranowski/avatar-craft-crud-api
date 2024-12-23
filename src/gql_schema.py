import json
import strawberry
import avatar_creator
from typing import List, Optional
from fastapi import Request, HTTPException
from strawberry.asgi import GraphQL
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select
from models import User, Avatar
from db_session import get_db_session
import random
import string


@strawberry.type
class AvatarType:
    id: int
    url: str
    name: str
    type: str


@strawberry.type
class UserType:
    id: int
    mail: str
    avatars: List[AvatarType]


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, email: str | None = None) -> List[UserType]:
        async with get_db_session() as session:
            query = select(User).options(joinedload(User.avatars))

            if email:
                query = query.where(User.mail == email)

            result = await session.execute(query)
            users = result.unique().scalars().all()

            return [
                UserType(
                    id=user.id,
                    mail=user.mail,
                    avatars=[AvatarType(id=avatar.id, name=avatar.name, url=avatar.url, type=avatar.type) for avatar in user.avatars]
                )
                for user in users
            ]

    @strawberry.field
    async def avatars(self, email: str, avatar_id: int | None = None, avatar_type: str | None = None) -> List[AvatarType]:

        async with get_db_session() as session:
            user = await session.execute(select(User).where(User.mail == email))
            user_obj = user.unique().scalar_one_or_none()
            query = select(Avatar).where(Avatar.user_id == user_obj.id)

            if avatar_id:
                query = query.where(Avatar.id == avatar_id)
            if avatar_type:
                query = query.where(Avatar.type == avatar_type)

            result = await session.execute(query)
            avatars = result.unique().scalars().all()

            return [
                AvatarType(
                    id=avatar.id,
                    name=avatar.name,
                    url=avatar.url,
                    type=avatar.type
                )
                for avatar in avatars
            ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, email: str) -> UserType:
        async with get_db_session() as session:
            existing_user = await session.execute(select(User).where(User.mail == email))
            existing_user_obj = existing_user.unique().scalar_one_or_none()

            if existing_user_obj:
                return UserType(
                    id=existing_user_obj.id,
                    mail=existing_user_obj.mail,
                    avatars=existing_user_obj.avatars
                )

            new_user = User(mail=email)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return UserType(id=new_user.id, mail=new_user.mail, avatars=new_user.avatars)

    @strawberry.mutation
    async def create_avatar(self, email: str, ai_model: str, prompt: str) -> AvatarType:
        # image_url = ''.join(random.choices(string.ascii_letters, k=7))
        image_url = await avatar_creator.create_avatar(model=ai_model, prompt=prompt)

        async with get_db_session() as session:
            user = await session.execute(select(User).where(User.mail == email))
            user_obj = user.unique().scalar_one_or_none()
            new_avatar = Avatar(url=image_url, user_id=user_obj.id, name=prompt, type=ai_model)
            session.add(new_avatar)
            await session.commit()

            return AvatarType(id=new_avatar.id, name=new_avatar.name, url=new_avatar.url, type=new_avatar.type)

    @strawberry.mutation
    async def edit_avatar(self, email: str, avatars_urls: List[str], ai_model: str, prompt: str) -> AvatarType:
        # image_url = ''.join(random.choices(string.ascii_letters, k=7))
        image_url = await avatar_creator.update_avatar(model=ai_model, prompt=prompt, input_avatars=avatars_urls)

        async with get_db_session() as session:
            user = await session.execute(select(User).where(User.mail == email))
            user_obj = user.unique().scalar_one_or_none()
            new_avatar = Avatar(url=image_url, user_id=user_obj.id, name=prompt, type=ai_model)
            session.add(new_avatar)
            await session.commit()

            return AvatarType(id=new_avatar.id, name=new_avatar.name, url=new_avatar.url, type=new_avatar.type)

    @strawberry.mutation
    async def delete_avatar(self, email: str, avatar_id: int) -> str:
        async with get_db_session() as session:
            user = await session.execute(select(User).where(User.mail == email))
            user_obj = user.unique().scalar_one_or_none()
            avatar = await session.get(Avatar, avatar_id)

            if user_obj.id == avatar.user_id:
                await session.delete(avatar)
                await session.commit()
                return json.dumps({"message": "Avatar deleted successfully"})


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQL(schema)
