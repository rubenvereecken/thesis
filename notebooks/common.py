from scipy.signal import gaussian
from scipy.ndimage import filters

import sys
import os
import numpy as np
import csv
import json
import re
# from __future__ import print_function

exp_re = re.compile('(?P<experiment>.*?)' +
               '([_-]+rep.(?P<rep>[0-9]+))?' +
               '([_-]+(?P<date>[0-9]{2}-[0-9]{2}.*?))?$')


def csv_to_dict_of_arrays(filename):
    with open(filename) as f:
        reader = csv.DictReader(f)
        l = list(reader)
        learning = dict.fromkeys(reader.fieldnames)
        # Figure out the types by checking the first row
        types = []
        for d, k in l[0].items():
            try:
                int(k)
                types.append(np.int)
            except ValueError:
                types.append(np.float)
        for i, k in enumerate(learning):
            learning[k] = np.empty(len(l), dtype=types[i])
        for i, row in enumerate(l):
            for k, v in row.items():
                learning[k][i] = v
        return learning

def json_to_dict(filename):
    with open(filename) as f:
        return json.load(f)


#gaussian filter (running average but closer points have higher weights)
def smoothing(x,window=10,axis=0):
    filt = gaussian(window,2.)
    return filters.convolve1d(x,filt/np.sum(filt),axis)


def gather(d):
    learning_dict = {}
    results_dict = {}
    params_dict = {}

    for dirname in sorted(os.path.join(d, dirname) for dirname in os.listdir(d)):
        fulldir = dirname
        dirname = os.path.basename(fulldir)
        learning = csv_to_dict_of_arrays(os.path.join(fulldir, 'learning.csv'))
        results = csv_to_dict_of_arrays(os.path.join(fulldir, 'results.csv'))

        match = exp_re.match(dirname).groupdict()
        name = match['experiment']

        if name not in learning_dict:
            sys.stdout.write(name + ' ')

        learning_dict[name] = learning_dict.get(name, []) + [learning]
        results_dict[name] = results_dict.get(name, []) + [results]

        if name not in params_dict:
            params = json_to_dict(os.path.join(fulldir, 'parameters.json'))
            params_dict[name] = params

    print ''
    return learning_dict, results_dict, params_dict
