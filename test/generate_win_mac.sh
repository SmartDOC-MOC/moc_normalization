#!/bin/sh
echo "Generating windows and mac test files from -nix file."
unix2dos --convmode ascii -n input-nixEOL-utf8.txt input-dosEOL-utf8.txt
unix2mac --convmode ascii -n input-nixEOL-utf8.txt input-macEOL-utf8.txt
echo "All done."
