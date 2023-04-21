import logging
from datetime import datetime

from adb_automations import ADBAutomationHandler
from appium_automations import AppiumAutomationHandler, Postcard


class AutomationHandler():
    """
    Class to handle and coordinate automations
    """

    def __init__(self, clear_downloads_folder=True):
        # Initialize the handlers
        self.adb_handler = ADBAutomationHandler()
        self.appium_handler = AppiumAutomationHandler(
            self.adb_handler.get_device_id())
        self.clear_downloads_folder = clear_downloads_folder

        self.adb_handler.prepare_vm()

        # Login the user if he isn't already
        self.logged_in = self.appium_handler.is_logged_in()
        if not self.logged_in:
            self.login()

        # Initialize the delay for sending another postcard
        self.time_remaining = self.appium_handler.check_if_waiting()
        self.updated_timestamp = datetime.now()

    def login(self):
        """
        Logs in the user into the application
        """
        if not self.logged_in:
            self.logged_in = self.appium_handler.login_with_swissid()
        else:
            logging.error("User is already logged in when attempting login")

    def send_postcard(self, postcard: Postcard):
        """
        Sends a postcard if the user is logged in

        Args:
            image_location (str): The file location of the image
            recipient (Recipient): The recipient of the postcard
            message (str): The message to put on the postcard
        """
        if not self.logged_in:
            logging.error("Failed to send postcard, not logged in")
            return False

        if self.appium_handler.check_if_waiting() != 0:
            logging.info(
                "Need to wait %s seconds before sending another postcard", self.time_remaining)
            return False

        self.adb_handler.upload_image(
            postcard.image_location, clear_downloads_folder=self.clear_downloads_folder)

        outcome = self.appium_handler.send_free_postcard(postcard)

        return outcome

    def get_timeout_seconds(self):
        """
        A function that returns the time remaining before being able to send a new postcard

        Returns:
            _type_: _description_
        """
        return self.appium_handler.check_if_waiting()
