import pickle

from textblob.classifiers import NaiveBayesClassifier


def save_classifier(classifier):
    with open('allocine_classifier.pickle', 'wb') as f:
        pickle.dump(classifier, f, -1)


def train_with_allocine(file):
    with open(file, "rb") as file:
        return pickle.load(file)


if __name__ == "__main__":
    classifier = NaiveBayesClassifier(train_with_allocine("train2.data"))
    save_classifier(classifier)
