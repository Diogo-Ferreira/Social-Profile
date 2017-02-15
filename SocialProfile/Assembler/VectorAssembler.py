import json

import sys

import pika

from SocialProfile.AbstractMiner import AbstractMiner
from SocialProfile.Manager.MinerManager import MinerManager


class VectorAssembler(AbstractMiner):
    """
    A vector assembler groups mining data by,
     the data comes from the tag miners.

    Once the data regrouped, it is send to the job_done queue
    """
    def __init__(self, queue):
        """
        :param queue: the name of this assembler queue
        """
        self.queue = queue
        self.name = "ASM %s" % queue

        # List of current jobs
        self.current_jobs = {}

        super(VectorAssembler, self).__init__()
        self.channel.exchange_declare(exchange='vector_assemblers_ex', type='direct')
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.queue_bind(exchange='vector_assemblers_ex', queue=queue, routing_key=queue)
        self.channel.basic_consume(self._on_paquet_arrived, queue=queue)
        self.channel.start_consuming()

    def _on_paquet_arrived(self, ch, method, properties, body):

        ch.basic_ack(delivery_tag=method.delivery_tag)

        json_body = json.loads(body.decode(encoding='UTF-8'))

        self._log("New packet from miner %s with value %s" % (str(json_body['tag_miner']), str(json_body)))

        self._handle_job(json_body)

    def _get_job_miners_count(self, job_id):
        """Gets de count of different miners which contributed to the vec"""
        miners = set(
            [history['tag_miner'] for history in self.current_jobs[job_id]["history"]]
        )
        return len(miners)

    def _current_job(self, job):
        return self.current_jobs[job['job_id']]

    def _handle_job(self, job):
        """
        Checks if the received job is already in the system,
        create ones if not, merge is values if yes.

        Creates also a job history, which is useful to count
        the numbers of miners which contributed,
        in order to know if our likelihood vector is done

        :param job: received message (dictionary)
        :return:

        """
        if job['job_id'] in self.current_jobs:
            # Jobs already in system, let's updated it
            for tag, value in job['likelihood_vec'].items():

                if tag not in self._current_job(job)["likelihood_vec"]:
                    self._current_job(job)["likelihood_vec"][tag] = value
                    self._current_job(job)["history"].append(job)

            if self._get_job_miners_count(job['job_id']) >= MinerManager.tag_len():
                self._publish_job(job['job_id'])

        else:
            self.current_jobs[job['job_id']] = {
                "likelihood_vec": job['likelihood_vec'],
                "history": [job],
                "token": job['token'],
                "job_id": job['job_id'],
                "user_id": job['user_id']
            }

    def _publish_job(self, id):
        """
        Send the finished job to the job done queue
        with the following format:
            likelihood_vec: dict,
            job_id: str,
            token: str,
            user_id: str

        It also delete the job from the current_jobs dict

        :param id: job id
        """
        job = self.current_jobs[id]
        del self.current_jobs[id]

        self.channel.basic_publish(
            exchange='',
            routing_key='job_done',
            body=json.dumps({
                "likelihood_vec": job['likelihood_vec'],
                "job_id": job['job_id'],
                "token": job['token'],
                "user_id": job['user_id']
            }),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        self._log("DONE !")


if __name__ == "__main__":
    VectorAssembler(sys.argv[1])
