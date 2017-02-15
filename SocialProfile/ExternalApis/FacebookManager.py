import facebook


class FacebookManager(object):
    def __init__(self, token):
        """
        We don't load the artists,movies... here, because maybe we don't need it,
        so it will be unnecessary to load them in the constructor
        """
        self.graph = facebook.GraphAPI(access_token=token)

        self._music_artists = None
        self._movies = None
        self._events = None
        self._sports = None
        self._posts = None
        self._pages = None
        self._profile = None

        # checks if token is valid
        try:
            self.feed
        except Exception as e:
            raise e

    def is_post_about(self, post, subject):

        subject = subject.lower()

        # If the post is a youtube, soundcloud,.. share
        if "status_type" in post and post['status_type'] is ("video" or "link") and subject in post['name'].lower():
            return True

        # if the user posts something with the subject on it
        if "message" in post and subject in post['message'].lower():
            return True

        return False

    @staticmethod
    def get_profile(token):
        graph = facebook.GraphAPI(access_token=token)
        return graph.get_object('me?fields=email,id,name')

    @property
    def feed(self, limit=20):
        if not self._posts:
            self._posts = self.graph.get_connections("me", "feed", limit=limit)
        return self._posts['data']

    @property
    def music_artists(self):
        if not self._music_artists:
            self._music_artists = self.graph.get_connections("me", "music", limit=1000)

            """
            Checks wall for every listening to..., and group it.
            Reminder: currently it isn't possible to retrieve user's feelings, but
            we can get the listening to, and watching to by extracting them from the post story.
            """
            artists = {}
            for post in [p for p in self.feed if "story" in p and "listening to" in p["story"]]:

                # TODO: check if this artist is already liked

                name = post["story"].split("listening to ")[1][:-1]

                # Tries to detect the artist
                if 'by' in name:
                    name = name.split("by ")[1]

                if name in artists:
                    artists[name]["from_feed"].append({
                        "from_post": post,
                        "name": name
                    })
                else:
                    artists[name] = {
                        "from_feed": [{
                            "from_post": post,
                            "name": name
                        }]
                    }

            self._music_artists['data'] += [{"name": k, "from_feed": v["from_feed"]} for k, v in artists.items()]
        return self._music_artists['data']

    @property
    def movies(self):
        if not self._movies:
            self._movies = self.graph.get_connections("me", "movies")

            # also cheking wall for every watching...
            to_add = [
                {"name": post["story"].split("watching")[1][:-1], "from_post": post}
                for post in self.feed if "story" in post and "watching" in post["story"]
                ]

            self._movies['data'] += to_add

        return self._movies['data']

    @property
    def sports(self):
        if not self._sports:
            self._sports = self.graph.get_connections("me", "sports")
        return self._sports['data']

    @property
    def events(self):
        if not self._events:
            self._events = self.graph.get_connections("me", "events?fields=description,name,rsvp_status")
        return self._events['data']

    @property
    def pages(self):
        if not self._pages:
            self._pages = self.graph.get_connections("me", "likes")
        return self._pages

    @property
    def food_pages(self):
        if not self._pages:
            self.pages

        keywords = "restaurant beverage food eating fast-food pizza italian".split()

        def filter_restaurants(page):
            if page["category"].lower() in keywords:
                return True
            elif 'category_list' in page:
                matches = [cat for cat in page['category_list'] if
                           set(cat['name'].lower().split()).intersection(keywords)]

                if len(matches) > 0:
                    return True

            return False

        return [data for data in self._pages["data"] if 'category' in data and filter_restaurants(data)]


if __name__ == "__main__":
    fb = FacebookManager("YOUR TOKEN HERE")

    for movie in fb.movies:
        print(movie)
