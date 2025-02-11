import os


class AWSSettings:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH")
