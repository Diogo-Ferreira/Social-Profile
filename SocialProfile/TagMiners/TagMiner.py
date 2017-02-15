import abc
import datetime
import json

import math
import pika

from SocialProfile.AbstractMiner import AbstractMiner
from scipy import spatial

from SocialProfile.ExternalApis.FacebookManager import FacebookManager


class TagMiner(AbstractMiner):
    def __init__(self, tag):
        self.tag = tag
        self._current_progress = 0
        self.send_details = True
        super(TagMiner, self).__init__()
        self.channel.exchange_declare(exchange='tag_miners_ex', type='fanout')
        self.channel.queue_declare(queue='miner_tag_queue_%s' % self.tag, durable=True)
        self.channel.queue_bind(exchange='tag_miners_ex', queue='miner_tag_queue_' + str(self.tag))
        self.channel.basic_consume(self.__on_paquet_arrived_pre_processing, queue='miner_tag_queue_' + str(self.tag))
        self.channel.start_consuming()

    def __on_paquet_arrived_pre_processing(self, ch, method, properties, body):
        """
        Checks if the fb token is valid, or a test token
        """

        json_body = json.loads(body.decode(encoding='UTF-8'))

        self.fb_token = json_body["token"]
        self.job_id = json_body["job_id"]
        self.current_progress = 0

        if json_body['token'] != "test":

            try:
                self.fb = FacebookManager(token=self.fb_token)
                data = self._on_paquet_arrived(ch, method, properties, body)
                self.__on_paquet_arrived_post_processing(data, ch, method, properties)
            except Exception as e:
                """
                Oops ! Something wrong occured, well the exception is going to job_errors
                queue, as for the likihood_vec, all values will be -1
                """
                self._log("error : %s" % str(e))
                self._send_error(json_body, e)
                json_body['likelihood_vec'] = {k: -1 for k, v in self._get_tags().items()}
                self.__on_paquet_arrived_post_processing(json_body, ch, method, properties)
        else:
            self._log("test !")
            tags = self._get_tags()
            json_body['likelihood_vec'] = {k: 0.888 for k, v in tags.items()}
            self.__on_paquet_arrived_post_processing(json_body, ch, method, properties)

    def __on_paquet_arrived_post_processing(self, data, ch, method, properties):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self._send_to_assembler(data)

    def _send_to_assembler(self, body):
        body['tag_miner'] = self.__class__.__name__
        self.channel.basic_publish(
            exchange='vector_assemblers_ex',
            routing_key=body["vec_asm"],
            body=json.dumps(body),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def _send_error(self, body, exception=None):
        body['tag_miner'] = self.__class__.__name__
        if exception:
            body['exception'] = str(exception)
        self.channel.basic_publish(
            exchange='',
            routing_key='job_errors',
            body=json.dumps(body),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def _send_mining_details(self, tag, details):
        """
        Sends mining details, in order the retrieve this details from some kind of gui
        :param tag:
        :param details:
        :return:
        """

        # if we don't need the details, we should not fill the queues for nothing
        if not self.send_details:
            return

        try:
            self.name
        except AttributeError:
            self.name = str(self.__class__.__name__)

        body = {
            "miner": self.name,
            "when": datetime.datetime.now().strftime("%H:%M:%S"),
            "tag": tag,
            "details": details,
            "token": self.fb_token,
            "job_id": self.job_id
        }

        self.channel.basic_publish(
            exchange='',
            routing_key='mining_details',
            body=json.dumps(body),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    @property
    def current_progress(self):
        return self._current_progress

    @current_progress.setter
    def current_progress(self, value):
        self._current_progress = value
        self._send_progress(self._current_progress, self.fb_token)

    def update_progress(self, value):
        self.current_progress += value
        self._send_progress(self._current_progress, self.fb_token)

    @abc.abstractmethod
    def _get_tags(self):
        """
        Gets the miner correspong tags dict
        :return:
        """

    @staticmethod
    def cosine_similarity_of_words(words_a, words_b):
        """
        Cosine similarity of 2 sets
        TODO: move this to the NLP class
        :param words_a:
        :param words_b:
        :return:
        """
        togheter = words_a + words_b

        count_in_a = [words_a.count(w) for w in togheter]

        count_in_b = [words_b.count(w) for w in togheter]

        return 1 - spatial.distance.cosine(count_in_a, count_in_b)

    @staticmethod
    def normalize_vec(vec, y_max=1.0):
        return [TagMiner.normalize_value(x, y_max) for x in vec]

    @staticmethod
    def normalize_value(value, y_max):
        return (1 - math.exp(-value)) * y_max

    @staticmethod
    def _map_to_mcars(tags, map):
        """
        Maps last fm tags to mcars tags
        :param tags: last fm tags
        :return: dict with mcars tag as key and occurences as value
        """

        out = {k: 0 for k, y in map.items()}

        for tag in tags:
            tag = str(tag).lower().replace("-", " ")
            for k, v in map.items():
                if tag in v:
                    out[k] += 1

        return out
