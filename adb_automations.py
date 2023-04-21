"""
Module containing all automation of ADB interaction
"""

import logging
from ppadb.client import Client as AdbClient
from ppadb.device import Device


class ADBAutomationHandler:
    """
    A class to automate all interactions made over ADB
    """

    def __init__(self, device_id=0):
        adb = AdbClient(host='127.0.0.1', port=5037)
        devices = adb.devices()
        self.device: Device = devices[device_id]
        logging.info("ADB is now connected to device %s",
                     self.device.get_serial_no())

    def get_device_id(self):
        """
        Returns the id of the connected device

        Returns:
            str: The id of the device
        """
        return self.device.get_serial_no()

    def prepare_vm(self):
        """
        Prepares the device connected over adb, reinstalling postcardcreator and starting it
        """

        # Check if postcard creator is installed
        serial_num = self.device.get_serial_no()
        is_pcc_installed = self.device.is_installed('ch.post.it.pcc')

        if not is_pcc_installed:
            self.device.install('./application/postcardcreator.apk')

        logging.info('Postcardcreator is installed on device %s', serial_num)

        self.device.shell('monkey -p ch.post.it.pcc 1')

        logging.info('Postcardcreator is now opened on device %s', serial_num)

        return True

    def upload_image(self, image_name, clear_downloads_folder=True):
        """
        Uploads the given image to the downloads folder of the connected device
        Clears all files in downloads on the device if specified

        Args:
            image_name (_type_): _description_
        """
        if clear_downloads_folder:
            self.device.shell('rm -r /storage/emulated/0/Download/*')

        self.device.push(f'images/{image_name}',
                         f'/storage/emulated/0/Download/{image_name}')

        logging.info('Uploaded image %s to the virtual device', image_name)
