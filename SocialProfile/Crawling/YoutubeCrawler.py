from urllib.parse import urlparse, parse_qs

from googleapiclient.discovery import build

from SocialProfile.Crawling import FilteringTools


class YoutubeCrawler:

    def __init__(self):
        self.videos = {}
        self._init_api()

    def crawl(self, link):
        """
        Retrieves meta data from video
        :param link: the youtube video link
        :return:
        """
        # get video id from link
        link = parse_qs(urlparse(link).query)['v'][0]

        if link not in self.videos:
            self.videos[link] = YoutubeVideo(link, self.api)
        return self.videos[link]

    def _init_api(self):
        self.api = build("youtube", "v3", developerKey="AIzaSyBRNXAIXuKO1qFRpiywKL9f5P9rtIsdGmM")


class YoutubeVideo:
    def __init__(self, id, api):
        self.id = id
        self.api = api
        self._category_id = None
        # Allows to cache, and only retrieve if needed
        self._comments = []
        self._description = []
        self._category = []
        self._tags = []

    def __eq__(self, other):
        return self.link == other

    @property
    def comments(self):
        if not self._comments:
            self._load_video_comments()
        return self._comments

    def _load_video_comments(self):
        results = self.api.commentThreads().list(
            part="snippet",
            videoId=self.id,
            textFormat="plainText",
            maxResults=100
        ).execute()

        for item in results["items"]:
            comment = item["snippet"]["topLevelComment"]
            self._comments.append({
                "comment": comment,
                "author": comment["snippet"]["authorDisplayName"],
                "text": FilteringTools.remove_simple_smileys(
                    FilteringTools.remove_emoji(comment["snippet"]["textDisplay"]))
            })

    def _load_video_meta(self):
        result = self.api.videos().list(
            part='snippet',
            id=self.id
        ).execute()

        if len(result['items']) > 0:
            data = result['items'][0]['snippet']

            if result:
                self._description = data['description']
                self._tags = data['tags']
                self._category_id = data["categoryId"]
            return data

        return None

    def _load_category(self):

        if not self._category_id:
            self._load_video_meta()

        result = self.api.videoCategories().list(
            part='snippet',
            id=self._category_id
        ).execute()

        self._category = result['items'][0]['snippet']['title']

    @property
    def description(self):
        if not self._description:
            self._load_video_meta()
        return self._description

    @property
    def category(self):
        if not self._category:
            self._load_category()
        return self._category

    @property
    def tags(self):
        if not self._tags:
            self._load_video_meta()
        return self._tags


if __name__ == "__main__":
    crawler = YoutubeCrawler()

    video = crawler.crawl("https://www.youtube.com/watch?v=y4mxxw6frwm")

    for comment in video.comments: print("%s\n===" % comment["text"])

    # [print("%s\n===" % comment["text"]) for comment in video.comments]
