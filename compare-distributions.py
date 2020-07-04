# Crystal Butler
# 2020/06/15
# Plot histograms of two sets of relatedness scores with best fit curves overlaid.

import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('scores_file_1', help='path to first comparison file of synonymy scores', type=str)
parser.add_argument('scores_file_2', help='path to second comparison file of synonymy scores', type=str)
parser.add_argument('histogram_dir', help='path to a directory where the histogram plot will be written', type=str)
parser.add_argument('--bin_count', 
                    help='the number of bins used in the histogram', 
                    default=100,
                    type=int)
args = parser.parse_args()


def make_output_subdir():
    if not os.path.exists(args.histogram_dir):
        os.makedirs(args.histogram_dir)
    return


def read_scores(scores_file):
    """Get all the scores from a set of files in a directory,
    and put them into a single list."""
    score_count = 0
    all_scores = []
    with open(scores_file, 'r') as f:
        for line in f:
            score = line.strip()
            all_scores.append(score)
            score_count += 1
    assert len(all_scores) == score_count
    return all_scores


def sort_scores(scores):
    scores.sort()
    return scores


def make_array(scores):
    """Turn a list into a numpy array."""
    scores_array = np.array(scores).astype(np.float)
    return(scores_array)


def trim_scores(scores_array):
    """Only consider synonymy scores for pairs of different words.
    Same word pairs have a synonymy score of 1."""
    scores_rounded = scores_array.round(decimals=6)  # clean up floating point errors and reduce significant digits
    trimmed_scores = scores_rounded[scores_rounded < 1]
    print(f'trimmed scores is type {type(trimmed_scores)}, with shape {trimmed_scores.shape}.')
    return trimmed_scores


def normalize_array(scores_array):
    print(f'min of scores_array is {np.min(scores_array[0:-1])}.')
    scores_norm = (scores_array - np.min(scores_array))/(np.max(scores_array) - np.min(scores_array))
    return scores_norm


def calculate_statistics(scores_array):
    """Calculate descriptive statistics for the scores distribution."""
    mu = np.mean(scores_array)
    sigma = np.std(scores_array)
    a_min = np.min(scores_array)
    a_max = scores_array.max()
    return mu, sigma, a_min, a_max


def make_output_filenames():
    """Write statistics and histogram figure to the specified directory."""
    hist_file = os.path.join(args.histogram_dir, 'distribution_histogram.png')
    stats_file = os.path.join(args.histogram_dir, 'distribution_stats_1.txt')
    stats_file = os.path.join(args.histogram_dir, 'distribution_stats_2.txt')
    return hist_file, stats_file_1, stats_file_2


def format_distribution_stats(mu, sigma, a_min, a_max):
    """Pretty print layout for distribution statistics; can be appended to the histogram or saved out as a file."""
    stats_printout = '---------------------------------------------------------------------------------\n'
    stats_printout += 'Synonymy Scores Distribution Statistics\n---------------------------------------------------------------------------------\n'
    stats_printout += ('Mean: ' + str(mu) + '\n')
    stats_printout += ('Standard Deviation: ' + str(sigma) + '\n')
    stats_printout += ('Minimum: ' + str(a_min) + '\n')
    stats_printout += ('Maximum: ' + str(a_max) + '\n')
    return stats_printout


if __name__ == '__main__':
    make_output_subdir()
    scores_1 = read_scores(args.scores_file_1)
    scores_w = read_scores(args.scores_file_2)
    scores_sorted_1 = sort_scores(scores_1)
    scores_sorted_2 = sort_scores(scores_2)
    scores_array_1 = make_array(scores_sorted_1)
    scores_array_2 = make_array(scores_sorted_2)
    # Comment out the next three lines to skip normalization.
    scores_norm_1 = normalize_array(scores_array_1)
    scores_norm_2 = normalize_array(scores_array_2)
    scores_trimmed_1 = trim_scores(scores_norm_1)
    scores_trimmed_2 = trim_scores(scores_norm_2)
    # Uncomment the next 2 lines if skipping normaliztion.
    # scores_trimmed-1 = trim_scores(scores_array_1)
    # scores_trimmed-2 = trim_scores(scores_array_2)

    # Calculate statistics of the distributions.
    mu_1, sigma_1, a_min_1, a_max_1 = calculate_statistics(scores_trimmed_1)
    stats_printout_1 = format_distribution_stats(mu_1, sigma_1, a_min_1, a_max_1)
    mu_2, sigma_2, a_min_2, a_max_2 = calculate_statistics(scores_trimmed_2)
    stats_printout_2 = format_distribution_stats(mu_2, sigma_2, a_min_2, a_max_2)

    # Set up the plot.
    fig, ax = plt.subplots(figsize=(14, 8.5))  #(width, height) in inches
    
    # Plot the histogram of the first dataset.
    n, bins, patches = ax.hist(scores_trimmed_1, args.bin_count, density=1, alpha=.05)
    plt.figtext(0.02, 0.12, stats_printout_1, horizontalalignment='left', verticalalignment='center', fontsize=14)
    # Add a 'best fit' line.
    y = ((1 / (np.sqrt(2 * np.pi) * sigma_1)) *
        np.exp(-0.5 * (1 / sigma_1 * (bins - mu_1))**2))
    ax.plot(bins, y, '--')

    # Plot the histogram of the second dataset.
    n, bins, patches = ax.hist(scores_trimmed_2, args.bin_count, density=1, alpha=.05)
    plt.figtext(0.52, 0.12, stats_printout_2, horizontalalignment='left', verticalalignment='center', fontsize=14)
    # Add a 'best fit' line.
    y = ((1 / (np.sqrt(2 * np.pi) * sigma_2)) *
        np.exp(-0.5 * (1 / sigma_2 * (bins - mu_2))**2))
    ax.plot(bins, y, '--')

    # Format the figure.
    plt.subplots_adjust(bottom=0.32, top=0.95, right=0.98, left=0.06)
    y_label = 'Probability Density'
    x_label = 'Score Grouping: ' + str(args.bin_count) + ' Bins'
    ax.set_xlabel(x_label, fontsize=16)
    ax.set_ylabel(y_label, fontsize=16)
    ax.set_title('Histogram of Synonymy Scores', fontsize=18)

    # Save the figure and statistics.
    hist_file, stats_file_1, stats_file_2 = make_output_filenames()
    with open(stats_file_1, 'w') as f_stat:
        f_stat.write(stats_printout_1)
    with open(stats_file_2, 'w') as f_stat:
        f_stat.write(stats_printout_2)
    plt.savefig(hist_file, format='png')

    # Display the figure.
    plt.show()
    plt.close()