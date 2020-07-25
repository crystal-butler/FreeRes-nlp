# Crystal Butler
# 2019/03/01
# Pre-process free response label lists for input into the synonymy scoring script, word_pair_distance.py.
# Any line with the string "NA" (without quotes) will be dropped.
#
# The required arguments are for a directory containing files of label lists, with one label per line,
# and one file per stiumulus; then a directory where label pair files will be output, with one space-separated
# label pair per line and one set of all-pairs per stimulus in a file. The generate_all_pairs function will keep
# duplicate labels, and will pair them as with any other label. This design allows for accurate weighting of
# labels in word_pair_distance.py, which calculates synonymy scores for all pairs as a precursor to
# the weighting and clustering steps in cluster_synonymy_scores.py.

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


# Create files of all pairs of labels per ID from a directory of label lists, with one space-separated pair per line.
def generate_all_pairs():
    read_directory = os.fsencode(args.wordlists_dir)
    for file in os.listdir(read_directory):
        filename = os.fsdecode(file)
        if filename.startswith('.'):
            continue
        ID = filename.split("_")[0]
        in_file = os.path.join(args.wordlists_dir, filename)
        out_file = os.path.join(args.wordpairs_dir, ID + "_pairs" + SUFFIX)
        with open(in_file, 'r') as f:
            label_list = [line.rstrip('\n') for line in f]
            with open(out_file, 'w') as o:
                for i in range(len(label_list)):
                    for j in range(i + 1, (len(label_list))):
                        o.write("{} {}\n".format(label_list[i], label_list[j]))


if __name__ == "__main__":
    if (args.ID_label_file is not None):
        split_ID_labels()
    generate_all_pairs()
