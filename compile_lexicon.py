# Crystal Butler
# 2020/08/28
# Combine passing dendrograms and statistics created by cluster_synonymy_scores,
# the top label and weight from sum_label_weights and AUs and weights
# from a spreadsheet to create a lexicon of facial expressions.

import os
import sys
import argparse
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage, AnnotationBbox)
import matplotlib.cbook as cbook

DENDRO_EXT = ".png"
WEIGHTS_EXT = ".weights.txt"
IMAGE_EXT = ".jpg"

parser = argparse.ArgumentParser()
parser.add_argument('dendros_dir', help='full path to a directory containing dendrograms that passed the clustering test', type=str)
parser.add_argument('labels_weights_dir', help='full path to a directory containing summed labels weights', type=str)
parser.add_argument('images_dir', help='full path to a directory of facial expression images', type=str)
parser.add_argument('aus_weights', help='full path to a CSV file containing AUs and weights', type=str)
parser.add_argument('lexicon_dir', help='full path to a directory where lexicon pages will be written', type=str)
args = parser.parse_args()


def make_output_dir():
    if not os.path.exists(args.lexicon_dir):
        os.makedirs(args.lexicon_dir)


def make_input_lists():
    dendros_files = []
    labels_weights_files = []
    images_files = []
    for entry in sorted(os.listdir(args.dendros_dir)):
        if os.path.isfile(os.path.join(args.dendros_dir, entry)):
            if not entry.startswith('.'):
                dendros_files.append(os.path.join(args.dendros_dir, entry))
    for entry in sorted(os.listdir(args.labels_weights_dir)):
        if os.path.isfile(os.path.join(args.labels_weights_dir, entry)):
            if not entry.startswith('.'):
                labels_weights_files.append(os.path.join(args.labels_weights_dir, entry))
    for entry in sorted(os.listdir(args.images_dir)):
        if os.path.isfile(os.path.join(args.images_dir, entry)):
            if not entry.startswith('.'):
                images_files.append(os.path.join(args.images_dir, entry))
    if (len(dendros_files) < 1 or len(labels_weights_files) < 1 or len(images_files) < 1):
        print ("One of the input file lists is empty: quitting!")
        sys.exit()
    if (len(dendros_files) != len(labels_weights_files)):
        print("The dendrogram and label_weights file lists are not the same length: quitting!")
        sys.exit()
    return dendros_files, labels_weights_files, images_files


def get_csv_values():
    aus_weights_vals = pd.read_csv(args.aus_weights, dtype=str)
    index_column = aus_weights_vals.columns.values[0]
    # print(index_column)
    aus_weights_vals.set_index(index_column, inplace=True)
    return aus_weights_vals


def extract_image_names(dendros_files):
    image_names = []
    for file in dendros_files:
        file_name = os.path.basename(file)
        image_name = file_name.split('.')[0]
        image_names.append(image_name)
    assert len(dendros_files) == len(image_names), \
        "Dendros list has %r members and image name list has %r members!" % (len(dendros_files), len(image_names))
    return image_names


def find_dendros_file(image_name, dendros_files):
    for dendros_file in dendros_files:
        if (image_name + DENDRO_EXT) in os.path.basename(dendros_file):
            return dendros_file
    print(f'uh-oh, image {image_name} not found in dendros_files list!')


def find_labels_weights_file(image_name, labels_weights_files):
    for labels_weights_file in labels_weights_files:
        if (image_name + WEIGHTS_EXT) in os.path.basename(labels_weights_file):
            return labels_weights_file
    print(f'uh-oh, image {image_name} not found in labels_weights_files list!')


def get_label_weight(labels_weights_file):
    with open(labels_weights_file, 'r') as f:
        top = f.readline()
        label, weight = top.split()
        weight = round(float(weight), 6)
        return label, weight


def find_images_file(image_name, images_files):
    for images_file in images_files:
        if (image_name + IMAGE_EXT) in os.path.basename(images_file):
            return images_file
    print(f'uh-oh, image {image_name} not found in images_files list!')


def get_image_record(image_name, aus_weights_vals):
    image_record = aus_weights_vals.loc[image_name]
    return image_record


def print_image_record(image_record):
    for i in range(len(image_record)):
        print('{:>10}'.format(image_record.index[i]), end='')
    print()
    for i in range(len(image_record)):
        print('{:>10}'.format(image_record.values[i]), end='')
    print('\n')


def plot_image(images_file):
    with cbook.get_sample_data(images_file) as image_file:
        image = plt.imread(image_file)
    fig, ax = plt.subplots()
    im = ax.imshow(image)
    ax.axis('off')
    plt.show(block=False)
    plt.pause(1)
    plt.close()


def print_label_weight(label, weight):
    print(f'Label: {label}')
    print(f'Weight: {weight}')


def format_image_text(label, weight, image_record):
    """Pretty print layout for the text of the lexicon plot."""
    image_text = '-----------------------------------------------\n'
    image_text += 'Image Label: ' + label + '\n'
    image_text += ('Label Similarity Score: ' + str(weight) + '\n')
    image_text += '-----------------------------------------------\n'
    image_text += 'Action Units and Weights\n'
    for i in range(len(image_record)):
        image_text += '{:>10}'.format(image_record.index[i])
    image_text += '\n'
    for i in range(len(image_record)):
        image_text += '{:>10}'.format(image_record.values[i])
    image_text += '\n'
    image_text += '-----------------------------------------------\n'
    return image_text


def build_plot(image_name, dendros_file, images_file, image_text):
    # xy = [0.3, 0.55]
    # with cbook.get_sample_data(images_file) as image_file:
    #     image = plt.imread(image_file)
    # fig, ax = plt.subplots()
    # imagebox = OffsetImage(image, zoom=0.2)
    # imagebox.image.axes = ax
    # ab = AnnotationBbox(imagebox, xy,
    #                     xybox=(120., -80.),
    #                     xycoords='data',
    #                     boxcoords="offset points",
    #                     pad=0.5)
    # ax.add_artist(ab)
    with cbook.get_sample_data(images_file) as image_file:
        image = plt.imread(image_file)
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    im = ax.imshow(image)
    ax.axis('off')
    
    title = "Image: " + image_name
    plt.title(title, fontsize=18)
    # plt.rc('ytick',labelsize=14)
    # y_label = 'Cophenetic Coefficient (Cutoff: ' + str(args.dendro_cutoff) + ')'
    # plt.ylabel(y_label, fontsize=16)
    # plt.axhline(y=args.dendro_cutoff, color="grey", linestyle="--")
    plt.figtext(0.02, 0.12, image_text, horizontalalignment='right', verticalalignment='center', fontsize=14)
    plt.subplots_adjust(bottom=0.22, top=0.95, right=0.98, left=0.06)
    # Create the dendrogram, with a cutoff specified during module invocation.
    plt.show(block=False)
    plt.pause(1)
    plt.close()


def save_lexicon_entry(plot):
        #     # Save out the plot and statistics.
        #     dendro_file, stats_file = make_output_filenames(pct, dendro_name)
        #     with open(stats_file, 'w') as f_stat:
        #         f_stat.write(stats_printout)
        #     try:
        #         plt.savefig(dendro_file, format='png')
        #     except:
        #         print(f'Unable to save {dendro_file}!')
    plt.show(block=False)
    plt.pause(1)
    plt.close()


# def make_output_filenames(pct, dendro_name):
#     """Write statistics and dendrograms to Pass or Fail directories based on the clustering coherence test."""
#     if pct >= 75:
#         dendro_file = os.path.join(args.clustering_dir, 'Dendrograms/Pass/' + dendro_name + '.png')
#         stats_file = os.path.join(args.clustering_dir, 'Statistics/Pass/' + dendro_name + '.txt')
#     else:
#         dendro_file = os.path.join(args.clustering_dir, 'Dendrograms/Fail/' + dendro_name + '.png')
#         stats_file = os.path.join(args.clustering_dir, 'Statistics/Fail/' + dendro_name + '.txt')
#     return dendro_file, stats_file


if __name__ == '__main__':
    make_output_dir()
    if (os.path.isdir(args.dendros_dir) and os.path.isdir(args.labels_weights_dir) and os.path.isdir(args.images_dir) \
        and os.path.isfile(args.aus_weights)):
        """We are pulling dendrogram, summed label weight and synthetic facial expression
        image files and matching them with lines from a CSV file that documents the
        generative parameters for the expressions. Lexicon entries are created
        by iteratively compiling one entry from each source per entry."""
        dendros_files, labels_weights_files, images_files = make_input_lists()
        aus_weights_vals = get_csv_values()
        # index = aus_weights_vals.index
        # row_count = len(index)
        # print(aus_weights_vals.head())
        # print(aus_weights_vals.columns.values[0])
        image_names = extract_image_names(dendros_files)
        for image_name in image_names:
            dendros_file = find_dendros_file(image_name, dendros_files)
            # print(dendros_file)
            labels_weights_file = find_labels_weights_file(image_name, labels_weights_files)
            # print(labels_weights_file)
            label, weight = get_label_weight(labels_weights_file)
            # print(label, weight)
            images_file = find_images_file(image_name, images_files)
            # print(images_file)
            image_record = get_image_record(image_name, aus_weights_vals)
            # print_image_record(image_record)
            # print_label_weight(label, weight)
            # plot_image(images_file)
            image_text = format_image_text(label, weight, image_record)
            # print(image_text)
            build_plot(image_name, dendros_file, images_file, image_text)


    else:
        print("Be sure to include options for the dendrogram directory, labels and weights directory, \
            images directory, AUs and weights file and output directory when calling this module.")