#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unicode Explorer.
"""


# ==============================================================================
# Imports
import logging
import argparse
import sys
import unicodedata
import io
# import codecs

# ==============================================================================
# Logging
logger = logging.getLogger(__name__)

# ==============================================================================
# Constants
PROG_VERSION = "1.1"
PROG_DESCR = "OCR Result Explorer for ICDAR15 SmartDOC"
PROG_NAME = "moc_explorer"

ERRCODE_OK = 0
ERRCODE_NOFILE = 10

# ==============================================================================
# Utility private functions
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
    format="%(module)-9s %(levelname)-7s: %(message)s"
    formatter = logging.Formatter(format)    
    ch = logging.StreamHandler()  
    ch.setFormatter(formatter)  
    logger.addHandler(ch)
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logger.setLevel(level)

def _unichr2str(unichar):
    return unicodedata.name(unichar, repr(unichar))

# ==============================================================================
# Main function
def main():
    # Option parsing
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=PROG_DESCR, 
        version=PROG_VERSION)
    parser.add_argument('-d', '--debug', 
        action="store_true", 
        help="Activate debug output.")
    parser.add_argument('input', 
        help='Text file with UTF-8 encoding.')
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
    line_no = 0
    with io.open(args.input, 'r', encoding="UTF-8", newline=None, errors="strict") as file_input:
        # io lines are unicode code point sequences with LF-normalized EOL
        for line in file_input:
            line_no += 1
            char_no = 0
            print "l:%03d (%d char.)" % (line_no, len(line))
            print u"\"%s\"" % line.rstrip(u"\n")
            for char in line:
                char_no += 1
                print "\tc:%03d %04x %s" %  (char_no, ord(char), _unichr2str(char))

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

