"""
The :mod:`dump <QPQ.dump>` module defines the :func:`dump` function.
"""

import pickle


def dump(file_name, predictions=None, algo=None, verbose=0):
    """A basic wrapper around Pickle to serialize a list of prediction and/or
    an algorithm on drive.

    What is dumped is a dictionary with keys ``'predictions'`` and ``'algo'``.

    
    """

    dump_obj = {'predictions': predictions,
                'algo': algo
                }
    pickle.dump(dump_obj, open(file_name, 'wb'),
                protocol=pickle.HIGHEST_PROTOCOL)

    if verbose:
        print('The dump has been saved as file', file_name)


def load(file_name):
    """A basic wrapper around Pickle to deserialize a list of prediction and/or
    an algorithm that were dumped on drive using :func:`dump()
    <QPQ.dump.dump>`.

    

    """

    dump_obj = pickle.load(open(file_name, 'rb'))

    return dump_obj['predictions'], dump_obj['algo']
