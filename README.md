# SmartDOC-MOC Normalization Tools

Programs included in this project form the basis for checking and normalizing participants results for the challenge 2 ("Mobile OCR Challenge") of the SmartDOC competition at ICDAR 2015.

The official website for the competition is at <http://l3i.univ-larochelle.fr/icdar2015smartdoc>.


## Summary for competition participants

The only thing you should know about this project is that the file `check.py` is the one you need to check that your results do not contain illegal characters.

To control one of your files, simply use:

```shell
python check.py /path/to/some/result.txt
```

Example with a **good file**:
```shell
$ python check.py test/input-dosEOL-utf8.txt 
check     INFO   : Input file contains only legal characters. Great!
```

Example with a **bad file**:
```shell
$ python check.py test/extra_chars.txt 
check     ERROR  : Got 13 illegal character(s) in line 215 : 
check     ERROR  :  l:215 c:003 LATIN SMALL LETTER DOTLESS I
check     ERROR  :  l:215 c:023 CARON
check     ERROR  :  l:215 c:025 BREVE
check     ERROR  :  l:215 c:027 DOT ABOVE
check     ERROR  :  l:215 c:029 RING ABOVE
check     ERROR  :   ... and 8 other(s).
[...]
check     ERROR  : --------------------------------------------------------------------------------
check     ERROR  : Input file contains 91 illegal characters.
check     ERROR  : Please review previous error messages and fix them before submitting your results.
check     ERROR  : --------------------------------------------------------------------------------
```

Requirements:
* This program requires Python 2, (>= 2.6) and was tested on recent versions of Windows, Linux and Mac OSX.
* Your files MUST BE encoded with UTF-8.


## Package content

The current package contains the following programs:
- `check.py`: checks text files to ensure they contain only legal characters
- `normalize.py`: checks and normalizes participants results, and will be used before computing OCR accuracy
- `explore.py`: gives line by line, character by character information about the content of an UTF-8 encoded file

It also contains several documents:
- `LICENCE`: GPL-v3 license details
- `README.md`: this file
- `char_mapping.ods`: Spreadsheet file (Libreoffice Calc format) containing details about the allowed character set and the normalization performed


## Installation

To use the programs, you will need Python 2, (>= 2.6) and was tested on recent versions of Windows, Linux and Mac OSX.

Then, simply checkout or download the programs you need, and call them from command line:

```shell
# Check whether a result is valid
python check.py /path/to/some/result.txt

# Perform the same normalization as the organizers
python normalize.py /path/to/some/result.txt /path/to/normalized/output.txt

# Review the Unicode content of a file
python explore.py /path/to/some/result.txt
```

You can review the command line syntax with the `-h` option for all programs.


## Design choices

We chose to implement this solution as independent Python 2 scripts for several reasons:

- Portability: Python 2 is widely available on many platforms
- Simplicity: No compilation required, works from any directory, no configuration
- Robustness: Python has excellent Unicode support
- Openness: Participants can review, reuse and improve our methods


## Licenses

All programs (`check.py`, `explore.py`, and `normalize.py`) are licensed under the GPL v3 license. We recommend you check <http://choosealicense.com/licenses/gpl-3.0/> for an uncomplicated explanation of what is required, permitted and forbidden when you redistribute those programs.

The character mapping table (`char_mapping.ods`) is licensed under the Creative Commons Attribution 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/.


## Contacting the authors

Please check the official competition website at <http://l3i.univ-larochelle.fr/icdar2015smartdoc> to contact the authors.

