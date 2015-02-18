#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO LICENCE (or in separate file)

TODO description

Sample usage:
    normalize.py /path/to/utf-8/text/file.txt -o /path/to/normalized/output.txt

"""


# ==============================================================================
# Imports
import logging
import argparse
import os
import os.path
import sys
import fileinput
from collections import defaultdict
import re
import csv

# ==============================================================================
# Logging
logger = logging.getLogger(__name__)

# ==============================================================================
# Constants
PROG_VERSION = "0.1"
PROG_NAME = "OCR Result Normalized for ICDAR15 SmartDOC"
PROG_NAME_SHORT = "moc_norm"

ERRCODE_OK = 0
ERRCODE_NOFILE = 10

# ==============================================================================
# Utility private fonctions
def _dumpArgs(args, logger=logger):
    logger.debug("Arguments:")
    for (k, v) in args.__dict__.items():
        logger.debug("    %-20s = %s" % (k, v))

_DBGLINELEN = 80
_DBGSEP = "-"*_DBGLINELEN

def _programHeader(logger, prog_name, prog_version):
    logger.debug(_DBGSEP)
    dbg_head = "%s - v. %s" % (prog_name, prog_version)
    dbg_head_pre = " " * (max(0, (_DBGLINELEN - len(dbg_head)))/2)
    logger.debug(dbg_head_pre + dbg_head)

def _initLogger(logger, debug=False):
    format="%(name)-12s %(levelname)-7s: %(message)s" #%(module)-10s
    formatter = logging.Formatter(format)    
    ch = logging.StreamHandler()  
    ch.setFormatter(formatter)  
    logger.addHandler(ch)
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logger.setLevel(level)

# ==============================================================================
# Main function
def main():
    # Option parsing
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=PROG_NAME, 
        version=PROG_VERSION)
    parser.add_argument('-d', '--debug', 
        action="store_true", 
        help="Activate debug output.")
    parser.add_argument('-o', '--output', 
        help="Optional path to output file.")
    parser.add_argument('input', 
        help='Input text file with UTF-8 encoding.')
    args = parser.parse_args()

    # -----------------------------------------------------------------------------
    # Logger activation
    _initLogger(logger)
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # -----------------------------------------------------------------------------
    # Output log header
    _programHeader(logger, PROG_NAME, PROG_VERSION)
    logger.debug(_DBGSEP)
    _dumpArgs(args, logger)
    logger.debug(_DBGSEP)

    # --------------------------------------------------------------------------
    logger.debug("--- Process started. ---")
    
    
    

    logger.debug("--- Process complete. ---")
    # --------------------------------------------------------------------------

    logger.debug("Clean exit.")
    logger.debug(_DBGSEP)
    return ERRCODE_OK
    # --------------------------------------------------------------------------


# ==============================================================================
# Entry point
if __name__ == "__main__":
    sys.exit(main())

