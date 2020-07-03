# Crystal Butler
# 2020/07/02
# Perform a Kolmogorov-Smirnov test on two sets of synonymy
# scores , to determine the probability that they are drawn
# from different distributions. Samples do not have to be equal size.

import os
import argparse
from scipy import stats
import numpy as np

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('scores_file_1', help='path to first comparison file of synonymy scores', type=str)
parser.add_argument('scores_file_2', help='path to second comparison file of synonymy scores', type=str)
parser.add_argument('--stats_dir', help='optional path to the directory where the test statistic is written', 
                    default=None,
                    type=str)
args = parser.parse_args()


def make_array(scores_file):
    """Read a scores list and convert it into a numpy array."""
    scores_array = np.array(scores).astype(np.float)
    return(scores_array)