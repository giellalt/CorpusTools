#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2013-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains classes to add files to a corpus directory."""


import argparse
import cgi
import os
import shutil

import requests

from corpustools import argparse_version, namechanger, util, versioncontrol, xslsetter


class AdderError(Exception):
    """Raise this exception when errors happen in this module."""


def add_url_extension(filename, content_type):
    """Add an extension to the file depending on the content type."""
    if filename == "":
        filename += "index"

    content_type_extension = {
        "text/html": ".html",
        "application/msword": ".doc",
        "application/pdf": ".pdf",
        "text/plain": ".txt",
    }

    for name, extension in content_type_extension.items():
        if name in content_type and not filename.endswith(extension):
            filename += extension

    return filename


def url_to_filename(response):
    """Compute the filename.

    Args:
        response (requests.get response).

    Returns:
        str: Name of the file.
    """
    try:
        _, params = cgi.parse_header(response.headers["Content-Disposition"])
        return params["filename"]
    except KeyError:
        return add_url_extension(
            os.path.basename(response.url), response.headers["content-type"]
        )


class UrlDownloader:
    """Download a document from a url."""

    def __init__(self, download_dir):
        """Initialise the UrlDownloader class.

        Args:
            download_dir: a string containing the path where the file should
            be saved.
        """
        self.download_dir = download_dir
        self.headers = {
            "user-agent": (
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) "
                "Gecko/20130331 Firefox/21.0"
            )
        }

    def download(self, url, wanted_name="", params=None):
        """Download a url to a temporary file.

        Return the request object and the name of the temporary file
        """
        try:
            request = requests.get(url, headers=self.headers, params=params)
            if request.status_code == requests.codes.ok:
                filename = wanted_name if wanted_name else url_to_filename(request)
                tmpname = os.path.join(self.download_dir, filename)
                with util.ignored(OSError):
                    os.makedirs(self.download_dir)
                with open(tmpname, "wb") as tmpfile:
                    tmpfile.write(request.content)

                return (request, tmpname)
            raise AdderError("ERROR:", url, "does not exist")
        except requests.exceptions.MissingSchema as error:
            raise AdderError(str(error))
        except requests.exceptions.ConnectionError as error:
            raise AdderError(str(error))


class AddToCorpus:
    """Class to add files, urls and dirs to the corpus."""

    def __init__(self, corpusdir, mainlang, path):
        """Initialise the AddToCorpus class.

        Args:
            corpusdir: (unicode) the directory where the corpus is
            mainlang: (unicode) three character long lang id (iso-639)
            path: (unicode) path below the language directory where the files
            should be added
        """
        if not os.path.isdir(corpusdir):
            raise AdderError(
                "The given corpus directory, {}, " "does not exist.".format(corpusdir)
            )

        if (
            len(mainlang) != 3
            or mainlang != mainlang.lower()
            or mainlang != namechanger.normalise_filename(mainlang)
        ):
            raise AdderError(
                "Invalid mainlang: {}. "
                "It must consist of three lowercase ascii "
                "letters".format(mainlang)
            )

        self.corpusdir = corpusdir
        self.vcs = versioncontrol.vcs(self.corpusdir)
        self.goaldir = os.path.join(
            corpusdir, "orig", mainlang, self.__normalise_path(path)
        )
        with util.ignored(OSError):
            os.makedirs(self.goaldir)
        self.additions = []

    @staticmethod
    def __normalise_path(path):
        """Normalise path.

        Args:
            path (str): Path that should be normalised.

        Returns:
            str: a normalised path
        """
        return "/".join(
            [namechanger.normalise_filename(part) for part in path.split("/")]
        )

    def copy_url_to_corpus(self, url, wanted_name="", parallelpath=""):
        """Add a URL to the corpus.

        Copy a downloaded url to the corpus
        """
        downloader = UrlDownloader(os.path.join(self.corpusdir, "tmp"))
        (request, tmpname) = downloader.download(url, wanted_name=wanted_name)

        return self.copy_file_to_corpus(
            origpath=tmpname, metadata_filename=request.url, parallelpath=parallelpath
        )

    def copy_file_to_corpus(self, origpath, metadata_filename, parallelpath=""):
        """Add a file from the hard disk to the corpus.

        Args:
            orig_path (str): path where the original file exists
            metadata_filename (str): the value of the filename in the
                metadata file
            parallelpath (str): where the parallel file of the original
                file exists in the corpus

        Returns:
            str: path to where the origfile exists in the corpus
        """
        none_dupe_path = self.none_dupe_path(origpath)
        shutil.copy(origpath, none_dupe_path)
        self.additions.append(none_dupe_path)

        self.add_metadata_to_corpus(none_dupe_path, metadata_filename)
        if parallelpath:
            self.update_parallel_data(util.split_path(none_dupe_path), parallelpath)
        print("Added", none_dupe_path)

        return none_dupe_path

    def add_metadata_to_corpus(self, none_dupe_path, meta_filename):
        """Add the metadata file to the corpus."""
        none_dupe_components = util.split_path(none_dupe_path)
        new_metadata = xslsetter.MetadataHandler(none_dupe_path + ".xsl", create=True)
        new_metadata.set_variable("filename", meta_filename)
        new_metadata.set_variable("mainlang", none_dupe_components.lang)
        new_metadata.set_variable("genre", none_dupe_components.genre)
        new_metadata.write_file()
        self.additions.append(none_dupe_path + ".xsl")

    @staticmethod
    def update_parallel_data(none_dupe_components, parallelpath):
        """Update metadata in the parallel files.

        Args:
            new_components: (util.PathComponents) of none_dupe_path
            parallelpath: (string) path of the parallel file
        """
        if not os.path.exists(parallelpath):
            raise AdderError(f"{parallelpath} does not exist")

        parallel_metadata = xslsetter.MetadataHandler(parallelpath + ".xsl")
        parallels = parallel_metadata.get_parallel_texts()
        parallels[none_dupe_components.lang] = none_dupe_components.basename

        parall_components = util.split_path(parallelpath)
        parallels[parall_components.lang] = parall_components.basename

        for lang, parallel in parallels.items():
            metadata = xslsetter.MetadataHandler(
                "/".join(
                    (
                        none_dupe_components.root,
                        none_dupe_components.module,
                        lang,
                        none_dupe_components.genre,
                        none_dupe_components.subdirs,
                        parallel + ".xsl",
                    )
                )
            )

            for lang1, parallel1 in parallels.items():
                if lang1 != lang:
                    metadata.set_parallel_text(lang1, parallel1)
            metadata.write_file()

    def none_dupe_path(self, path):
        """Compute the none duplicate path of the file to be added.

        Args:
            path: (string) path of the file as given as input
            This string may contain unwanted chars and
        """
        return namechanger.compute_new_basename(
            path,
            os.path.join(
                self.goaldir, namechanger.normalise_filename(os.path.basename(path))
            ),
        )

    def copy_files_in_dir_to_corpus(self, origpath):
        """Add a directory to the corpus.

        * Recursively walks through the given original directory
            * First checks for duplicates, raises an error printing a list
              of duplicate files if duplicates are found
            * For each file, do the "add file to the corpus" operations
              (minus the parallel info).

        """
        self.find_duplicates(origpath)
        for root, _, files in os.walk(origpath):
            for file_ in files:
                orig_f = os.path.join(root, file_)
                self.copy_file_to_corpus(origpath=orig_f, metadata_filename=orig_f)

    @staticmethod
    def find_duplicates(origpath):
        """Find duplicates based on the hex digests of the corpus files."""
        duplicates = {}
        for root, _, files in os.walk(origpath):
            for file_ in files:
                path = os.path.join(root, file_)
                with open(path, "rb") as content:
                    file_hash = namechanger.compute_hexdigest(content)
                    if file_hash in duplicates:
                        duplicates[file_hash].append(path)
                    else:
                        duplicates[file_hash] = [path]

        results = list(x for x in list(duplicates.values()) if len(x) > 1)
        if results:
            print("Duplicates Found:")
            print("___")
            for result in results:
                for subresult in result:
                    print(f"\t{subresult}")
                print("___")

            raise AdderError("Found duplicates")

    def add_files_to_working_copy(self):
        """Add the downloaded files to the working copy."""
        self.vcs.add(self.additions)


def parse_args():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Add file(s) to a corpus directory. The filenames are "
        "converted to ascii only names. Metadata files containing the "
        "original name, the main language, the genre and possibly parallel "
        "files are also made. The files are added to the working copy.",
    )
    parser.add_argument(
        "origs",
        nargs="+",
        help="The original files, urls or directories where "
        "the original files reside (not the corpus repository)",
    )
    parser.add_argument(
        "--name",
        dest="name",
        help="Specify the name of the file in the corpus. "
        "Especially files fetched from the net often have "
        "names that are not human friendly. Use this "
        "option to guard against that.",
    )

    parallel = parser.add_argument_group("parallel")
    parallel.add_argument(
        "-p",
        "--parallel",
        dest="parallel_file",
        help="Path to an existing file in the corpus that "
        "will be parallel to the orig that is about to be added",
    )
    parallel.add_argument(
        "-l", "--lang", dest="lang", help="Language of the file to be added"
    )

    no_parallel = parser.add_argument_group("no_parallel")
    no_parallel.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="The directory where the origs should be placed",
    )

    return parser.parse_args()


def main():
    """Add files, directories and urls to the corpus."""
    args = parse_args()

    if args.parallel_file is None:
        if args.lang is not None:
            raise SystemExit(
                "The argument -l|--lang is not allowed together with " "-d|--directory"
            )
        (root, _, lang, genre, path, _) = util.split_path(
            os.path.join(args.directory, "dummy.txt")
        )
        if genre == "dummy.txt":
            raise SystemExit(
                "Error!\n"
                "You must add genre to the directory\ne.g. {}".format(
                    os.path.join(args.directory, "admin")
                )
            )

        adder = AddToCorpus(root, lang, os.path.join(genre, path))
        for orig in args.origs:
            if os.path.isfile(orig):
                if args.name:
                    newname = os.path.join(os.path.dirname(orig), args.name)
                    try:
                        shutil.copy(orig, newname)
                    except FileNotFoundError:
                        raise SystemExit(f"Not a valid filename: {args.name}")
                    orig = newname

                adder.copy_file_to_corpus(
                    origpath=orig, metadata_filename=os.path.basename(orig)
                )
            elif orig.startswith("http"):
                adder.copy_url_to_corpus(orig, wanted_name=args.name)
            elif os.path.isdir(orig):
                if args.name:
                    raise SystemExit(
                        "It makes no sense to use the --name "
                        "option together with --directory."
                    )
                adder.copy_files_in_dir_to_corpus(orig)
            else:
                raise SystemExit(
                    "Cannot handle the orig named: {}.\n"
                    "If you used the --name option and a name with spaces, "
                    "encase it in quote marks.".format(orig)
                )
    else:
        if args.directory is not None:
            raise SystemExit(
                "The argument -d|--directory is not allowed together with "
                "-p|--parallel\n"
                "Only -l|--lang is allowed together with -p|--parallel"
            )
        (root, _, lang, genre, path, _) = util.split_path(args.parallel_file)
        adder = AddToCorpus(root, args.lang, os.path.join(genre, path))

        if not os.path.exists(args.parallel_file):
            raise SystemExit(
                "The given parallel file\n\t{}\n"
                "does not exist".format(args.parallel_file)
            )
        if len(args.origs) > 1:
            raise SystemExit(
                "When the -p option is given, it only makes "
                "sense to add one file at a time."
            )
        if len(args.origs) == 1 and os.path.isdir(args.origs[-1]):
            raise SystemExit(
                "It is not possible to add a directory " "when the -p option is given."
            )
        orig = args.origs[0]
        if os.path.isfile(orig):
            if args.name:
                newname = os.path.join(os.path.dirname(orig), args.name)
                shutil.copy(orig, newname)
                orig = newname
            adder.copy_file_to_corpus(
                origpath=orig, metadata_filename=orig, parallelpath=args.parallel_file
            )
        elif orig.startswith("http"):
            adder.copy_url_to_corpus(
                orig, wanted_name=args.name, parallelpath=args.parallel_file
            )

    adder.add_files_to_working_copy()
