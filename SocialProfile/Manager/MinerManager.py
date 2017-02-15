import json
import uuid

import pika

from SocialProfile.Config import Config
from SocialProfile.AbstractMiner import AbstractMiner
from SocialProfile.ExternalApis import FacebookManager


class MinerManager(AbstractMiner):
    def __init__(self):
        super(MinerManager, self).__init__()
        self.channel.queue_declare(queue='input_queue', durable=True)
        self._prepare_queues()
        self.channel.basic_consume(self._on_paquet_arrived, queue='input_queue')
        self.channel.start_consuming()

    def _on_paquet_arrived(self, ch, method, properties, body):
        self._log("new user arrived with token %s" % str(body), id=body.decode(encoding='UTF-8'))

        job = self._create_job(body.decode(encoding='UTF-8'))

        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.channel.basic_publish(exchange='tag_miners_ex',
                                   routing_key='',
                                   body=json.dumps(job),
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   ))

    def _create_job(self, fb_token):
        """
        Creates a new Social-Profile job for the given token.
        :param fb_token:
        :return:
        """

        """
        TODO: Currently the token validation is done by the tag miners, but it should be here logically,
        so if the token is invalid, the manager should deny the processing of this token and no longer
        continue it.
        """

        # Getting facebook user id
        try:
            profile = FacebookManager.FacebookManager.get_profile(fb_token)
        except:
            profile = {'id': '-1'}

        out = {
            "job_id": str(uuid.uuid4()),
            "token": str(fb_token),
            "vec_asm": self.vec_asm_queues[self.current_vec_asm_queue % len(self.vec_asm_queues)],
            "user_id": profile['id']
        }
        self.current_vec_asm_queue += 1
        return out

    @staticmethod
    def tag_len():
        return 4

    def _create_tag_queue(self, miner):
        self.channel.queue_declare(queue='miner_tag_queue_%s' % miner['tag'], durable=True)
        self._log("Queue %s created" % miner['tag'])

    def _create_asm_queue(self, vec_asm):
        self.channel.queue_declare(queue=vec_asm['queue'], durable=True)
        self.vec_asm_queues.append(vec_asm['queue'])
        self._log("Queue %r created" % vec_asm['queue'])

    def _prepare_queues(self):
        """
        For each tag miner, we create a queue,
        base on the architecture config
        """

        [self._create_tag_queue(miner) for miner in Config.ARCHITECTURE['tag_miners']]

        self.channel.exchange_declare(exchange='tag_miners_ex', type='fanout')
        self.vec_asm_queues = []
        self.current_vec_asm_queue = 0

        [self._create_asm_queue(vec_asm) for vec_asm in Config.ARCHITECTURE["vector_assemblers"]]

        self.channel.exchange_declare(exchange='vector_assemblers_ex', type='direct')

        self.channel.queue_declare(queue='job_done', durable=True)

        self.channel.queue_declare(queue='progress', durable=False)

        self.channel.queue_declare(queue='job_errors', durable=True)

        self.channel.queue_declare(queue='mining_details', durable=True)


if __name__ == "__main__":
    MinerManager()
