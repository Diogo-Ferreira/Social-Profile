import json
import re

from SocialProfile.Crawling.FilteringTools import FilteringTools
from SocialProfile.Crawling.LinkAnalyser import LinkAnalyser
from SocialProfile.Crawling.YoutubeCrawler import YoutubeCrawler
from SocialProfile.Nlp.NLP import NLP
from SocialProfile.TagMiners.MappingValues import EVENT_KEYWORDS
from SocialProfile.TagMiners.TagMiner import TagMiner


class EventTagMiner(TagMiner):
    """
    Analyses event, with a cosine similarity on each description
    """

    N_POST_TO_LIKE_IT = 5

    def __init__(self):
        self.nlp = NLP()
        self.yt_crawler = YoutubeCrawler()
        super(EventTagMiner, self).__init__("events")

    def _get_tags(self):
        return {
            "salon->livre": 0.5,
            "automobiles": 0.5,
            "soiree": 0.5,
            "exposition->peintures": 0.5,
            "exposition->culturelle": 0.5
        }

    def _on_paquet_arrived(self, ch, method, properties, body):

        json_body = json.loads(body.decode(encoding='UTF-8'))

        self.mining_details = {}

        self.token = json_body['token']

        self._log("new job arrived (%s)" % json_body, id=self.token)

        not_normalized = self._analyse_events()

        normalized = {k: 0.5 + self.normalize_value(v, y_max=0.5) for k, v in not_normalized.items()}

        self.likelihood_vec = normalized

        self._log(self.likelihood_vec, id=self.token)

        json_body['likelihood_vec'] = self.likelihood_vec

        self.current_progress = 100

        self._send_mining_details("events", {k.replace(".", " "): v for k, v in self.mining_details.items()})

        return json_body

    def _analyse_events(self):

        all_events = self.fb.events

        categorized_events = {k: [] for k, v in self._get_tags().items()}

        categorized_events["unknown"] = []

        if len(all_events) > 0:
            progress_increment = 90.0 / len(all_events)

        for event in all_events:

            cosine_scores = {}
            description = ""

            if "description" in event:
                description = event["description"].lower()

            content = "%s\n%s" % (event["name"].lower(), description)

            search = re.search("(?P<url>https?://[^\s]+)", content)

            """
            We check if there are some links on the description,
            we analyse each link in order to improve our classification,
            if a description contains a lot of soundcloud links for instance,
            it is more likely to be a party, club etc...
            """

            links = []

            if search:
                links.append(search.group("url"))

            self._log("links %s" % links, id=self.token)

            for link in links:
                link_meta = LinkAnalyser.analyse_link(link)
                if 'likeli_tag' in link_meta:

                    # if we have a yt video, we can add his description to the content to analyse it
                    if 'domain' in link_meta and link_meta['domain'] == 'youtube':
                        description = self.yt_crawler.crawl(link).description
                        content += "\n%s\n" % description

                    for tag in link_meta['likeli_tag']:
                        cosine_scores[tag] = 0.2

            # we don't need the links anymore, we can now fully clean the text
            content = FilteringTools.full_cleaning(content)

            # Translates content to french
            try:
                translated_description = self.nlp.translate(content, to='fr')
            except:
                translated_description = content

            """
            For each mcars tags about events (See MappingValues.py), we do a cosine similarity
            between the descriptions keywords (pre-processed) and the keywords of the current tag
            """

            event_keywords = self.nlp.word_vector(translated_description)

            for tag, keywords in EVENT_KEYWORDS.items():

                cosine = self.cosine_similarity_of_words(event_keywords, keywords)

                if cosine > 0:
                    self._log("cosine of %s for %s is %s " % (event['name'], tag, cosine), id=self.token)

                if tag not in cosine_scores:
                    cosine_scores[tag] = 0

                cosine_scores[tag] = cosine

            max_score_tag, max_score = max(cosine_scores.items(), key=lambda t: t[1])

            if max_score > 0:
                categorized_events[max_score_tag].append(event)
            else:
                categorized_events["unknown"].append(event)

            self.mining_details[event["name"].lower()] = {
                "event": event,
                "cosines": cosine_scores,
                "max_score_tag": max_score_tag,
                "max_score": max_score,
                "links": links,
                "event_keywords": event_keywords
            }

            self.update_progress(progress_increment)

        self._log("cosine analysis done", id=self.token)

        self._log({k: len(v) for k, v in categorized_events.items()}, id=self.token)

        # we assume that we need to go 5 times to that event in order to like it a lot
        tmp_vec = {k: len(categorized_events[k]) / self.N_POST_TO_LIKE_IT for k, v in self._get_tags().items()}

        return tmp_vec


if __name__ == "__main__":
    EventTagMiner()
