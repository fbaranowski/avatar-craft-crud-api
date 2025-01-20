from functools import lru_cache

import aioboto3

from s3.settings import AWSSettings


@lru_cache
def get_s3_session():
    return aioboto3.Session()


async def connect_client():
    session = get_s3_session()

    return session.client(
        service_name="s3",
        aws_access_key_id=AWSSettings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWSSettings.AWS_SECRET_ACCESS_KEY,
        region_name=AWSSettings.AWS_REGION_NAME,
    )
