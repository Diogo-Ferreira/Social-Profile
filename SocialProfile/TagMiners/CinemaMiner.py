import json

import asyncio

import math

from SocialProfile.Crawling.FilteringTools import FilteringTools
from SocialProfile.ExternalApis.MovieDbManager import MovieDBManager
from SocialProfile.Nlp.NLP import NLP
from SocialProfile.TagMiners.MappingValues import MOVIEDB_TO_MCARS_MAP
from SocialProfile.TagMiners.TagMiner import TagMiner


class CinemaTagMiner(TagMiner):
    POST_SENTIMENT_COEFF = 0.2
    BASE_COEFF = 0.1
    REVIEW_COSINE_LIMIT = 0.5
    SHARE_COEFF = 0.2

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.nlp = NLP(load_classifier=True)
        self.movie_db = MovieDBManager()
        super(CinemaTagMiner, self).__init__("cinema")

    def _get_tags(self):
        return {
            "cinema->action": 0.5,
            "cinema->thriller": 0.5,
            "cinema->romance": 0.5,
            "cinema->comedie": 0.5
        }

    def _on_paquet_arrived(self, ch, method, properties, body):

        json_body = json.loads(body.decode(encoding='UTF-8'))

        self.mining_details = {}

        self._log("new job arrived (%s)" % json_body)

        self.likelihood_vec = self._get_tags()

        not_normalised_vec = self._process_movies()

        sign = lambda x: (1, -1)[x < 0]

        for tag, value in not_normalised_vec.items():
            self.likelihood_vec[tag] += sign(value) * self.normalize_value(abs(value), y_max=0.5)

        json_body['likelihood_vec'] = self.likelihood_vec

        self._log(self.likelihood_vec)

        self.current_progress = 100

        self._send_mining_details("cinema", {k.replace(".", " "): v for k, v in self.mining_details.items()})

        return json_body

    def _process_movies(self):
        movies = self.fb.movies

        tmp_vec = {k: 0 for k, v in self.likelihood_vec.items()}

        if len(movies) > 0:
            progress_increment = 90.0 / len(movies)

        async def __tag_movies(movies, tmp_vec):
            """
            For each movie, we tag it with tmdb
            :param movies: movies names
            :param tmp_vec:
            :return:
            """
            tasks = [self.movie_db.tag_movie(m['name']) for m in movies]

            for response in await asyncio.gather(*tasks):
                if "error" not in response and response:
                    movie_db_genres = [g['name'] for g in response["genres"]]

                    mcars_tags = self._map_to_mcars(movie_db_genres, MOVIEDB_TO_MCARS_MAP)

                    movie = next(m for m in movies if m["name"] == response["name"])

                    movie["tmdb"] = response

                    movie["mcars_tags"] = mcars_tags

                    movie['actors'] = response['actors']

                    movie['keywords'] = response['keywords']

                    self.mining_details[response["name"].lower()] = {
                        "mcars": mcars_tags,
                        "tmdb": response
                    }

                    if "from_post" in movies:
                        self.mining_details[response["name"].lower()]["from_post"] = movie["from_post"]

                    sentiment = self._analyse_wall_for_movie(movie)

                    for k, v in tmp_vec.items():
                        if k in movie['mcars_tags'] and movie['mcars_tags'][k]:
                            tmp_vec[k] += sentiment

                    self._log("TMP VEC %s" % tmp_vec)

                    self.update_progress(progress_increment)

        self.loop.run_until_complete(__tag_movies(movies, tmp_vec))

        return tmp_vec

    def _analyse_wall_for_movie(self, movie):
        """
        Checks if the user talked about the movie on his feed
        :param movie: movie name
        :return:
        """
        movie_name = movie['name'].lower()

        posts = self.fb.feed

        sentiment = self.BASE_COEFF

        if 'from_post' in movie and 'message' in movie['from_post'] \
                and not self.nlp.binary_sentiment_of_post(movie['from_post']['message']):
            sentiment = 0

        self._log(movie_name)

        self.mining_details[movie_name]["posts"] = []

        for post in posts:

            # if the message is big, it can be a review, but we need to be more sure about it
            if 'message' in post and len(post['message'].split()) > 20:

                clean_message = FilteringTools.full_cleaning(post['message'])

                # we need the text in english for the cosine similarity
                translated_message = self.nlp.translate(clean_message.lower(), to='en')

                self._log(translated_message)

                # Get words of message, minus the stop words
                post_words = self.nlp.word_vector(translated_message, lang='en')

                movie_keywords = [m['name'].lower() for m in movie['keywords']]

                movie_actors = [a['name'].lower() for a in movie['actors'][:5]]

                movie_characters = [a['character'].lower() for a in movie['actors'][:5]]

                keywords_and_post = [words for segments in movie_keywords for words in segments.split()]

                similarity = self.cosine_similarity_of_words(post_words, keywords_and_post)

                # in case if something goes wrong..., we never know what we can have in the event description
                if math.isnan(similarity):
                    similarity = 0

                self._log("similarity of posts %s is %s " % (translated_message[:10], similarity))

                """
                Warning: this part is very experimental, and may cause many errors, maybe it will be wise to cut
                this part from the production.

                If the user speaks about the actor, or the character of the movie, it makes sense that he speaks
                about the movie, on the contrary we can't have the same reflexion for the keyword, because they're
                more general, that's why we calculate a cosine similarity between them.
                """
                if similarity > self.REVIEW_COSINE_LIMIT or any(name for name in movie_actors + movie_characters if name in post['message']):
                    sentiment += self._analyze_post_sentiment(post, movie_name)

                    self.mining_details[movie_name]["posts"].append({
                        "post": post,
                        "similarity": similarity,
                        "post_words": post_words,
                        "sentiment": sentiment
                    })

            # Since the message is short, we only check if the name of the movie is on the message
            elif self.fb.is_post_about(post, movie_name):
                sentiment += self._analyze_post_sentiment(post, movie_name)

                self.mining_details[movie_name]["posts"].append({
                    "post": post,
                    "sentiment": sentiment
                })

        return sentiment

    def _analyze_post_sentiment(self, post, movie_name):

        sentiment_out = 0

        clean_message = FilteringTools.full_cleaning(post['message'])

        # Since we trained our classifier with french comments from allocine, lets translate all in french
        msg_to_analyze = self.nlp.translate(clean_message.replace(movie_name, " sam"), to='fr')

        if self.nlp.classify_post(msg_to_analyze) is 'pos':
            self._log("talked good about %s from %s" % (movie_name, post['message']))
            sentiment_out += self.POST_SENTIMENT_COEFF
        else:
            self._log("talked bad about %s from %s" % (movie_name, post['message']))
            sentiment_out -= self.POST_SENTIMENT_COEFF

        # if the post is a video share
        if 'status_type' in post and post['status_type'] in "link video":
            sentiment_out += self.SHARE_COEFF

        return sentiment_out


if __name__ == "__main__":
    CinemaTagMiner()
