from atmdb import TMDbClient


class MovieDBManager(object):

    API_KEY = ''

    def __init__(self):
        self.client = TMDbClient(api_token=self.API_KEY)

    async def tag_movie(self, movie_name):
        """
        Tags a movie with the tmdb service, beware that this method
         is async and should therefore be called from an asyncio loop
        :param movie_name:
        :return: dict(
            "name": ...,
            "tmdb_id": ...,
            "imdb_id": ...,
            "genres": ...,
            "keywords": ...,
            "actors" : ...
        )
        """

        print(movie_name)

        movie_search_data = await self.client.find_movie(query=movie_name)

        if movie_search_data:
            #we only care for the best match
            movie_id = movie_search_data[0].id_

            #Movie data
            url = self.client.url_builder('movie/{movie_id}', dict(movie_id=movie_id))
            movie_data = await self.client.get_data(url)

            #KeyWords
            url = self.client.url_builder('movie/{movie_id}/keywords', dict(movie_id=movie_id))
            movie_keywords = await self.client.get_data(url)

            #actors
            url = self.client.url_builder('movie/{movie_id}/credits', dict(movie_id=movie_id))
            movie_credits = await self.client.get_data(url)

            return {
                "name": movie_name,
                "tmdb_id": movie_id,
                "imdb_id": movie_data['imdb_id'],
                "genres": movie_data['genres'],
                "keywords": movie_keywords["keywords"],
                "actors" : movie_credits['cast']
            }

        else:
            return {}

