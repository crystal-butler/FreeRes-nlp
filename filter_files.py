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
import shutil

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
        os.makedirs(args.labels_out)
    if not os.path.exists(args.images_out):
        os.makedirs(args.images_out)


def create_filter_list():
    filter_list = []
    read_directory = os.fsencode(args.filter_dir)
    for file in os.listdir(read_directory):
        filename = os.fsdecode(file)
        if filename.startswith('.'):
            continue
        filter_name = filename.split(".")[0]
        try:
            filter_list.append(filter_name)
        except:
            print(f"Unable to append {filter_name} to filter list!")
    print(f"Found {len(filter_list)} file names to check.")
    return filter_list


def filter_label_files(filter_list):
    copy_list = []
    read_directory = os.fsencode(args.labels_dir)
    for file in os.listdir(read_directory):
        filename = os.fsdecode(file)
        if filename.startswith('.'):
            continue
        check_name = filename.split(".")[0]
        if (check_name in filter_list):
            try:
                copy_list.append(filename)
                copy_file = os.path.join(args.labels_dir, filename)
                shutil.copy2(copy_file, args.labels_out)
            except:
                print(f"Failed to copy {filename}.")
    print(f"Matched {len(copy_list)} files.")
    assert len(copy_list) == len(filter_list)


# def filter_image_files(filter_list):
#     pass


if __name__ == "__main__":
    make_output_subdirs()
    filter_list = create_filter_list()
    filter_label_files(filter_list)
    # filter_image_files(filter_list)
