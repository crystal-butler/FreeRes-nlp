# Crystal Butler
# 2020/08/28
# Combine passing dendrograms and statistics created by cluster_synonymy_scores,
# the top label and weight from sum_label_weights and AUs and weights
# from a spreadsheet to create a lexicon of facial expressions.

import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('dendros_dir', help='full path to a directory containing dendrograms that passed the clustering test', type=str)
parser.add_argument('labels_weights_dir', help='full path to a directory containing summed labels weights', type=str)
parser.add_argument('images_dir', help='full path to a directory of facial expression images', type=str)
parser.add_argument('aus_weights', help='full path to a CSV file containing AUs and weights', type=str)
parser.add_argument('output_dir', help='full path to a directory where lexicon pages will be written', type=str)
args = parser.parse_args()

def make_input_lists():
    dendros_files = []
    labels_weights_files = []
    images_files = []
    for entry in sorted(os.listdir(args.dendros_dir)):
        if os.path.isfile(os.path.join(args.dendros_dir, entry)):
            if not entry.startswith('.'):
                dendros_files.append(entry)
    for entry in sorted(os.listdir(args.labels_weights_dir)):
        if os.path.isfile(os.path.join(args.labels_weights_dir, entry)):
            if not entry.startswith('.'):
                labels_weights_files.append(entry)
    for entry in sorted(os.listdir(args.images_dir)):
        if os.path.isfile(os.path.join(args.images_dir, entry)):
            if not entry.startswith('.'):
                images_files.append(entry)
    if (len(dendros_files) < 1 or len(labels_weights_files) < 1 or len(images_files) < 1):
        print ("One of the input file lists is empty: quitting!")
        sys.exit()
    if (len(dendros_files) != len(labels_weights_files)):
        print("The dendrogram and label_weights file lists are not the same length: quitting!")
        sys.exit()
    return dendros_files, labels_weights_files, images_files

def get_csv_values():
    aus_weights_vals = pd.read_csv(args.aus_weights, header=1)
    return aus_weights_vals

def make_arrays(scores_path, labels_path):
    """Read scores and labels in from files. Convert them to ndarrays for clustering.
    Transform similarity (proximity) scores to distances."""
    pairs_scores = pd.read_csv(scores_path, header=None)
    labels = pd.read_csv(labels_path, header=None)
    scores_array = np.array(pairs_scores[0][:])
    scores_norm = normalize_array(scores_array)
    distances_array = 1 - scores_norm
    labels_array = np.array(labels[0][:])
    assert len(pairs_scores[0]) == len(distances_array), "Scores dataframe and distances array should be the same length."
    assert len(labels[0]) == len(labels_array), "Labels dataframe and labels array should be the same length."
    return distances_array, labels_array


def normalize_array(scores_array):
    scores_norm = (scores_array - np.min(scores_array))/np.ptp(scores_array)
    scores_norm = scores_norm.round(decimals=6)  # clean up floating point errors and reduce significant digits
    return scores_norm


def check_expected_distances_count(labels_array):
    """The distances array should be a serialized upper triangular label x label matrix,
       with entries below the diagonal omitted."""
    expected_distances_count = int((len(labels_array) * (len(labels_array) - 1)) / 2)
    return expected_distances_count


def build_linkage_matrix(distances_array):
    """Create the linkage matrix Z (perform hierarchical/agglomerative clustering)."""
    linkage_matrix = sch.linkage(distances_array, 'average')
    # Fix distances that have become less than 0 due to floating point errors.
    for i in range(len(linkage_matrix)):
        if linkage_matrix[i][2] < 0:
            linkage_matrix[i][2] = 0
    return linkage_matrix


def extract_dendro_name(labels_file, scores_file):
    labels_name = os.path.basename(labels_file)
    scores_name = os.path.basename(scores_file)
    labels_prefix = labels_name.split('_')[0]
    scores_prefix = scores_name.split('_')[0]
    assert labels_prefix == scores_prefix, "Labels and scores should have the same file name prefix."
    return labels_prefix


def calculate_cluster_stats(linkage_matrix, distances_array):
    """Calculate clustering statistics for cophenetic coefficient correlation, 
    the number of clusters, the count of labels per cluster and the 
    percent membershp in the largest cluster."""
    clusters = sch.fcluster(linkage_matrix, args.dendro_cutoff, criterion='distance')
    cluster_enumeration = np.unique(clusters)
    # Calculate the cophenetic correlation coefficient statistic: closer to 1 is better.
    cophenetic_coefficient, _ = sch.cophenet(linkage_matrix, distances_array)
    # Get membership counts for each cluster.
    cluster_membership = {}
    for value in cluster_enumeration:
        member_count = np.count_nonzero(clusters == value)
        cluster_membership[value] = member_count
    # Calculate the percentage membership in the largest cluster.
    c_max = max(cluster_membership.values())
    c_sum = sum(cluster_membership.values())
    pct = 100 * (c_max / c_sum)
    return cophenetic_coefficient, cluster_membership, pct


def make_output_dir():
    if not os.path.exists(args.output_dir):
        os.makedirs(args.clustering_dir)


def format_cluster_stats(cophenetic_coefficient, cluster_membership, pct):
    """Pretty print layout for clustering statistics; can be appended to the dendrogram or saved out as a file."""
    stats_printout = '---------------------------------------------------------------------------------\n'
    stats_printout += 'Agglomerative Hierarchical Clustering Statistics\n---------------------------------------------------------------------------------\n'
    stats_printout += ('Cophenectic correlation coefficient: ' + str(cophenetic_coefficient) + '\n')
    stats_printout += ('Cluster: Count\n')
    for key in cluster_membership.keys():
        stats_printout += (str(key) + ': ' + str(cluster_membership[key]) + '\n')
    cluster_max_membership = max(cluster_membership.items(), key=lambda x : x[1])
    stats_printout += ('Cluster ' + str(cluster_max_membership[0]) + ' with ' + str(cluster_max_membership[1]) + ' members has ' + str(pct) + '% of the membership.\n')
    pass_fail = classify_pass_fail(pct)
    stats_printout += ('Cluster coherence test: ' + pass_fail)
    return stats_printout


def classify_pass_fail(pct):
    """The clustering coherence test is based on membership percentage in the largest cluster."""
    pass_fail = 'pass' if pct >= 75 else 'fail'
    return pass_fail


def make_output_filenames(pct, dendro_name):
    """Write statistics and dendrograms to Pass or Fail directories based on the clustering coherence test."""
    if pct >= 75:
        dendro_file = os.path.join(args.clustering_dir, 'Dendrograms/Pass/' + dendro_name + '.png')
        stats_file = os.path.join(args.clustering_dir, 'Statistics/Pass/' + dendro_name + '.txt')
    else:
        dendro_file = os.path.join(args.clustering_dir, 'Dendrograms/Fail/' + dendro_name + '.png')
        stats_file = os.path.join(args.clustering_dir, 'Statistics/Fail/' + dendro_name + '.txt')
    return dendro_file, stats_file


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
        index = aus_weights_vals.index
        row_count = len(index)
        
        # for i in range(len(dendros_files)):
        #     dendros_file = os.path.join(args.dendros_dir, dendros_files[i])
        #     labels_weights_file = os.path.join(args.labels_weights_dir, labels_weights_files[i])
        #     images_file = os.path.join(args.images_dir, images_files[i])
        #     distances_array, labels_array = make_arrays(scores_file, labels_file)
        #     expected_distances_count = check_expected_distances_count(labels_array)
        #     if (expected_distances_count != len(distances_array)):
        #         print(f'The number of values in the {scores_file} distances list is {len(distances_array)}, but it should be {expected_distances_count}.')
        #         input("Press Enter to continue...")
        #         continue
            
        #     linkage_matrix = build_linkage_matrix(distances_array)
        #     assert (linkage_matrix.shape[0] + 1) == (len(labels_array)), "The linkage matrix and labels array have mismatched lengths."
        #     cophenetic_coefficient, cluster_membership, pct = calculate_cluster_stats(linkage_matrix, distances_array)
        #     stats_printout = format_cluster_stats(cophenetic_coefficient, cluster_membership, pct)

        #     # Title the dendrogram, using the labels file name.
        #     dendro_name = extract_dendro_name(labels_file, scores_file)
        #     # Set up the plot.
        #     fig, ax = plt.subplots(figsize=(14, 8.5))  #(width, height) in inches
        #     title = "Image: " + dendro_name
        #     plt.title(title, fontsize=18)
        #     plt.rc('ytick',labelsize=14)
        #     y_label = 'Cophenetic Coefficient (Cutoff: ' + str(args.dendro_cutoff) + ')'
        #     plt.ylabel(y_label, fontsize=16)
        #     plt.axhline(y=args.dendro_cutoff, color="grey", linestyle="--")
        #     # plt.figtext(0.02, 0.12, stats_printout, horizontalalignment='left', verticalalignment='center', fontsize=14)
        #     plt.subplots_adjust(bottom=0.22, top=0.95, right=0.98, left=0.06)
        #     # Create the dendrogram, with a cutoff specified during module invocation.
        #     dendro = sch.dendrogram(linkage_matrix, labels=labels_array, color_threshold=args.dendro_cutoff, \
        #         leaf_font_size=14, leaf_rotation=70, count_sort='ascending', ax=ax)
        #     ax.set_ylim(0, 1)

        #     # Save out the plot and statistics.
        #     dendro_file, stats_file = make_output_filenames(pct, dendro_name)
        #     with open(stats_file, 'w') as f_stat:
        #         f_stat.write(stats_printout)
        #     try:
        #         plt.savefig(dendro_file, format='png')
        #     except:
        #         print(f'Unable to save {dendro_file}!')
        #     # plt.show()  # uncomment to display the plot before continuing
        #     plt.close()

    else:
        print("Be sure to include options for the dendrogram directory, labels and weights directory, \
            images directory, AUs and weights file and output directory when calling this module.")