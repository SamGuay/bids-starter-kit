#!/usr/bin/env python
#
# Detect Latin abbreviations that can be difficult for screenreaders and non-native English speakers
#
# This script initially adopted from The Turing Way from in October 2020.
# doi:10.5281/zenodo.3233853
# https://github.com/alan-turing-institute/the-turing-way/blob/af98c94/tests/no-bad-latin.py
import argparse
import os
import re

from pull_files import filter_files

HERE = os.getcwd()
ABSOLUTE_HERE = os.path.dirname(HERE)
IGNORE_LIST = ["CHANGES.md"]


def parse_args():
    """Construct command line interface for parsing Pull Request number"""
    DESCRIPTION = "Script to check for latin phrases in Markdown files"
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        "--pull-request",
        type=str,
        default=None,
        help="If the script is being run on a Pull Request, parse the PR number",
    )

    return parser.parse_args()


def remove_comments(text_string: str) -> str:
    """Function to omit  html comment identifiers in a text string using
    regular expression matches

    Arguments:
        text_string -- The text to be matched

    Returns:
        The input text string with html comments removed
    """
    return re.sub("(?s)<!--(.*?)-->", "", text_string)


def get_lines(text_string: str, sub_string: str) -> list:
    """Get individual lines in a text file

    Arguments:
        text_string -- The text string to test
        sub_string -- The conditional string to perform splitting on

    Returns:
        A list of split strings
    """
    return [line for line in text_string.split("\n") if sub_string in line]


def construct_error_message(files_dict: dict) -> str:
    """Function to construct an error message pointing out where bad latin
    phrases appear in lines of text

    Arguments:
        files_dict -- Dictionary of failing files containing the
                      bad latin phrases and offending lines

    Returns:
        The error message to be raised
    """
    error_message = ["Bad latin found in the following files:\n"]

    for file in files_dict.keys():
        error_message.append(
            f"{file}:\t{files_dict[file]['latin_type']}\tfound in line\t[{files_dict[file]['line']}]\n"
        )

    return "\n".join(error_message)


def read_and_check_files(files: list) -> dict:
    """Function to read in files, remove html comments and check for bad latin
    phrases

    Arguments:
        files -- List of filenames to be checked

    Returns:
        Dictionary: Top level keys are absolute filepaths to files
        that failed the check. Each of these has two keys:
        'latin_type' containing the unwanted latin phrase, and 'line'
        containing the offending line.
    """
    failing_files = {}
    bad_latin = ["i.e.", "i.e ", " ie ", "e.g.", "e.g ", "e.t.c.", " etc", "et cetera"]

    for filename in files:
        if os.path.basename(filename) not in IGNORE_LIST:
            try:
                with open(
                    os.path.join(ABSOLUTE_HERE, filename),
                    encoding="utf8",
                    errors="ignore",
                ) as f:
                    text = f.read()
                    text = remove_comments(text)

                    for latin_type in bad_latin:
                        if latin_type in text.lower():
                            lines = get_lines(text.lower(), latin_type)
                            for line in lines:
                                failing_files[os.path.abspath(filename)] = {
                                    "latin_type": latin_type,
                                    "line": line,
                                }
            except FileNotFoundError:
                pass

    return failing_files


def get_all_files(directory=os.path.join(ABSOLUTE_HERE, "src")) -> list:
    """Get a list of files to be checked. Ignores images, javascript, css files.

    Keyword Arguments:
        directory {string} -- The directory containing the files to check

    Returns:
        List of files to check
    """
    files = []
    filetypes_to_ignore = (".png", ".jpg", ".js", ".css")

    for rootdir, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith(filetypes_to_ignore):
                files.append(os.path.join(rootdir, filename))

    return files


def main():
    """Main function"""
    args = parse_args()

    if args.pull_request is not None:
        files = filter_files(args.pull_request)
    else:
        files = get_all_files()

    failing_files = read_and_check_files(files)

    if bool(failing_files):
        error_message = construct_error_message(failing_files)
        raise Exception(error_message)


if __name__ == "__main__":
    main()
