#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO LICENCE (or in separate file)
"""
This program checks text files to ensure they contain only legal characters.

This file is part of the tools used for the evaluation of OCR accuracy in the 
context of the challenge 2 "Mobile OCR Challenge" of the SmartDOC competition 
at ICDAR 2015. 

Sample usage:
    check.py /path/to/utf-8/text/file.txt

"""

# ==============================================================================
# Imports
import logging
import argparse
import sys
import unicodedata
import io

# ==============================================================================
# Logging
logger = logging.getLogger(__name__)

# ==============================================================================
# Constants
PROG_VERSION = "1.0"
PROG_DESCR = "OCR Result Checker for ICDAR15 SmartDOC"
PROG_NAME = "moc_check"

ERRCODE_OK = 0
ERRCODE_NOFILE = 10
ERRCODE_EXTRACHAR = 50

ALLOWED_INPUT = (
    u""" !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abc"""
    u"""defghijklmnopqrstuvwxyz{|}~ ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉ"""
    u"""ÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿŒœŠšŸŽžƒˆ˜–—‘’"""
    u"""‚“”„†‡•…‰‹›€™ﬁﬂﬀﬃﬄ"""
# Horizontal tab added separately for convenience
    u"\u0009"
# additions due to Unicode normalization:
# - 0308 COMBINING DIAERESIS
# - 0301 COMBINING ACUTE ACCENT 
# - 03BC GREEK SMALL LETTER MU  
# - 0327 COMBINING CEDILLA  
# - 0303 COMBINING TILDE
# - 0304 COMBINING MACRON   
# - 2044 FRACTION SLASH 
    u"\u0308\u0301\u03BC\u0327\u0303\u0304\u2044"
    )


CHAR_ERR_LIM = 5

# ==============================================================================
def _transform(unistr):
    s2 = unistr
    for fr, to in TRANSFORMATIONS:
        s2 = s2.replace(fr, to)
    return s2

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
        help='File to control.')
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
    charset = ALLOWED_INPUT + u'\u000a' # Tolerate '\n' (LF) EOL

    logger.debug("--- Process started. ---")
    line_no = 0
    err_count = 0
    with io.open(args.input, "rt", encoding="UTF-8", newline=None, 
                 errors="strict") as file_input:
        for line in file_input:
            line_no += 1
            extra_chars = []
            char_no = 0
            for char in line:
                char_no += 1
                if char not in charset:
                    extra_chars.append((char, char_no))
                    err_count += 1
            if extra_chars:
                logger.error("Got %d illegal character(s) in line %d : " 
                             % (len(extra_chars), line_no))
                for i in range(min(CHAR_ERR_LIM, len(extra_chars))):
                    char, pos = extra_chars[i]
                    logger.error("\tl:%03d c:%03d %s" 
                                 % (line_no, pos, _unichr2str(char)))
                if len(extra_chars) > CHAR_ERR_LIM:
                    logger.error("\t ... and %d other(s)." 
                                 % (len(extra_chars) - CHAR_ERR_LIM))

    logger.debug("--- Process complete. ---")
    # --------------------------------------------------------------------------
    ret_code = ERRCODE_OK
    if err_count > 0:
        logger.error(_DBGSEP)
        logger.error("Input file contains %d illegal characters." % err_count)
        logger.error("Please review previous error messages and "
                     "fix them before submitting your results.")
        logger.error(_DBGSEP)
        ret_code = ERRCODE_EXTRACHAR
    else:
        logger.info("Input file contains only legal characters. Great!")

    logger.debug("Clean exit.")
    logger.debug(_DBGSEP)
    return ret_code
    # --------------------------------------------------------------------------

# ==============================================================================
# Entry point
if __name__ == "__main__":
    sys.exit(main())

