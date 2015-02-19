#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unicode Explorer.

It gives line by line, character by character information about the content of 
an UTF-8 encoded file.
"""


# ==============================================================================
# Imports
import logging
import argparse
import sys
import unicodedata
import codecs
import locale
import io

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
ERRCODE_IOERROR = 20

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

    encoder = None
    logger.debug("sys.stdout.encoding = %s" % sys.stdout.encoding)
    if not sys.stdout.encoding or sys.stdout.encoding.upper() != 'UTF-8':
        encoding = sys.stdout.encoding or locale.getpreferredencoding()
        try:
            encoder = codecs.getwriter(encoding)
        except LookupError:
            logger.warn("Unknown encoding %s specified in locale().\n" % encoding)
            encoder = codecs.getwriter('UTF-8')
        if encoding.upper() != 'UTF-8':
            logger.warn("Stdout in %s format. Out-of-charset signs are represented in XML-coded format." % encoding)
        try:
            sys.stdout = encoder(sys.stdout.buffer, 'xmlcharrefreplace')
        except AttributeError:
            sys.stdout = encoder(sys.stdout, 'xmlcharrefreplace')

    line_no = 0
    try:
        with io.open(args.input, 'rt', encoding="UTF-8", newline=None, errors="strict") as file_input:
            for line in file_input:
                line_no += 1
                char_no = 0
                sys.stdout.write("l:%03d (%d char.)\n" % (line_no, len(line)))
                sys.stdout.write(line)
                for char in line:
                    char_no += 1
                    sys.stdout.write("\tc:%03d U+%04x %s\n" %  (char_no, ord(char), _unichr2str(char)))
    except IOError:
        logger.debug("IO Error.")
        return ERRCODE_IOERROR

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

