"""
This module contains all the code for the automations made with appium
"""

import logging
import os
import re
from dataclasses import dataclass
from time import sleep

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel

load_dotenv()


# @dataclass
class Recipient(BaseModel):
    """
    Dataclass for storing the recipients information
    """
    first_name: str
    last_name: str
    address: str
    postal_code: str
    location: str


# @dataclass
class Postcard(BaseModel):
    """
    Dataclass for storing all metadata of a postcard
    """
    recipient: Recipient
    image_location: str
    description: str


class AppiumAutomationHandler:
    """
    A class to handle all the automations performed by appium
    """

    def __init__(self, device_id):
        # Appium
        options = UiAutomator2Options()
        options.udid = device_id
        # Set the connection timeout to 2 days
        options.new_command_timeout = 3600 * 48
        self.driver = webdriver.Remote(
            'http://127.0.0.1:4723', options=options)
        self.driver.implicitly_wait(20)

        print(options.udid)
        print(options.platform_name)
        print(options.automation_name)

        self.button_class = "android.widget.Button"
        self.text_class = "android.widget.TextView"
        self.image_view_class = "android.widget.ImageView"
        self.layout_class = "android.widget.LinearLayout"
        self.input_field_class = "android.widget.EditText"
        self.switch_class = "android.widget.Switch"

        logging.info("Appium is now connected to the selected device")

    def __find_button_by_text(self, target_text: str):

        sleep(1)

        buttons = self.driver.find_elements(
            AppiumBy.CLASS_NAME, value=self.button_class)
        for button in buttons:
            try:
                if button.text.find(target_text) != -1:
                    return button
            except Exception:
                continue
        return False

    def __find_text(self, target_text: str):

        sleep(1)

        texts = self.driver.find_elements(
            AppiumBy.CLASS_NAME, value=self.text_class)

        for text in texts:
            try:
                if text.text.find(target_text) != -1:
                    return text
            except Exception:
                continue
        return False

    def __find_image(self, image_name: str):
        sleep(1)

        images = self.driver.find_elements(
            AppiumBy.CLASS_NAME, value=self.layout_class
        )

        for image in images:
            if content_desc := image.get_attribute('content-desc'):
                if content_desc.find(image_name) != -1:
                    return image

        return False

# ************************ Functions startin ***********************

    def __return_to_login_screen(self):
        for _ in range(2):
            if button := self.__find_button_by_text("Cancel login"):
                button.click()

    def login_with_swissid(self):
        """
        Logs into the app with swissid
        """
        if (button := self.__find_button_by_text("Login / registration")):
            button.click()

        if (button := self.__find_button_by_text("Login with SwissID")):
            button.click()

        if self.__find_text("Log in to Swiss Post"):
            input_fields = self.driver.find_elements(
                AppiumBy.CLASS_NAME, value=self.input_field_class)

            input_fields[0].send_keys(os.environ.get('swissid_username'))
            input_fields[1].send_keys(os.environ.get('swissid_password'))

            if button := self.__find_button_by_text("Continue"):
                button.click()

            if self.__find_text("Confirm with SwissID App"):
                logging.info("Waiting for swissid 2FA confirmation")

                while not self.__find_button_by_text("Create postcard"):
                    if self.__find_text("Cancelled"):
                        logging.error("The signing was cancelled from SwissID")
                        self.__return_to_login_screen()
                        return False
                logging.info("Successful signin over swissid for account %s", os.environ.get(
                    'swissid_username'))
                return True
            if self.__find_text("incorrect"):
                logging.info("Wrong credentials")
                self.__return_to_login_screen()
                return False
        else:
            logging.error("Not on login screen")

        return False

    def is_logged_in(self):
        """
        Function to check if a user is logged in already
        """
        if (self.__find_button_by_text("Login / registration")):
            return False

        if (self.__find_button_by_text("Login with SwissID")):
            return False

        if self.__find_text("Log in to Swiss Post"):
            return False

        return True

    def __insert_image_into_postcard(self, image_name: str):
        if button := self.__find_button_by_text("Select image"):
            button.click()

        if button := self.__find_button_by_text("Allow"):
            button.click()

        # Switch to the download section if neccessary
        if self.__find_text("Recent"):
            show_roots_xpath = '//android.widget.ImageButton[@content-desc="Show roots"]'
            burger_menu = self.driver.find_element(
                AppiumBy.XPATH, value=show_roots_xpath)
            burger_menu.click()
            if text := self.__find_text("Downloads"):
                text.click()

        if image := self.__find_image(image_name):
            image.click()
        else:
            logging.error("Image with name %s not found", image_name)

        if button := self.__find_text("N"):
            button.click()

        if button := self.__find_button_by_text("OK"):
            logging.warning(
                "Low resolution warning received for image %s", image_name)
            button.click()

    def __enter_recipient(self, recipient: Recipient):
        if button := self.__find_button_by_text("Recipient"):
            button.click()

        input_fields = self.driver.find_elements(
            AppiumBy.CLASS_NAME, value=self.input_field_class)

        first_name_field_id = 3
        last_name_field_id = 4
        street_field_id = 5
        postcode_field = 6

        input_fields[first_name_field_id].send_keys(recipient.first_name)
        input_fields[last_name_field_id].send_keys(recipient.last_name)
        input_fields[street_field_id].send_keys(recipient.address)
        input_fields[postcode_field].send_keys(recipient.postal_code)

        # Check for location select
        if self.__find_text("Select location"):
            if button := self.__find_text(recipient.location):
                button.click()
            else:
                logging.error(
                    "The location %s and postal code %s do not combine",
                    recipient.location, recipient.postal_code
                )
                return False

        if button := self.__find_button_by_text("Next"):
            button.click()

    def __enter_message(self, message):
        if button := self.__find_button_by_text("Enter message"):
            button.click()

        input_fields = self.driver.find_elements(
            AppiumBy.CLASS_NAME, value=self.input_field_class)

        input_fields[0].send_keys(message)

        for _ in range(3):
            if button := self.__find_text("N"):
                button.click()

    def send_free_postcard(self, postcard: Postcard):
        """
        Sends a free postcard over the api

        Args:
            image_name (str): the name of the image to use
        """
        if not self.__find_button_by_text("Create free postcard"):
            sleep(10)

        if button := self.__find_button_by_text("Create free postcard"):
            button.click()

        self.__insert_image_into_postcard(postcard.image_location)

        if button := self.__find_button_by_text("Next"):
            button.click()

        self.__enter_recipient(postcard.recipient)
        self.__enter_message(postcard.description)

        if button := self.__find_button_by_text("Next"):
            button.click()

        if gtg_accept_switch := self.driver.find_element(AppiumBy.CLASS_NAME, self.switch_class):
            gtg_accept_switch.click()

        if button := self.__find_button_by_text("Send it now for free"):
            button.click()

        if button := self.__find_button_by_text("Home"):
            button.click()

        return True

    def check_if_waiting(self):
        """
        A function that checks if the feature is disabled for a certain time.
        Returns the time remaining in seconds.
        """
        if button := self.__find_button_by_text("Available again from"):
            regex = re.compile(
                r'.+(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})\sat\s(?P<hour>\d{2}):(?P<minute>\d{2}).*')
            extracted = [m.groupdict() for m in regex.finditer(button.text)]
            if len(extracted) == 1:
                match = extracted[0]
                available_again = datetime(int(match["year"]), int(match["month"]), int(
                    match["day"]), int(match["hour"]), int(match["minute"]))
                now = datetime.now()
                duration = available_again - now

                if duration.days < 0:
                    return 0

                return duration.seconds

        return 0
