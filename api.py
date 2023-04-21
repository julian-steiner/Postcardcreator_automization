import logging
import json
import pathlib
from fastapi import FastAPI, UploadFile, File, Form, Request, Depends
import uvicorn
from typing import Annotated
from appium_automations import Postcard, Recipient

from scheduler import PostcardScheduler
from pydantic import BaseModel

app = FastAPI(debug=True)

IMAGE_FOLDER = "images/"
scheduler = PostcardScheduler()

@app.get("/delay")
def get_delay():
    """
    Returns the estimated delay
    """
    return scheduler.estimated_queue_finish()


@app.post("/postcard")
# def read_item(postcard: Postcard, image : UploadFile):
async def read_item(image : UploadFile, postcard : str = Form(...)):
    """
    Send a postcard
    """

    response_postcard = json.loads(postcard)

    postcard = Postcard(
        recipient=Recipient(
            first_name=response_postcard["recipient"]["first_name"],
            last_name=response_postcard["recipient"]["last_name"],
            postal_code=response_postcard["recipient"]["postal_code"],
            location=response_postcard["recipient"]["location"],
            address=response_postcard["recipient"]["address"],
        ),
        description=response_postcard["description"],
        image_location=f"{image.filename}"
    )

    # save the image
    with open(f'{IMAGE_FOLDER}/{image.filename}', 'wb') as file:
        content = await image.read()
        file.write(content)

    scheduler.schedule_postcard(postcard)
    return


if __name__ == "__main__":
    cwd = pathlib.Path(__file__).parent.resolve()
    uvicorn.run(app, host="0.0.0.0", port=5000, log_config=f"{cwd}/log.ini")
    # uvicorn.run(app, host="0.0.0.0", port=5000)
