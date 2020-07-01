# Crystal Butler
# 2020/07/01
# Generate a distribution of synonymy scores for a vocabulary by
# randomly sampling word pairs.

import os
import argparse
import random
import numpy as np
np.seterr(divide='ignore', invalid='ignore')  # fix runtime error when dividing by zero

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('vocab_file', help='path to file of vocabulary words, one per line', type=str)
parser.add_argument('scores_file', help='path to file in which to store word pair scores', type=str)
parser.add_argument('vectors_file', help='path to the word embeddings file used to calculate synonymy scores', type=str)
parser.add_argument('sample_count', help='number of sample word pairs to score', type=int)
args = parser.parse_args()


def read_vocab():
    with open(args.vocab_file, 'r') as f:
        words = [x.rstrip().split(' ')[0] for x in f.readlines()]
    return words


def generate():
    # Semantic vectors (or word embeddings) are the result of training a ML model to represent word relatedness.
    with open(args.vectors_file, 'r') as f:
        # The pre-trained semantic vectors will go into a Python dictionary.
        # Dictionaries are key:value indexed; lookup is done via hash function and should be O(1) time complexity.
        # But the dictionary is just an intermediate. Lookups will be done against a numpy ndarray, constructed later.
        vectors = {}
        # The "words" list is an intermediate. The dictionary used in processing is constructed later.
        keys = []
        vals = []
        for line in f:
            vals = line.rstrip().split(' ')
            # Turn semantic vectors into key-value pairs, indexed by lookup word.
            keys.append(vals[0])
            vectors[vals[0]] = [float(x) for x in vals[1:]]
        vector_dim = len(vals) - 1  # Number of features in a semantic vector, minus the index word at the beginning.
        vector_vocab_size = len(keys)

    # Create word:number dictionary from the keys list, to be used for vector lookups.
    vector_vocab = {w: idx for idx, w in enumerate(keys)}

    # Create a numpy ndarray of semantic vectors. The ndarray is indexed by row number, while we need to index by word.
    # But we'll be using the O(1) lookup time from our vocab dictionary to translate from input word to row number.
    W = np.zeros((vector_vocab_size, vector_dim))
    for word, v in vectors.items():
        if word == '<unk>':
            continue
        W[vector_vocab[word], :] = v

    # Normalize each word vector to unit variance.
    W_norm = np.zeros(W.shape)
    d = (np.sum(W ** 2, 1) ** (0.5))
    W_norm = (W.T / d).T
    return (W_norm, vector_vocab)


def get_random_pair(words, sample_range):
    random_index = random.randrange(sample_range)
    print(f'Index 1 is {random_index}.')
    word1 = words[random_index]
    random_index = random.randrange(sample_range)
    print(f'Index 1 is {random_index}.')
    word2 = words[random_index]
    return word1, word2


def distance(W, vector_vocab, word1, word2):
    if word1 not in vocab or word2 not in vector_vocab:
        # Magic number to indicate that some word wasn't in the vocabulary.
        return -100

    # Cosine similarity is calculated as (vector1 • vector2) / (\\vector1\\ * \\vector2\\). But the magnitudes of
    # our vectors have all been normalized to 1, so this reduces to a vector dot product.
    distance = np.dot(W[vector_vocab[word1]], W[vector_vocab[word2]])
    return distance


if __name__ == "__main__":
    # Read in the vocab file.
    words = read_vocab()
    sample_range = len(words)
    print(f'The sample range is 0 to {sample_range - 1}.')

    # Generate the vector lookup references.
    W, vector_vocab = generate()
    
    # Randomly select word pairs for scoring until the specified sample count is reached.
    with open(args.scores_file, 'w') as f:
        for i in range(args.sample_count):
            word1, word2 = get_random_pair(words, sample_range)
            print(word1, word2)
            score = distance(W, vector_vocab, word1, word2)
            print(score)
