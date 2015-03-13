import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pprint
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('test_findr.log', mode="w"))
logger.setLevel(logging.DEBUG)
from afrift.findr_files import Finder

def test_findr():
    "test routine"
    ## import logging
    ## logging.basicConfig(filename='findr_files.log')
    ## logger = logging.getLogger(__name__)
    h = Finder(
        zoek="logging",
        vervang=None, # "voor",
        pad='/home/albert/projects/filefindr',
        #filelist=['test.py.txt',],
        extlist = ['py'], # [".txt",".ini"],
        subdirs=True, # zoeken in subdirectories
        ## case=True, # case-sensitive ja/nee
        woord=True, # woord/woorddeel
        regexp=True,  # zoekstring is regexp
        #backup=True
        )
    for x, y in sorted(h.p.items()):
        logger.info("%s: %s" % (x, y))
    h.do_action()
    for x in h.rpt:
        logger.info("%s" % x)

def test_findr_complex():
    def do_stuff(data, regexp=False):
        h = Finder(
            zoek=data,
            vervang=None,
            filelist=['/home/albert/projects/filefindr/sample.txt',],
            regexp=regexp,
            use_complex=True)
        for item in ('zoek', 'wijzig', 'regexp'):
            if item in h.p:
                logger.info("%s: %s" % (item, h.p[item]))
        for x in h.rpt:
            logger.info("%s" % x)
        logger.info(h.re)
        logger.info(h.ignore)
        h.do_action()
        for x in h.rpt:
            logger.info("%s" % x)
    for use_this in ( #'',
            'def',
            '"def"',
            'def, test',
            'def + test',
            'def - test',
            'def - test - class',
            '"def, test"',
            '"def + test"',
            '"def - test"',
            'def, test, "def + test" + snork + "dit, ook", "nog wat"'):
        do_stuff(use_this)
        do_stuff(use_this, regexp=True)

if __name__ == '__main__':
    ## test_findr()
    test_findr_complex()
