"""test routines
"""
import sys
## import os
import pathlib
HERE = pathlib.Path(__file__).parent.resolve()
ROOT = HERE.parent
sys.path.append(str(ROOT))
import pickle
import pprint
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(str(HERE / 'test_abase.log'), mode="w"))
logger.setLevel(logging.DEBUG)
from afrift.afrift_base import ABase


def lees_ini():
    """test routine
    """
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
        logger.info(pprint.pformat(mru_items))
        logger.info(pprint.pformat(p))
    else:
        logger.info("ini lezen ging mis - geen pickle file?")


def test_abase(parent=None, apptype="", fnaam=""):
    """test routine
    """
    logger.info("\ntesting Abase with apptype = %s, filename = %s", apptype, fnaam)
    abase = ABase(parent=parent, apptype=apptype, fnaam=fnaam)
    logger.info(pprint.pformat(abase.__dict__))
    if not abase.pickled:
        logger.info('Settings in oud formaat, konden niet gelezen worden')
    abase.schrijfini()
    lees_ini()


if __name__ == '__main__':
    test_abase()
    for item in ("glug", "single", "multi"):
        try:
            test_abase(apptype=item)
        except ValueError as err:
            logger.info(str(err))
    for item, naam in (("single", "test_afrift_base.py"),
                       ("multi", "afrift_args")):
        try:
            test_abase(apptype=item, fnaam=naam)
        except ValueError as err:
            logger.info(str(err))
