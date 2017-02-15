import abc
import json
from datetime import datetime

import pika

from SocialProfile.Config import Config


class AbstractMiner(object):
    def __init__(self):
        """
        Setup connection to the broker.
        """
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=Config.RABBITMQ_SERVER_IP
        )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='log')

    @abc.abstractmethod
    def _on_paquet_arrived(self, ch, method, properties, body):
        """
        Callback for rabbitmq arriving paquets, every miner should
        implement this method to decicde what it will do with the message.
        """

    def _send_progress(self, progrees_percent, id, message=""):
        """
        Sends the current mining progress to a specific queue
        :param progrees_percent:
        :param message:
        :return:
        """

        try:
            self.name
        except AttributeError:
            self.name = str(self.__class__.__name__)

        body = {
            "miner": self.name,
            "progress": progrees_percent,
            "message": message,
            "id": id
        }

        self.channel.basic_publish(
            exchange='',
            routing_key='progress',
            body=json.dumps(body),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def _log(self, log_message, print_in_console=True, id=None):
        """
        Sends message to the log miner queue, the function gets
        the name of the miner, and the automaticaly

        :param log_message: message to log
        :return:
        """
        try:
            self.name
        except AttributeError:
            self.name = str(self.__class__.__name__)

        body = {
            "miner": self.name,
            "when": datetime.now().strftime("%H:%M:%S"),
            "message": log_message,
            "id": id
        }

        self.channel.basic_publish(
            exchange='',
            routing_key='log',
            body=json.dumps(body),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        if print_in_console:
            print(body["message"])


if __name__ == '__main__':
    pass
