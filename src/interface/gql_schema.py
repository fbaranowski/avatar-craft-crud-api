import base64
import json
import uuid
from pathlib import Path
from typing import List

import strawberry
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import literal
from strawberry.asgi import GraphQL

from core.rabbitmq import RabbitMQProducer
from database.db_session import get_db_session
from interface.exceptions import (AvatarDoesNotExistException,
                                  UserNotFoundException)
from models import Avatar, User
from s3.s3_handler import download_file_from_s3
from s3.settings import AWSSettings


@strawberry.type
class AvatarType:
    id: int
    uuid: uuid.UUID
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
                            uuid=avatar.uuid,
                            type=avatar.type,
                        )
                        for avatar in user.avatars
                    ],
                )
                for user in users
            ]

    @strawberry.field
    async def avatars(
        self,
        email: str,
        avatar_id: int | None = None,
        avatar_type: str | None = None,
        shared_to_email: str | None = None,
        shared_from_email: str | None = None,
    ) -> List[AvatarType]:

        async with get_db_session() as session:
            if shared_to_email == email:
                user = await session.execute(
                    select(User).where(User.mail == shared_from_email)
                )
            else:
                user = await session.execute(select(User).where(User.mail == email))

            user_obj = user.unique().scalar_one_or_none()

            if not user_obj:
                raise UserNotFoundException(email)

            query = select(Avatar).where(Avatar.user_id == literal(user_obj.id))

            if avatar_type:
                query = query.where(Avatar.type == avatar_type)
            if avatar_id:
                query = query.where(Avatar.id == avatar_id)

            result = await session.execute(query)
            avatars = result.unique().scalars().all()

            return [
                AvatarType(
                    id=avatar.id, uuid=avatar.uuid, name=avatar.name, type=avatar.type
                )
                for avatar in avatars
            ]

    @strawberry.field
    async def download_avatar(
        self,
        email: str,
        avatar_uuid: str,
        shared_to_email: str | None = None,
        shared_from_email: str | None = None,
    ) -> str:
        async with get_db_session() as session:
            if shared_to_email == email:
                user = await session.execute(
                    select(User).where(User.mail == shared_from_email)
                )
            else:
                user = await session.execute(select(User).where(User.mail == email))

            user_obj = user.unique().scalar_one_or_none()

            if not user_obj:
                raise UserNotFoundException(email)

            avatar = await session.execute(
                select(Avatar).where(Avatar.user_id == literal(user_obj.id))
            )
            avatar_obj = avatar.unique().scalar_one_or_none()

            if not avatar_obj:
                raise AvatarDoesNotExistException(avatar_uuid)

        file_path = Path(AWSSettings.DOWNLOADS_PATH) / f"{avatar_uuid}.jpg"

        if not file_path.exists():
            await download_file_from_s3(avatar_uuid)

        with open(file_path, "rb") as file:
            file_bytes = file.read()

        base64_bytes = base64.b64encode(file_bytes).decode("utf-8")

        return base64_bytes


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
        async with get_db_session() as session:
            user_query = await session.execute(select(User).where(User.mail == email))
            user = user_query.unique().scalar_one_or_none()

            if not user:
                raise UserNotFoundException(email)

            new_avatar = Avatar(
                uuid=uuid.uuid4(), user_id=user.id, name=prompt, type=ai_model
            )
            session.add(new_avatar)
            await session.commit()

            body = {
                "uuid": str(new_avatar.uuid),
                "ai_model": ai_model,
                "prompt": prompt,
            }

            async with RabbitMQProducer() as producer:
                await producer.publish_message(message=body)

        return AvatarType(
            id=new_avatar.id,
            uuid=new_avatar.uuid,
            name=new_avatar.name,
            type=new_avatar.type,
        )

    @strawberry.mutation
    async def delete_avatar(self, email: str, avatar_id: int) -> str:
        async with get_db_session() as session:
            user_query = await session.execute(select(User).where(User.mail == email))
            user = user_query.unique().scalar_one_or_none()

            if not user:
                raise UserNotFoundException(email)

            avatar = await session.get(Avatar, avatar_id)

            if user.id == avatar.user_id:
                await session.delete(avatar)
                await session.commit()
                return json.dumps({"message": "Avatar deleted successfully"})


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQL(schema)
