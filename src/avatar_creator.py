import uuid
from typing import List

from runware import IImageInference, IPhotoMaker, Runware

from settings import RunwareSettings

MODELS = {
    "anime": "civitai:30240@125771",
    "cartoon": "civitai:30240@125771",
    "lego": "civitai:306814@344398",
}


async def create_avatar(model: str, prompt: str) -> str:
    runware = Runware(api_key=RunwareSettings.RUNWARE_API_KEY)
    await runware.connect()

    request_image = IImageInference(
        positivePrompt=prompt,
        model=MODELS[model],
        numberResults=1,
        height=512,
        width=512,
    )
    image_data = await runware.imageInference(requestImage=request_image)

    for data in image_data:
        return data.imageURL


async def update_avatar(model: str, prompt: str, input_avatars: List[str]) -> str:
    runware = Runware(api_key=RunwareSettings.RUNWARE_API_KEY)
    await runware.connect()

    request_image = IPhotoMaker(
        model=MODELS[model],
        positivePrompt=prompt,
        taskUUID=str(uuid.uuid4()),
        numberResults=1,
        inputImages=input_avatars,
        height=512,
        width=512,
    )
    image_data = await runware.photoMaker(requestPhotoMaker=request_image)

    for data in image_data:
        return data.imageURL
