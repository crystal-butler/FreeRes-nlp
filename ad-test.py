# Crystal Butler
# 2020/07/02
# Perform an Anderson-Darling test on two sets of synonymy
# scores, to determine the probability that they are drawn
# from the test distribution.
# From the SciPy docs: "This function works for normal, exponential, 
# logistic, or Gumbel (Extreme Value Type I) distributions."
# Distribution options are ‘norm’, ‘expon’, ‘logistic’, ‘gumbel’, ‘gumbel_l’, ‘gumbel_r'

import os
import argparse
from scipy import stats
import pandas as pd
import numpy as np

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('scores_file', help='path to first comparison file of synonymy scores', type=str)
parser.add_argument('--dist_type', help='optional distribution type to test against',
                    default='norm',
                    type=str)  
parser.add_argument('--stats_dir', help='optional path to the directory where the test statistic is written', 
                    default=None,
                    type=str)
args = parser.parse_args()


def make_array(scores_file):
    """Read a scores list and convert it into a numpy array."""
    pairs_scores = pd.read_csv(scores_file, header=None)
    scores_array = np.array(pairs_scores).astype(np.float)
    scores_array = normalize_array(scores_array)  # comment out if no normalization is desired
    return(scores_array)


def normalize_array(scores_array):
    scores_norm = (scores_array - np.min(scores_array))/(np.max(scores_array) - np.min(scores_array))
    return scores_norm


def calculate_ad(scores):
    """Calculate the Anderson-Darling statistic."""
    ad_stat, crit_values , sig_levels = stats.anderson(scores[:, 0], dist=args.dist_type)
    return ad_stat, crit_values, sig_levels


def format_ad_stats(ad_stat, crit_values, sig_levels):
    """Pretty print layout for Anderson-Darling test results."""
    stats_printout = '---------------------------------------------------------------------------------\n'
    stats_printout += 'Anderson-Darling Test Results\n---------------------------------------------------------------------------------\n'
    stats_printout += ('Sample data file: ' + args.scores_file + '\n')
    stats_printout += ('AD Statistic: ' + str(ad_stat) + '\n')
    stats_printout += ('Critical Values :' + '\n')
    for n in crit_values:
        stats_printout += (str(n) + '\n')
    stats_printout += ('Significance Levels:' + '\n')
    for n in sig_levels:
        stats_printout += (str(n) + '\n')x
    return stats_printout


def write_stats(stats_printout):
    """Write statistics to the specified directory."""
    stats_file = os.path.join(args.stats_dir, 'ad_stats.txt')
    with open(stats_file, 'w') as f_stat:
        f_stat.write(stats_printout)


if __name__ == '__main__':
    scores = make_array(args.scores_file)
    ad_stat, crit_values, sig_levels = calculate_ad(scores)
    stats_printout = format_ad_stats(ad_stat, crit_values, sig_levels)
    if args.stats_dir is None:
        print(stats_printout)
    else:
        write_stats(stats_printout)