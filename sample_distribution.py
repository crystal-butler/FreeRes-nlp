# Crystal Butler
# 2020/07/01
# Generate a distribution of synonymy scores for a vocabulary by
# randomly sampling word pairs.

import os
import argparse
import random
import numpy as np

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
        vector_vocab_size = len(words)

    # Create word:number dictionary from the keys list, to be used for vector lookups.
    vector_vocab = {w: idx for idx, w in enumerate(keys)}

    # Create a numpy ndarray of semantic vectors. The ndarray is indexed by row number, while we need to index by word.
    # But we'll be using the O(1) lookup time from our vocab dictionary to translate from input word to row number.
    W = np.zeros((vector_vocab_size, vector_dim))
    for word, v in vectors.items():
        if word == '<unk>':
            continue
        W[vocab[word], :] = v

    # Normalize each word vector to unit variance.
    W_norm = np.zeros(W.shape)
    d = (np.sum(W ** 2, 1) ** (0.5))
    W_norm = (W.T / d).T
    return (W_norm, vector_vocab)


if __name__ == "__main__":
    # Read in the vocab file.
    words = read_vocab()
    print(len(words))
    
    # Randomly select word pairs for scoring until the specified sample count is reached.
