import json

from SocialProfile.TagMiners.TagMiner import TagMiner


class FoodMiner(TagMiner):
    EACH_RESTAURANT_PONDERATION = .5

    def __init__(self):
        super(FoodMiner, self).__init__("food")

    def _on_paquet_arrived(self, ch, method, properties, body):
        json_body = json.loads(body.decode(encoding='UTF-8'))

        self._log("new job arrived (%s)" % json_body)

        restaurants = self.fb.food_pages

        normalized_value = self.normalize_value(len(restaurants) * self.EACH_RESTAURANT_PONDERATION, y_max=0.5)

        self.likelihood_vec = self._get_tags()

        self.likelihood_vec["restaurants"] += normalized_value

        self._log(self.likelihood_vec)

        json_body['likelihood_vec'] = self.likelihood_vec

        return json_body

    def _get_tags(self):
        return {
            "restaurants": 0.5
        }


if __name__ == "__main__":
    FoodMiner()
