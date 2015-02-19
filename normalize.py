#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO LICENCE (or in separate file)


This file is part of the tools used for the evaluation of OCR accuracy in the 
context of the challenge 2 "Mobile OCR Challenge" of the SmartDOC competition 
at ICDAR 2015. This particular program checks and normalizes participants 
results, and is used before computing OCR accuracy.

Normalization performed here is idempotent.

Warning:
    End of line can be EITHER CRLF (Windows), CR (old Macintosh) or LF (OSX, 
    *nix).

Sample usage:
    normalize.py /path/to/utf-8/text/file.txt -o /path/to/normalized/output.txt

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
PROG_DESCR = "OCR Result Normalizer for ICDAR15 SmartDOC"
PROG_NAME = "moc_norm"

ERRCODE_OK = 0
ERRCODE_NOFILE = 10

ALLOWED_INPUT = u""" !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿŒœŠšŸŽžƒˆ˜–—‘’‚“”„†‡•…‰‹›€™ﬁﬂﬀﬃﬄ"""
# Horizontal tab added separately for convenience
ALLOWED_INPUT += u"\u0009"
# additions due to Unicode normalization:
# - 0308 COMBINING DIAERESIS
# - 0301 COMBINING ACUTE ACCENT 
# - 03BC GREEK SMALL LETTER MU  
# - 0327 COMBINING CEDILLA  
# - 0303 COMBINING TILDE
# - 0304 COMBINING MACRON   
# - 2044 FRACTION SLASH 
ALLOWED_INPUT += u"\u0308\u0301\u03BC\u0327\u0303\u0304\u2044"

TRANSFORMATIONS = [
    (u"\u0009", u" "), # HTAB to SPACE
    (u"\u00A0", u" "), # NBSP to SPACE
    (u"¦", u"|"), # U+00A6 # Commonly interchanged
# ¨ U+00A8 to U+0020 U+0308    ̈
# ª U+00AA to U+0061  a
    (u"«", u"\""), # U+00AB
    (u"\u00AD", u""), # remove SOFT HYPHEN
# ¯ U+00AF to U+0020 U+0304    ̄
# ² U+00B2 to U+0032  2
# ³ U+00B3 to U+0033  3
# ´ U+00B4 to U+0020 U+0301    ́
# µ U+00B5 to U+03BC  μ
# ¸ U+00B8 to U+0020 U+0327    ̧
# ¹ U+00B9 to U+0031  1
# º U+00BA to U+006F  o
    (u"»", u"\""), # U+00BB
# ¼ U+00BC to U+0031 U+002F U+0034  1/4 # done by FRACTION SLASH replace after norm.
# ½ U+00BD to U+0031 U+002F U+0032  1/2 # done by FRACTION SLASH replace after norm.
# ¾ U+00BE to U+0033 U+002F U+0034  3/4 # done by FRACTION SLASH replace after norm.
    (u"Æ", u"AE"), # U+00C6
    (u"æ", u"ae"), # U+00E6
    (u"Œ", u"OE"), # U+0152
    (u"œ", u"oe"), # U+0153
#˜   U+02DC to U+0020 U+0303    ̃
    (u"–", u"-"), # U+2013
    (u"—", u"-"), # U+2014
    (u"‘", u"\'"), # U+2018
    (u"’", u"\'"), # U+2019
    (u"‚", u"\'"), # U+201A
    (u"“", u"\""), # U+201C
    (u"”", u"\""), # U+201D
    (u"„", u"\""), # U+201E
# …   U+2026 to U+002E U+002E U+002E    ...
    (u"‹", u"\'"), # U+2039
    (u"›", u"\'"), # U+203A
# ™   U+2122 to U+0054 U+004D   TM
    # (u"\uFB00", u"ff"),  # Replace ff, fi, fl, ffi, ffl ligatures with separated 
    # (u"\uFB01", u"fi"),  # chars. before Unicode normalization inserts
    # (u"\uFB02", u"fl"),  # "200c ZERO WIDTH NON-JOINER"
    # (u"\uFB03", u"ffi"), # (actually not wrote to UTF-8 output so not done here)
    # (u"\uFB04", u"ffl"),
    (u"⁄", u"/"), # FRACTION SLASH U+2044
    ]

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
        help='Input text file with UTF-8 encoding.')
    parser.add_argument('-o', '--output', 
        help="Optional path to output file.")
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

    file_output = None
    fo_is_real_file = False
    try:
        if args.output:
            # file_output = codecs.open(args.output, 'w', "UTF-8")
            file_output = open(args.output, "w") # FIXME specify target encoding and EOL
            fo_is_real_file = True
        else:
            file_output = sys.stdout
            logger.info("Output results to stdout.")
            # FIXME detect necessary encoding here, subst. policy and warn if necessary

        logger.debug("--- Process started. ---")
        line_no = 0
        # with codecs.open(args.input, 'r', "UTF-8") as file_input:
        with io.open(args.input, "rt", encoding="UTF-8", newline=None, errors="strict") as file_input:
            # io lines are unicode code point sequences with LF-normalized EOL
            for line in file_input:
                line_no += 1

                # Check input
                extra_chars = []
                char_no = 0
                for char in line:
                    char_no += 1
                    if char not in charset:
                        extra_chars.append((char, char_no))
                    # logger.debug("\tl:%03d c:%03d %04x %s" %  (line_no, char_no, ord(char), _unichr2str(char)))
                if extra_chars:
                    logger.error("Got illegal %d character(s) in line %d : " % (len(extra_chars), line_no))
                    for i in range(min(CHAR_ERR_LIM, len(extra_chars))):
                        char, pos = extra_chars[i]
                        logger.error("\tl:%03d c:%03d %s" %  (line_no, pos, _unichr2str(char)))
                    if len(extra_chars) > CHAR_ERR_LIM:
                        logger.error("\t ... and %d other(s)." % (len(extra_chars) - CHAR_ERR_LIM))

                # Unicode normalization
                line_norm = unicodedata.normalize('NFKC', line)
                
                # Perform custom translations
                line_tr = _transform(line_norm)

                # Output new line
                print >>file_output, line_tr.encode("UTF-8"), 
                # FIXME encoding must be done at the output driver level, warning for unsupported charset if required
                # Use io.TextIOBase.write()


    finally:
        if fo_is_real_file:
            file_output.close()

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

