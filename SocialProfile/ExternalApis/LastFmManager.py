import json

import aiohttp


class LastFmManager(object):
    # TODO: put this on secrets file
    API_KEY = ""

    def __init__(self):
        self.cache = {}

    async def top_artists(self, limit=100):
        """
        Gets the top :limit: artists from last.fm service, beware that this method
         is async and should therefore be called from an asyncio loop
        :param limit:
        :return:
        """
        url = "http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&limit=%s&api_key=%s&format=json" % (
            limit, self.API_KEY)

        # TODO: replace with client session, but not urgent
        async with aiohttp.request('GET', url) as response:
            raw_html = await response.read()
            try:
                out = json.loads(raw_html.decode(encoding='UTF-8'))

                if "error" in out:
                    return {"error": "404"}
                elif "artists" in out:
                    return {"artists": [t['name'] for t in out['artists']['artist']]}
                else:
                    return {"error": "unknown"}
            except Exception as e:
                print(e)

    async def tags_of(self, artist_name, limit=5):
        """
        Tags an artist with the last.fm service, beware that this method
         is async and should therefore be called from an asyncio loop
        :param limit:
        :return:
        """
        print("Searching for %s" % artist_name)
        if artist_name not in self.cache:
            self.cache[artist_name] = await self._fetch(artist_name, limit)

        return self.cache[artist_name]

    async def _fetch(self, artist_name, limit):
        """
        Make the http request to the last.fm top tags of artist route, with aiohttp.
        :param artist_name:
        :param limit:
        :return: dict("tags":...,"name":...")
        """
        urlified_name = artist_name.replace(' ', '%20')
        url = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist=%s&api_key=%s&format=json" % (
            urlified_name, self.API_KEY)

        # TODO: replace with client session, but not urgent
        async with aiohttp.request('GET', url) as response:
            try:
                raw_html = await response.read()
                print("Received data for %s " % artist_name)
                try:
                    out = json.loads(raw_html.decode(encoding='UTF-8'))

                    if "error" in out and out['error'] is '6':
                        return {"error": "404"}
                    elif "toptags" in out:
                        return {
                            "tags": [t['name'] for t in out['toptags']['tag']][:limit],
                            "name": artist_name
                        }
                    else:
                        return {"error": "unknown"}
                except Exception as e:
                    print(e)
            except Exception as e:
                print(str(e))
                return {
                    "error": "timeout"
                }