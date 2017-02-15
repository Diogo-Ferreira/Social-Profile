import pickle

from nltk.corpus import stopwords
from textblob import Blobber
from textblob.en.sentiments import NaiveBayesAnalyzer
from translation import bing


class NLP(object):
    def __init__(self, load_classifier=False):

        if load_classifier:
            self._load_classifier()
            print("classifier loaded !")

        self.tb = Blobber(analyzer=NaiveBayesAnalyzer())
        self.stop = set(stopwords.words('french'))
        self.stop_en = set(stopwords.words('english'))

    def sentiments_of_post(self, post):
        """
        Gives the TextBlob naive bayes sentiment of post

        The language should must be english
        :param post:
        :return:
        """
        sentiment = self.tb(post).sentiment

        if sentiment.classification == 'pos':
            return sentiment.p_pos
        else:
            return -1 * sentiment.p_neg

    def classify_post(self, post):
        """
        Classifies a post with the allocine classifier

        The language should must be french.
        :param post:
        :return:
        """
        if self.classifier is None:
            self.load_classifier()

        return self.classifier.classify(post)

    def binary_sentiment_of_post(self, post):
        """
        Returns a binary sentiment: pos or neg ? Always with naives bayes

        The language should must be english

        :param post:
        :return: True if pos, False if neg
        """
        return self.sentiments_of_post(post) > 0

    def word_vector(self, sentence, lang='fr'):
        """
        Creates a word vector from the sentence, it also removes
        all stop words in the specified language.
        :param sentence:
        :param lang:
        :return:
        """
        if lang == 'fr':
            stop = self.stop
        else:
            stop = self.stop_en
        words = [i for i in sentence.lower().split() if i not in stop]
        return words

    def translate(self, text, to='fr'):
        return bing(text, dst=to)

    def _load_classifier(self):
        self.classifier = self.load_classifier("allocine_classifier.pickle")

    @staticmethod
    def load_classifier(file):
        with open(file, "rb") as file:
            return pickle.load(file)


if __name__ == "__main__":
    nlp = NLP(load_classifier=False)

    print(nlp.sentiments_of_post("Glenfinnan's viaduct. They shot some Harry Potter's scenes here."))

