#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO LICENCE (or in separate file)

TODO description

End of line MUST BE either CRLF (Windows), CR (old Macintosh) or LF (OSX, *nix).

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
PROG_VERSION = "0.1"
PROG_DESCR = "OCR Result Normalizer for ICDAR15 SmartDOC"
PROG_NAME = "moc_norm"

ERRCODE_OK = 0
ERRCODE_NOFILE = 10

ALLOWED_INPUT=u"""	 !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿŒœŠšŸŽžƒˆ˜–—‘’‚“”„†‡•…‰‹›€™ﬁﬂﬀﬃﬄ"""
CHAR_ERR_LIM = 5

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
            file_output = open(args.output, 'w')
            fo_is_real_file = True
        else:
            file_output = sys.stdout
            logger.info("Output results to stdout.")

        logger.debug("--- Process started. ---")
        line_no = 0
        # with codecs.open(args.input, 'r', "UTF-8") as file_input:
        with io.open(args.input, 'r') as file_input:
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
                if extra_chars:
                    logger.error("Got illegal %d character(s) in line %d : " % (len(extra_chars), line_no))
                    for i in range(min(CHAR_ERR_LIM, len(extra_chars))):
                        char, pos = extra_chars[i]
                        logger.error("\tl:%03d c:%03d %s" %  (line_no, pos, _unichr2str(char)))
                    if len(extra_chars) > CHAR_ERR_LIM:
                        logger.error("\t ... and %d other(s)." % (len(extra_chars) - CHAR_ERR_LIM))

                # TODO Perform custom translations
                # replace line
                line_tr = line

                # Unicode normalization 
                line_norm = unicodedata.normalize('NFKC', line_tr)

                # Output new line
                print >>file_output, line_norm.encode("UTF-8"),
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

