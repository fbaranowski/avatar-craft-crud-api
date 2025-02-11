import logging
from pathlib import Path

from botocore.exceptions import ClientError

from s3.s3_client import connect_client
from s3.settings import AWSSettings


async def download_file_from_s3(file_uuid: str) -> bool:
    try:
        async with await connect_client() as client:
            response = await client.get_object(
                Bucket=AWSSettings.BUCKET_NAME, Key=f"{file_uuid}.jpg"
            )

            file_data = await response["Body"].read()

            local_directory = Path(AWSSettings.DOWNLOADS_PATH)
            local_directory.mkdir(parents=True, exist_ok=True)
            file_path = local_directory / f"{file_uuid}.jpg"

            with open(file_path, "wb") as file:
                file.write(file_data)

    except ClientError as e:
        logging.error(f"Error while downloading file from S3: {e}")
        return False

    return True
