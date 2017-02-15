import asyncio
import json
import unittest

import pika

from SocialProfile.Config import Config
from SocialProfile.ExternalApis.LastFmManager import LastFmManager


class SocialProfileModulesUnitTests(unittest.TestCase):
    def test_last_fm(self):
        loop = asyncio.get_event_loop()
        last_fm = LastFmManager()

        async def _test_tags():

            # Let's first test with the king of pop
            response = await last_fm.tags_of("Michael Jackson")
            test_tags = ['pop', '80s', 'dance', 'soul', 'funk']

            self.assertIn('name',response,'Name of artist not in response !')
            self.assertIn('tags', response, 'Name of artist not in response !')
            self.assertEquals(test_tags,response['tags'],'Incorrect tags !')

            # Now let's test someone who doesn't exists
            response = await last_fm.tags_of("ijsdgisjdhijsihjijhd")
            self.assertIn('error', response, 'error tag not in response !')
            self.assertEquals("unknown", response['error'], 'Incorrect error message !')

        loop.run_until_complete(_test_tags())

    def test_tmdb(self):
        pass

    def test_youtube(self):
        pass

    def test_nlp(self):
        pass


class SocialProfileInfrastructureUnitTests(unittest.TestCase):
    def test_stress_pipeline(self):
        for i in range(5):
            self.test_pipeline()

    def test_pipeline(self):
        """
        Test that if we sent a test user, the system will work
        normally and send all tags with the value of 0.888
        :return:
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=Config.RABBITMQ_SERVER_IP))
        channel = connection.channel()

        channel.queue_declare(queue='input_queue', durable=True)

        token = "test"

        channel.basic_publish(
            exchange='',
            routing_key='input_queue',
            body=token,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        print(" [ UnitTest] Sent %r" % token)

        def _on_message(ch, method, properties, body):
            json_body = json.loads(body.decode(encoding='UTF-8'))

            if json_body['token'] == 'test':
                for tag, value in json_body['likelihood_vec'].items():
                    print("[ %s ] %s" % (tag, value))
                    self.assertEquals(0.888, value, 'Incorrect tag value !')
                channel.basic_cancel(consumer_tag="test_consume")

        channel.basic_consume(_on_message, consumer_tag="test_consume", queue='job_done')

        channel.start_consuming()

        connection.close()
