# Crystal Butler
# 2020/08/08
# Filter one directory of files based on the contents of another.
#
# This script is used to match the image and label files to dendrograms that pass
# the clustering test applied in cluster_synonymy_scores.py. It uses the names of
# files in the Dendrograms/Pass directory as a filter. The label and image files
# must have the same suffix as the dendrogram files for the script to work.
# Matching image and label files are copied to the specified directories.

import os
import argparse

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('filter_dir', help='directory of files to be matched', type=str)
parser.add_argument('labels_dir', help='directory of label lists to filter against filter_dir', type=str)
parser.add_argument('images_dir', help='directory of images to filter against filter_dir', type=str)
parser.add_argument('labels_out', help='directory that matching label lists will be copied to', type=str)
parser.add_argument('images_out', help='directory that matching images will be copied to', type=str)
args = parser.parse_args()

# Constants, used to format output file names.
ZERO_PAD = 4
SUFFIX = ".txt"


def make_output_subdirs():
    if not os.path.exists(args.labels_out):
        os.makedirs(args.wordpairs_dir)
    if not os.path.exists(args.images_out):
        os.makedirs(args.wordpairs_dir)


filter_label_files(filter_list):
    pass


filter_image_files(filter_list):
    pass


if __name__ == "__main__":
    make_output_subdirs()
    print("Done!")
    filter_list = create_filter_list()
    filter_label_files(filter_list)
    filter_image_files(filter_list)