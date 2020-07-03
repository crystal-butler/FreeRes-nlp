# Crystal Butler
# 2020/07/02
# Perform a Kolmogorov-Smirnov test on two sets of synonymy
# scores , to determine the probability that they are drawn
# from different distributions. Samples do not have to be equal size.
# From the SciPy docs: "This is a two-sided test for the null hypothesis that 
# 2 independent samples are drawn from the same continuous distribution."

import os
import argparse
from scipy import stats
import pandas as pd
import numpy as np

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('scores_file_1', help='path to first comparison file of synonymy scores', type=str)
parser.add_argument('scores_file_2', help='path to second comparison file of synonymy scores', type=str)
parser.add_argument('--stats_dir', help='optional path to the directory where the test statistic is written', 
                    default=None,
                    type=str)
parser.add_argument('--p_value_target', help='optional target probability value for passing the KS test', 
                    default=0.05,
                    type=float)
args = parser.parse_args()


def make_array(scores_file):
    """Read a scores list and convert it into a numpy array."""
    pairs_scores = pd.read_csv(scores_file, header=None)
    scores_array = np.array(pairs_scores).astype(np.float)
    return(scores_array)


def calculate_ks(scores_1, scores_2):
    """Calculate the Kolmogorov-Smirnov statistic."""
    ks_stat, p_value = stats.ks_2samp(scores_1, scores_2)
    print(ks_stat, p_value)
    return ks_stat, p_value


def format_ks_stats(ks_stat, p_value):
    """Pretty print layout for Kolmogorov-Smirnov test results."""
    stats_printout = '---------------------------------------------------------------------------------\n'
    stats_printout += 'Kolmogorov-Smirnov Test Results\n---------------------------------------------------------------------------------\n'
    stats_printout += ('KS Statistic: ' + str(ks_stat) + '\n')
    stats_printout += ('p value: ' + str(p_value) + '\n')
    pass_fail = classify_pass_fail(p_value)
    stats_printout += ('The test statistic ' + pass_fail + ' the null hypothesis test at the ' + args.p_value_target + ' level.')
    return stats_printout


def classify_pass_fail(p_value):
    """Compare the calculated probability to the target probability, for null hypothesis testing."""
    pass_fail = 'passes' if p_value >= args.p_value_target else 'fails'
    return pass_fail


def write_stats(stats_printout):
    """Write statistics to the specified directory."""
    stats_file = os.path.join(args.stats_dir, 'ks_stats.txt')
    with open(stats_file, 'w') as f_stat:
        f_stat.write(stats_printout)


if __name__ == '__main__':
    scores_1 = make_array(args.scores_file_1)
    scores_2 = make_array(args.scores_file_2)
    ks_stat, p_value = calculate_ks(scores_1, scores_2)
    stats_printout = format_ks_stats(ks_stat, p_value)
    if args.stats_dir is None:
        print(stats_printout)
    else:
        write_stats(stats_printout)