import logging
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from time import sleep

from appium_automations import Postcard
from automation_handler import AutomationHandler


class PostcardScheduler:
    """
    A class for scheduling postcard sending
    """

    def __init__(self):
        self.automation_handler = AutomationHandler()
        self.queue = Queue()
        self.safe_timeout = 60
        self.worker_thread = Thread(target=self.__start)
        self.worker_thread.start()

    def schedule_postcard(self, postcard: Postcard):
        """
        Adds a postcard to the scheduler to be sent automatically once possible

        Args:
            postcard (Postcard): The postcard to append
        """

        # Compute the time when the postcard will be sent normally
        if (remaining_until_next := self.automation_handler.get_timeout_seconds()) != 0:
            time_remaining = remaining_until_next + \
                (self.queue.qsize() * (86400 + self.safe_timeout)) + self.safe_timeout
        else:
            time_remaining = remaining_until_next + \
                (self.queue.qsize() * (86400 + self.safe_timeout))

        time_sent = datetime.now() + timedelta(seconds=time_remaining)

        self.queue.put(postcard)

        logging.info(
            "Postcard added to the queue, it will be sent at %s", time_sent)

    def scheduler_run(self):
        """
        A run of the scheduler which sends the postcards
        """
        time_remaining = self.automation_handler.get_timeout_seconds()

        if time_remaining > 0:
            time_remaining += self.safe_timeout
            time_wakeup = datetime.now() + timedelta(seconds=time_remaining)
            logging.info(
                "Scheduler sleeping until %s when the next postcard can be sent", time_wakeup)

            sleep(time_remaining)
            return

        postcard_to_be_sent: Postcard = self.queue.get()

        logging.info("Sending postcard with description %s",
                     postcard_to_be_sent.description)

        self.automation_handler.send_postcard(postcard_to_be_sent)

    def estimated_queue_finish(self):
        """
        Return the amount of seconds remaining until the whole queue is finished

        Returns:
            int: the number of seconds as integer
        """
        return self.automation_handler.get_timeout_seconds() + \
            (self.queue.qsize() * (86400 + self.safe_timeout)) + self.safe_timeout

    def __start(self):
        logging.info("Scheduler started")
        while True:
            if self.queue.empty():
                logging.info("Queue is now empty, going to sleep")
            self.scheduler_run()
