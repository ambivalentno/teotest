import re
import json
import string
import nltk

from collections import defaultdict, Counter
from typing import List, Iterable, Dict, Sequence, Mapping
from redis import Redis

from gensim.models import Word2Vec
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

from blog.models import BlogPost


STOPWORDS = nltk.corpus.stopwords.words('english')
SENTENCE_TOKENIZER = nltk.data.load('tokenizers/punkt/english.pickle')


def count_to_percentage(idict: Dict[str, int], total: int) -> Dict[str, float]:
    to_percentage = lambda count, total: float("{0:.2f}".format((count / float(total)) * 100))
    return {word: to_percentage(count, total) for word, count in idict.items()}


def string_to_words(text: str) -> List[str]:
    """
    Converts text (single string) to the list of normalized (lowercase) words.
    """
    return re.sub("[^a-zA-Z]", " ", text).lower().split()


def drop_stopwords(words: Iterable[str]) -> Iterable[str]:
    return (w for w in words if w not in STOPWORDS and w != '')


def count_words(text: str) -> Counter:
    return Counter(drop_stopwords(string_to_words(text)))


def recalculate_stats() -> Mapping[str, Counter]:
    authors_words = defaultdict(Counter)

    # I use English posts only here, as:
    # 1. Polish requires good stemming because of higher variability.
    # 2. Given we've got a single short post in Polish, all words will have low count/frequency,
    #    therefore it's more of a noise, not a data.
    for blog in BlogPost.objects.filter(lang='en'):
        author = blog.author_slug
        count = count_words(blog.text)
        authors_words[author] += count

    return authors_words


def reset_stats(authors_words: Mapping[str, Counter], connection: Redis):
    total_counter = sum(authors_words.values(), Counter())
    top_10 = dict(total_counter.most_common(10))
    top_10_percentage = count_to_percentage(top_10, sum(total_counter.values()))

    top_10_per_author = {
        author: dict(words.most_common(10))
        for author, words in authors_words.items()
    }
    top_10_per_author_percentage = {
        author: count_to_percentage(words, sum(words.values()))
        for author, words in top_10_per_author.items()
    }
    connection.set('top_10', json.dumps(top_10))
    connection.set('top_10_percentage', json.dumps(top_10_percentage))
    # Potentially, it's better to set top_10_per_author_{author_slug} to have lesser data chunks,
    # but we dont need that right now because of small size of a dict.
    connection.set('top_10_per_author', json.dumps(top_10_per_author))
    connection.set('top_10_per_author_percentage', json.dumps(top_10_per_author_percentage))


def calc_wor2vec(sentences, filepath):
    """
    As we will not have any meaningful-looking result on such a small set, we omit stopwords
    from the vocabulary. Unfortunately, looks like v
    """
    # Instantiate Wor2Vec model.
    model = Word2Vec()
    # We use a vocabulary without stopwords, as most of meaningful words on such a small dataset are
    # mostly related to stopwords.
    model.build_vocab(
        [(word for word in drop_stopwords(sentence)) for sentence in sentences]
    )
    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)
    model.save(filepath)


def to_processed_sentences(text: Sequence) -> Iterable[Iterable[str]]:
    """
    Preprocessing function to prepare text for word2vec input.
    """
    # all_text = "/n".join(chunk.replace(" .", ".") for chunk in text)
    # Convert text to list of sentences
    raw_sentences = sum((SENTENCE_TOKENIZER.tokenize(chunk.strip()) for chunk in text), [])
    # Normalize text and convert string-sentences to lists of words.
    return [string_to_words(sent) for sent in raw_sentences]


def show_hierarchical_clustering(model):
    l = linkage(model.wv.syn0, method='complete', metric='seuclidean')

    # calculate full dendrogram
    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.ylabel('word')
    plt.xlabel('distance')

    dendrogram(
        l,
        leaf_font_size=16,  # font size for the x axis labels
        orientation='left',
        leaf_label_func=lambda v: str(model.wv.index2word[v]),
    )
    plt.show()
