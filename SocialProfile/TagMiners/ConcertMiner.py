import asyncio
import json

from SocialProfile.Crawling.FilteringTools import FilteringTools
from SocialProfile.ExternalApis.LastFmManager import LastFmManager
from SocialProfile.Nlp.NLP import NLP
from SocialProfile.TagMiners.MappingValues import LASTFM_TO_MCARS_MAP
from SocialProfile.TagMiners.TagMiner import TagMiner


class ConcertTagMiner(TagMiner):
    GEN_COEFF = 0.2
    POST_COEFF = 0.3
    SHARE_COEFF = 0.6

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.nlp = NLP()
        self.last_fm = LastFmManager()
        super(ConcertTagMiner, self).__init__("music")

    def _get_tags(self):
        return {
            "concert->rock": 0.5,
            "concert->techno": 0.5,
            "concert->hip-hop": 0.5,
            "concert->classique": 0.5
        }

    def _on_paquet_arrived(self, ch, method, properties, body):

        json_body = json.loads(body.decode(encoding='UTF-8'))

        self._log("new job arrived (%s)" % json_body)

        self.likelihood_vec = self._get_tags()

        not_normalised_vec = self._process_artists()

        sign = lambda x: (1, -1)[x < 0]

        for tag, value in not_normalised_vec.items():
            self.likelihood_vec[tag] += sign(value) * self.normalize_value(abs(value), y_max=0.5)

        json_body['likelihood_vec'] = self.likelihood_vec

        self._log(self.likelihood_vec)

        self.current_progress = 100

        return json_body

    def _process_artists(self):
        """
        Tags each artist with last fm (Final tags are from mcars)
        :return: one pos vec, and one neg vec
        """

        artists = self.fb.music_artists

        tmp_vec = {k: 0 for k, v in self.likelihood_vec.items()}

        artists_tags = {}

        if len(artists) > 0:
            progress_increment = 90.0 / len(artists)

        async def __tag_artists(artists, tmp_vec):

            """
            For each artist, tag him with the last fm service
            :param artists:
            :param tmp_vec:
            :return:
            """

            tasks = [self.last_fm.tags_of(a['name']) for a in artists]

            for response in await asyncio.gather(*tasks):

                if 'error' not in response:

                    self._log("Scruting %s" % response['name'])

                    mcars_tags = self._map_to_mcars(response['tags'], LASTFM_TO_MCARS_MAP)

                    artist = next(a for a in artists if a["name"] == response["name"])

                    artist['mcars_tags'] = mcars_tags

                    artist['tags'] = response['tags']

                    sentiment = self._analyse_wall(artist)

                    artists_tags[response["name"]] = {
                        "last_fm": response['tags'],
                        "mcars": mcars_tags,
                    }

                    if "from_feed" in artist:
                        sentiment *= len(artist["from_feed"])
                        artists_tags[response["name"]]["feed"] = artist["from_feed"]

                    self._log("sentiment of %s is %s" % (artist["name"], sentiment))

                    for k, v in tmp_vec.items():
                        if k in artist['mcars_tags'] and artist['mcars_tags'][k]:
                            tmp_vec[k] += sentiment
                    self._log("TMP VEC %s" % tmp_vec)
                else:
                    self._log("%s doesn't seem to exist, maybe it's a track ?" % (str(response)))

                self.update_progress(progress_increment)

        self.loop.run_until_complete(__tag_artists(artists, tmp_vec))

        self._send_mining_details("concerts", {k.replace(".", " "): v for k, v in artists_tags.items()})

        return tmp_vec

    def _analyse_wall(self, artist):
        """
        Check if the user talked about the artist on his feed
        :param artist:
        :return:
        """
        artist_name = artist['name'].lower()

        posts = self.fb.feed

        sentiment = self.GEN_COEFF

        self._log(artist_name)

        for post in posts:

            # if we catch the artist name in the post, we analyseit
            if 'message' in post and self.fb.is_post_about(post, artist_name):
                sentiment += self._analyze_post_sentiment(post, artist_name)

        return sentiment

    def _analyze_post_sentiment(self, post, artist_name):

        sentiment_out = 0

        clean_message = FilteringTools.full_cleaning(post['message'])

        # We do the sentiment analysis in english here, because you don't have any training data in fr
        msg_to_analyze = self.nlp.translate(clean_message.replace(artist_name, " sam"), to='en')

        if self.nlp.binary_sentiment_of_post(msg_to_analyze):
            self._log("talked good about %s from %s" % (artist_name, post['message']))
            sentiment_out += self.POST_COEFF
        else:
            self._log("talked bad about %s from %s" % (artist_name, post['message']))
            sentiment_out -= self.POST_COEFF

        if 'status_type' in post and post['status_type'] in "link video":
            sentiment_out += self.SHARE_COEFF

        return sentiment_out


if __name__ == "__main__":
    ConcertTagMiner()
