# Crystal Butler
# 2019/03/04
# Take lists of scored label pairs as generated by word_pair_distance.py,
# and output lists of (label, total weight) pairs.
# Weights are simply the sum of similarity scores for each label.

import os
import argparse

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('scored_labels_dir', help='directory where list of scored word pairs are stored', type=str)
parser.add_argument('sums_dir', help='directory in which to store summed label weight lists after\
 processing scored_labels_dir',
                    type=str)
args = parser.parse_args()

# Constants, used to format output file names.
ZERO_PAD = 4
SUFFIX = ".txt"


def make_output_subdirs():
    if not os.path.exists(args.sums_dir):
        os.makedirs(args.sums_dir)


# Create a sorted list of (label, weight) pairs from (label, label, weight) triplets.
def create_weights_list(file):
    filename = os.fsdecode(file)
    if filename.startswith('.'):
        return None, None
    out_name = filename.split(".")[0]
    in_file = os.path.join(args.scored_labels_dir, filename)
    list1 = []
    list2 = []
    with open(in_file, 'r') as f:
        for line in f:
            label1, label2, weight = line.rstrip().split()
            list1.append([label1, weight])
            list2.append([label2, weight])
    weights_list = list1 + list2
    weights_list.sort()
    return out_name, weights_list


# Take a sorted list of (label, weight) pairs and sum over labels.
def sum_weights(out_name, weights_list):
    out_file = os.path.join(args.sums_dir, out_name + ".weights" + SUFFIX)
    w_sum = 0.0
    w_arr = []
    for i in range(len(weights_list)):
        label_curr = weights_list[i][0]
        if (i < len(weights_list) - 1):
            label_next = weights_list[i + 1][0]
        else:
            label_next = None
        w_sum += float(weights_list[i][1])
        if (label_next != label_curr):
            w_arr.append([label_curr, w_sum])
            w_sum = 0.0
    w_arr.sort(key=lambda w: w[1], reverse=True)
    with open(out_file, 'w') as o:
        for w in w_arr:
            o.write("{}\t{}\n".format(w[0].ljust(20), str(w[1]).ljust(20)))


if __name__ == "__main__":
    make_output_subdirs()
    read_directory = os.fsencode(args.scored_labels_dir)
    for file in os.listdir(read_directory):
        out_name, weights_list = create_weights_list(file)
        if (weights_list is not None):
            sum_weights(out_name, weights_list)
