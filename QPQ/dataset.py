"""
The :mod:`dataset <surprise.dataset>` module defines the :class:`Dataset` class
and other subclasses which are used for managing datasets.

Users may use both *built-in* and user-defined datasets (see the
:ref:`getting_started` page for examples). Right now, three built-in datasets
are available:

* The `movielens-100k <http://grouplens.org/datasets/movielens/>`_ dataset.
* The `movielens-1m <http://grouplens.org/datasets/movielens/>`_ dataset.
* The `movielens-25m <http://grouplens.org/datasets/movielens/>`_ dataset.
* The `Jester <http://eigentaste.berkeley.edu/dataset/>`_ dataset 2.

Built-in datasets can all be loaded (or downloaded if you haven't already)
using the :meth:`Dataset.load_builtin` method.
Summary:

.. autosummary::
    :nosignatures:

    Dataset.load_builtin
    Dataset.load_from_file
    Dataset.load_from_folds
"""


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import defaultdict
import sys
import os
import itertools

from six.moves import input

from .reader import Reader
from .builtin_datasets import download_builtin_dataset
from .builtin_datasets import BUILTIN_DATASETS
from .trainset import Trainset


class Dataset:
   

    def __init__(self, reader):

        self.reader = reader

    @classmethod
    def load_builtin(cls, name='ml-100k', prompt=True):
        

        try:
            dataset = BUILTIN_DATASETS[name]
        except KeyError:
            raise ValueError('unknown dataset ' + name +
                             '. Accepted values are ' +
                             ', '.join(BUILTIN_DATASETS.keys()) + '.')

        # if dataset does not exist, offer to download it
        if not os.path.isfile(dataset.path):
            answered = not prompt
            while not answered:
                print('Dataset ' + name + ' could not be found. Do you want '
                      'to download it? [Y/n] ', end='')
                choice = input().lower()

                if choice in ['yes', 'y', '', 'omg this is so nice of you!!']:
                    answered = True
                elif choice in ['no', 'n', 'hell no why would i want that?!']:
                    answered = True
                    print("Ok then, I'm out!")
                    sys.exit()

            download_builtin_dataset(name)

        reader = Reader(**dataset.reader_params)

        return cls.load_from_file(file_path=dataset.path, reader=reader)

    @classmethod
    def load_from_file(cls, file_path, reader):
        

        return DatasetAutoFolds(ratings_file=file_path, reader=reader)

    @classmethod
    def load_from_folds(cls, folds_files, reader):
        

        return DatasetUserFolds(folds_files=folds_files, reader=reader)

    @classmethod
    def load_from_df(cls, df, reader):
        

        return DatasetAutoFolds(reader=reader, df=df)

    def read_ratings(self, file_name):
        """Return a list of ratings (user, item, rating, timestamp) read from
        file_name"""

        with open(os.path.expanduser(file_name)) as f:
            raw_ratings = [self.reader.parse_line(line) for line in
                           itertools.islice(f, self.reader.skip_lines, None)]
        return raw_ratings

    def construct_trainset(self, raw_trainset):

        raw2inner_id_users = {}
        raw2inner_id_items = {}

        current_u_index = 0
        current_i_index = 0

        ur = defaultdict(list)
        ir = defaultdict(list)

        # user raw id, item raw id, translated rating, time stamp
        for urid, irid, r, timestamp in raw_trainset:
            try:
                uid = raw2inner_id_users[urid]
            except KeyError:
                uid = current_u_index
                raw2inner_id_users[urid] = current_u_index
                current_u_index += 1
            try:
                iid = raw2inner_id_items[irid]
            except KeyError:
                iid = current_i_index
                raw2inner_id_items[irid] = current_i_index
                current_i_index += 1

            ur[uid].append((iid, r))
            ir[iid].append((uid, r))

        n_users = len(ur)  # number of users
        n_items = len(ir)  # number of items
        n_ratings = len(raw_trainset)

        trainset = Trainset(ur,
                            ir,
                            n_users,
                            n_items,
                            n_ratings,
                            self.reader.rating_scale,
                            raw2inner_id_users,
                            raw2inner_id_items)

        return trainset

    def construct_testset(self, raw_testset):

        return [(ruid, riid, r_ui_trans)
                for (ruid, riid, r_ui_trans, _) in raw_testset]


class DatasetUserFolds(Dataset):
    

    def __init__(self, folds_files=None, reader=None):

        Dataset.__init__(self, reader)
        self.folds_files = folds_files

        # check that all files actually exist.
        for train_test_files in self.folds_files:
            for f in train_test_files:
                if not os.path.isfile(os.path.expanduser(f)):
                    raise ValueError('File ' + str(f) + ' does not exist.')


class DatasetAutoFolds(Dataset):
    

    def __init__(self, ratings_file=None, reader=None, df=None):

        Dataset.__init__(self, reader)
        self.has_been_split = False  # flag indicating if split() was called.

        if ratings_file is not None:
            self.ratings_file = ratings_file
            self.raw_ratings = self.read_ratings(self.ratings_file)
        elif df is not None:
            self.df = df
            self.raw_ratings = [(uid, iid, float(r), None)
                                for (uid, iid, r) in
                                self.df.itertuples(index=False)]
        else:
            raise ValueError('Must specify ratings file or dataframe.')

    def build_full_trainset(self):
        

        return self.construct_trainset(self.raw_ratings)
