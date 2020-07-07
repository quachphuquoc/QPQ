'''This module contains the Trainset class.'''


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from six import iteritems


class Trainset:
    """A trainset contains all useful data that constitute a training set.

    It is used by the :meth:`fit()
    <QPQ.prediction_algorithms.algo_base.AlgoBase.fit>` method of every
    prediction algorithm. You should not try to build such an object on your
    own but rather use the :meth:`Dataset.folds()
    <QPQ.dataset.Dataset.folds>` method or the
    :meth:`DatasetAutoFolds.build_full_trainset()
    <QPQ.dataset.DatasetAutoFolds.build_full_trainset>` method.

    Trainsets are different from :class:`Datasets <QPQ.dataset.Dataset>`.
    You can think of a :class:`Dataset <QPQ.dataset.Dataset>` as the raw
    data, and Trainsets as higher-level data where useful methods are defined.
    Also, a :class:`Dataset <QPQ.dataset.Dataset>` may be comprised of
    multiple Trainsets (e.g. when doing cross validation).


    Attributes:
        ur(:obj:`defaultdict` of :obj:`list`): The users ratings. This is a
            dictionary containing lists of tuples of the form ``(item_inner_id,
            rating)``. The keys are user inner ids.
        ir(:obj:`defaultdict` of :obj:`list`): The items ratings. This is a
            dictionary containing lists of tuples of the form ``(user_inner_id,
            rating)``. The keys are item inner ids.
        n_users: Total number of users :math:`|U|`.
        n_items: Total number of items :math:`|I|`.
        n_ratings: Total number of ratings :math:`|R_{train}|`.
        rating_scale(tuple): The minimum and maximal rating of the rating
            scale.
        global_mean: The mean of all ratings :math:`\\mu`.
    """

    def __init__(self, ur, ir, n_users, n_items, n_ratings, rating_scale,
                 raw2inner_id_users, raw2inner_id_items):

        self.ur = ur
        self.ir = ir
        self.n_users = n_users
        self.n_items = n_items
        self.n_ratings = n_ratings
        self.rating_scale = rating_scale
        self._raw2inner_id_users = raw2inner_id_users
        self._raw2inner_id_items = raw2inner_id_items
        self._global_mean = None
        # inner2raw dicts could be built right now (or even before) but they
        # are not always useful so we wait until we need them.
        self._inner2raw_id_users = None
        self._inner2raw_id_items = None

    def knows_user(self, uid):
        

        return uid in self.ur

    def knows_item(self, iid):
        

        return iid in self.ir

    def to_inner_uid(self, ruid):
        

        try:
            return self._raw2inner_id_users[ruid]
        except KeyError:
            raise ValueError('User ' + str(ruid) +
                             ' is not part of the trainset.')

    def to_raw_uid(self, iuid):
        

        if self._inner2raw_id_users is None:
            self._inner2raw_id_users = {inner: raw for (raw, inner) in
                                        iteritems(self._raw2inner_id_users)}

        try:
            return self._inner2raw_id_users[iuid]
        except KeyError:
            raise ValueError(str(iuid) + ' is not a valid inner id.')

    def to_inner_iid(self, riid):
        

        try:
            return self._raw2inner_id_items[riid]
        except KeyError:
            raise ValueError('Item ' + str(riid) +
                             ' is not part of the trainset.')

    def to_raw_iid(self, iiid):
        

        if self._inner2raw_id_items is None:
            self._inner2raw_id_items = {inner: raw for (raw, inner) in
                                        iteritems(self._raw2inner_id_items)}

        try:
            return self._inner2raw_id_items[iiid]
        except KeyError:
            raise ValueError(str(iiid) + ' is not a valid inner id.')

    def all_ratings(self):
        """Generator function to iterate over all ratings.

        Yields:
            A tuple ``(uid, iid, rating)`` where ids are inner ids (see
            :ref:`this note <raw_inner_note>`).
        """

        for u, u_ratings in iteritems(self.ur):
            for i, r in u_ratings:
                yield u, i, r

    def build_testset(self):
        

        return [(self.to_raw_uid(u), self.to_raw_iid(i), r)
                for (u, i, r) in self.all_ratings()]

    def build_anti_testset(self, fill=None):
        
        fill = self.global_mean if fill is None else float(fill)

        anti_testset = []
        for u in self.all_users():
            user_items = set([j for (j, _) in self.ur[u]])
            anti_testset += [(self.to_raw_uid(u), self.to_raw_iid(i), fill) for
                             i in self.all_items() if
                             i not in user_items]
        return anti_testset

    def all_users(self):
        
        return range(self.n_users)

    def all_items(self):
        
        return range(self.n_items)

    @property
    def global_mean(self):
        """Return the mean of all ratings.

        It's only computed once."""
        if self._global_mean is None:
            self._global_mean = np.mean([r for (_, _, r) in
                                         self.all_ratings()])

        return self._global_mean
