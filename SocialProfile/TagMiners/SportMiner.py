import json

from SocialProfile.TagMiners.TagMiner import TagMiner


class SportTagMiner(TagMiner):
    """
    sport->raquettes
    sport->aquatique
    sport->décontracté

    """

    def __init__(self):
        super(SportTagMiner, self).__init__("sport")

    def _on_paquet_arrived(self, ch, method, properties, body):

        ch.basic_ack(delivery_tag=method.delivery_tag)

        json_body = json.loads(body.decode(encoding='UTF-8'))

        self._log("new job arrived (%s)" % json_body)

        likelihood_vec = {
            "sport->raquettes ": 0,
            "sport->aquatique": 0,
            "sport->decontracte": 0,
        }

        json_body['likelihood_vec'] = likelihood_vec

        self._send_to_assembler(json_body)


if __name__ == "__main__":
    SportTagMiner()