import logging
import sys
from time import sleep

from dotenv import load_dotenv
from adb_automations import ADBAutomationHandler

from appium_automations import Postcard, Recipient
from scheduler import PostcardScheduler

# Load username and password from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# IMAGE_NAME = "PXL_20230119_154801396.jpg"
recipient = Recipient(
    first_name="Julian",
    last_name="Steiner",
    address="Bühli 20",
    postal_code="8755",
    location="Ennenda"
)
IMAGE_NAME = "IMG-20221026-WA0006.jpg"

scheduler = PostcardScheduler()

postcard = Postcard(
    image_location=IMAGE_NAME,
    recipient=recipient,
    description="Das isch e poschtcharte woni automatisch gsendet han zum teschte öbs funktioniert 1"
)
postcard2 = Postcard(
    image_location=IMAGE_NAME,
    recipient=recipient,
    description="Das isch e poschtcharte woni automatisch gsendet han zum teschte öbs funktioniert 2"
)
postcard3 = Postcard(
    image_location=IMAGE_NAME,
    recipient=recipient,
    description="Das isch e poschtcharte woni automatisch gsendet han zum teschte öbs funktioniert 3"
)
postcard4 = Postcard(
    image_location=IMAGE_NAME,
    recipient=recipient,
    description="Das isch e poschtcharte woni automatisch gsendet han zum teschte öbs funktioniert 4"
)

sleep(10)
scheduler.schedule_postcard(postcard)
scheduler.schedule_postcard(postcard4)
scheduler.schedule_postcard(postcard3)
# sleep(60)
scheduler.schedule_postcard(postcard2)

# automation_handler.send_postcard(postcard)

# print(automation_handler.get_timeout_seconds())
