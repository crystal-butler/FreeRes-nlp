# Crystal Butler
# 2020/08/08
# Filter one directory of files based on the contents of another.
#
# This script is used to match the image and label files to dendrograms that pass
# the clustering test applied in cluster_synonymy_scores.py. 

import os
import argparse

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('wordlists_dir', help='directory where individual word lists by ID are stored', type=str)
parser.add_argument('wordpairs_dir', help='directory in which to store word pair lists after processing wordlists_dir',
                    type=str)
args = parser.parse_args()

# Constants, used to format output file names.
ZERO_PAD = 4
SUFFIX = ".txt"


def make_output_subdirs():
    if not os.path.exists(args.wordpairs_dir):
        os.makedirs(args.wordpairs_dir)
