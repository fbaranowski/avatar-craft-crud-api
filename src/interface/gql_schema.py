import json
from typing import List

import strawberry
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from strawberry.asgi import GraphQL

from core.avatar_creator import create_avatar, update_avatar
from database.db_session import get_db_session
from models import Avatar, User


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
                    avatars=[
                        AvatarType(
                            id=avatar.id,
                            name=avatar.name,
                            url=avatar.url,
                            type=avatar.type,
                        )
                        for avatar in user.avatars
                    ],
                )
                for user in users
            ]

    @strawberry.field
    async def avatars(
        self, email: str, avatar_id: int | None = None, avatar_type: str | None = None
    ) -> List[AvatarType]:

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
                    id=avatar.id, name=avatar.name, url=avatar.url, type=avatar.type
                )
                for avatar in avatars
            ]


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_user(self, email: str) -> UserType:
        async with get_db_session() as session:
            existing_user_query = await session.execute(
                select(User).where(User.mail == email)
            )
            existing_user = existing_user_query.unique().scalar_one_or_none()

            if existing_user:
                return UserType(
                    id=existing_user.id,
                    mail=existing_user.mail,
                    avatars=existing_user.avatars,
                )

            new_user = User(mail=email)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return UserType(
                id=new_user.id, mail=new_user.mail, avatars=new_user.avatars
            )

    @strawberry.mutation
    async def create_avatar(self, email: str, ai_model: str, prompt: str) -> AvatarType:
        image_url = await create_avatar(model=ai_model, prompt=prompt)

        async with get_db_session() as session:
            user_query = await session.execute(select(User).where(User.mail == email))
            user = user_query.unique().scalar_one_or_none()
            new_avatar = Avatar(
                url=image_url, user_id=user.id, name=prompt, type=ai_model
            )
            session.add(new_avatar)
            await session.commit()

            return AvatarType(
                id=new_avatar.id,
                name=new_avatar.name,
                url=new_avatar.url,
                type=new_avatar.type,
            )

    @strawberry.mutation
    async def edit_avatar(
        self, email: str, avatar_url: str, ai_model: str, prompt: str
    ) -> AvatarType:
        avatar_url_as_list = [avatar_url]

        image_url = await update_avatar(
            model=ai_model, prompt=prompt, input_avatars=avatar_url_as_list
        )

        async with get_db_session() as session:
            user_query = await session.execute(select(User).where(User.mail == email))
            user = user_query.unique().scalar_one_or_none()

            avatar_query = await session.execute(
                select(Avatar).where(
                    Avatar.url == avatar_url, Avatar.user_id == user.id
                )
            )
            avatar = avatar_query.unique().scalar_one_or_none()

            avatar.url = image_url

            await session.commit()

            return AvatarType(
                id=avatar.id,
                name=avatar.name,
                url=avatar.url,
                type=avatar.type,
            )

    @strawberry.mutation
    async def delete_avatar(self, email: str, avatar_id: int) -> str:
        async with get_db_session() as session:
            user_query = await session.execute(select(User).where(User.mail == email))
            user = user_query.unique().scalar_one_or_none()
            avatar = await session.get(Avatar, avatar_id)

            if user.id == avatar.user_id:
                await session.delete(avatar)
                await session.commit()
                return json.dumps({"message": "Avatar deleted successfully"})


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQL(schema)
