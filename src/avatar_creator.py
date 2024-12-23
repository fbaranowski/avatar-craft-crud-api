import uuid
from typing import List
from runware import Runware, IImageInference, IPhotoMaker

# models = {'anime': 'civitai:721039@806265', 'cartoon': 'civitai:30240@125771', 'lego': 'civitai:306814@344398'}
# models = ['civitai:721039@806265', 'civitai:30240@125771', 'civitai:306814@344398']
# prompts = [
#     'samurai with red armor in anime style',
#     'tea pot with eyes and wings in cartoon style',
#     'star wars sith with white badass mask lego minifigure'
# ]

MODELS = {
    'anime': 'civitai:30240@125771',
    'cartoon': 'civitai:30240@125771',
    'lego': 'civitai:306814@344398'
}


async def create_avatar(model: str, prompt: str) -> str:
    runware = Runware(api_key='Xso44mOdoBxmDa7ATxxbck8ndw5rpuyo')
    await runware.connect()

    request_image = IImageInference(
        positivePrompt=prompt,
        model=MODELS[model],
        numberResults=1,
        height=512,
        width=512
    )
    image_data = await runware.imageInference(requestImage=request_image)

    for data in image_data:
        return data.imageURL


async def update_avatar(model: str, prompt: str, input_avatars: List[str]) -> str:
    runware = Runware(api_key='Xso44mOdoBxmDa7ATxxbck8ndw5rpuyo')
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


# ToonYou                       cartoons        civitai:30240@125771 - ten dla anime i cartoons
# Photon - LCM                  lego            civitai:306814@344398 - ten dla lego

# 'civitai:25694@143906'