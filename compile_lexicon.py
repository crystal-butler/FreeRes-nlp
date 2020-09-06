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
import matplotlib.gridspec as gridspec
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
    try:
        if not os.path.exists(args.lexicon_dir):
            os.makedirs(args.lexicon_dir)
    except:
        print(f'Couldn\'t make the output directory at {args.lexicon_dir}!')


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


def get_labels_weights(labels_weights_file):
    with open(labels_weights_file, 'r') as f:
        labels_weights = []
        for line in f:
            stripped_line = line.strip()
            label, weight = stripped_line.split()
            weight = round(float(weight), 6)
            lw = [label, weight]
            labels_weights.append(lw)
        return labels_weights


def print_labels_weights(labels_weights):
    for lw in labels_weights:
        print(lw[0])
        print(lw[1])


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
        print('{:>15}'.format(image_record.index[i]), end='')
    print()
    for i in range(len(image_record)):
        print('{:>15}'.format(str(image_record.values[i])), end='')
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


def format_image_text(weight, image_record):
    """Pretty print layout for the text of the lexicon plot."""
    image_text = '-----------------------------\n'
    image_text += 'Action Units and Weights\n'
    image_text += '-----------------------------\n'
    image_text += '%-6s' % ('AU')
    image_text += '%10s' % ('Weight\n')
    for i in range(0, len(image_record), 2):
        image_text += '%-6s' % (str(image_record.values[i].strip()))
        image_text += '%10s' % (str(image_record.values[i + 1]))
        image_text += '\n'
    return image_text

def format_labels_weights_text(labels_weights):
    """Pretty print layout for the text of the lexicon plot."""
    labels_weights_text = '---------------------------\n'
    labels_weights_text += ('Label Similarity Scores\n')
    labels_weights_text += '---------------------------\n'
    for i in range(0, len(labels_weights)):
        labels_weights_text += '%-16s' % (str(labels_weights[i][0]))
        labels_weights_text += '%10s' % (str(labels_weights[i][1]))
        labels_weights_text += '\n'   
    labels_weights_text += '\n'
    return labels_weights_text


def build_plot(image_name, label, dendros_file, images_file, image_text, labels_weights_text):
    # Set up the plot and subplots.
    fig = plt.figure(figsize=(8.5, 11))
    fig.tight_layout()
    plt.subplots_adjust(bottom=0.05, top=0.95, right=0.95, left=0.05, wspace=0, hspace=0)

    # Add facial expression image to a subplot.
    with cbook.get_sample_data(images_file) as image_file:
        image = plt.imread(image_file)
    sub1 = fig.add_subplot(3, 3, (1,2))
    sub1.axis('off')
    plt.imshow(image)

    # Add image text to a subplot.
    sub2 = plt.subplot(3, 3, (4, 5))
    sub2.axis('off')
    sub2.text(0.5, 0.95,
            "Image Label: " + label, 
            fontsize=12,
            va='top',
            ha='center')
    sub2.text(0.5, 0.9,
            image_text,
            fontsize=8,
            fontfamily='monospace',
            va='top',
            ha='center')

    # Add labels and weights text to a subplot.
    sub3 = plt.subplot(3, 3, 3)
    sub3.axis('off')
    sub3.text(0.5, 1.0,
            labels_weights_text,
            fontsize = 8,
            fontfamily='monospace',
            va='top',
            ha='center')

    # Add dendrogram to a subplot.
    with cbook.get_sample_data(dendros_file) as dendro_file:
        dendro = plt.imread(dendro_file)
    sub4 = fig.add_subplot(2, 1, 2)
    sub4.axis('off')
    plt.imshow(dendro)
    
    # Save out the plot.
    plot_file = make_output_filename(image_name)
    try:
        plt.savefig(plot_file, format='png')
    except:
        print(f'Unable to save {plot_file}!')
    
    plt.show(block=False)
    plt.pause(1)
    plt.close()


def make_output_filename(image_name):
    """Name a plot file based on the facial expression image it displays."""
    plot_file = os.path.join(args.lexicon_dir, image_name + '.png')
    return plot_file


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
        image_names = extract_image_names(dendros_files)
        for image_name in image_names:
            dendros_file = find_dendros_file(image_name, dendros_files)
            labels_weights_file = find_labels_weights_file(image_name, labels_weights_files)
            labels_weights = get_labels_weights(labels_weights_file)
            images_file = find_images_file(image_name, images_files)
            image_record = get_image_record(image_name, aus_weights_vals)
            image_text = format_image_text(labels_weights[0][1], image_record)
            labels_weights_text = format_labels_weights_text(labels_weights)
            build_plot(image_name, labels_weights[0][0], dendros_file, images_file, image_text, labels_weights_text)

    else:
        if (not os.path.isdir(args.dendros_dir)):
            print(f'Missing or incorrect argument for dendros_dir: tried {args.dendros_dir}.')
        elif (not os.path.isdir(args.labels_weights_dir)):
            print(f'Missing or incorrect argument for labels_weights_dir: tried {args.labels_weights_dir}.')
        elif (not os.path.isdir(args.images_dir)):
            print(f'Missing or incorrect argument for images_dir: tried {args.images_dir}.')
        elif (not os.path.isfile(args.aus_weights)):
            print(f'Missing or incorrect argument for aus_weights: tried {args.aus_weights}.')
        else:
            print("Be sure to include options for the dendrogram directory, labels and weights directory, \
images directory, AUs and weights file and output directory when calling this module.")