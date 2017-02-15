import json

from SocialProfile.AbstractMiner import AbstractMiner


class Logger(AbstractMiner):
    """
    Logger service, basically prints everything
     he gets with the following convention : [ miner name] date message.

     Therefore each message should be structured as : {
        "name": the miner name,
        "when": the date when the print was taken,
        "message": well, the message I guess
     }

    """

    def __init__(self,filter = ''):
        super(Logger, self).__init__()
        self.filter = filter
        self.channel.queue_declare(queue='log')
        self.channel.basic_consume(self._on_paquet_arrived, queue='log')
        self.channel.start_consuming()

    def _on_paquet_arrived(self, ch, method, properties, body):
        log = json.loads(body.decode(encoding='UTF-8'))
        if log['miner'] in self.filter or self.filter is "":
            print("[ %s ] %s %s" % (log['miner'],log['when'],log['message']))
        ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    Logger()