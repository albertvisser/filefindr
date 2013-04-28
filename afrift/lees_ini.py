# lees afrift.ini
import pickle
import pprint

p = {}
with open("afrift.ini", 'rb') as f_in:
    pickled = True
    try:
        mru_items = pickle.load(f_in)
    except pickle.PickleError:
        pickled = False
    if pickled:
        for opt in ("case", "woord", "subdirs"):
            p[opt] = pickle.load(f_in)
if pickled:
    pprint.pprint(mru_items)
    pprint.pprint(p)

