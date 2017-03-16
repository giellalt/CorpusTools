# -*- coding: utf-8 -*-

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
#   Copyright © 2011-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Classes and functions to sentence align two files."""


from __future__ import absolute_import, print_function, unicode_literals

import argparse
import codecs
import io
import os
import re
import subprocess
import tempfile

from lxml import etree
import six

from corpustools import (argparse_version, ccat, corpusxmlfile,
                         generate_anchor_list, modes, util)

HERE = os.path.dirname(__file__)


def to_plain_text(lang, filename):
    """Turn an xml formatted file into clean text.

    Arguments:
        lang (str): three character name of main language of document.
        filename (str): name of the xmlfile

    Raises:
        UserWarning: if there is no text, raise a UserWarning

    Returns:
        str: the content of ccat output
    """
    xml_printer = ccat.XMLPrinter(lang=lang, all_paragraphs=True)
    xml_printer.parse_file(filename)
    text = xml_printer.process_file().getvalue()
    if text:
        return text
    else:
        raise UserWarning('Empty file {}'.format(filename))


class SentenceDivider(object):
    """A class to divide plain text output into sentences.

    Uses hfst-tokenise as the motor for this purpose.

    Attributes:
        lang (str): three character language code
        relative_path (str): relative path to where files needed by
            modes.xml are found.
        stops (list of str): tokens that imply where a sentence ends.
    """

    stops = [';', '!', '?', '.', '..', '...', '¶', '…']

    def __init__(self,
                 lang,
                 relative_path=os.path.join(
                     os.getenv('GTHOME'), 'langs')):
        """Set the files needed by preprocess.

        Arguments:
            lang (str): language the analyser can analyse
        """
        self.lang = lang
        self.relative_path = relative_path

    def setup_pipeline(self):
        """Setup the preprocess pipeline.

        Returns:
            modes.Pipeline: a preprocess pipeline that receives plain text
                input and outputs a token per line.
        """
        modefile = etree.parse(
            os.path.join(os.path.dirname(__file__), 'xml/modes.xml'))
        pipeline = modes.Pipeline(
            mode=modefile.find('.//mode[@name="{}"]'.format('preprocess')),
            relative_path=os.path.join(self.relative_path, self.lang))
        pipeline.sanity_check()

        return pipeline

    @staticmethod
    def clean_sentence(sentence):
        """Remove cruft from a sentence.

        Arguments:
            sentence (str): a raw sentence, warts and all

        Returns:
            str: a cleaned up sentence, looking the way a sentence should.
        """
        return sentence.replace('\n', '').strip()

    def make_sentences(self, ccat_output):
        """Turn ccat output into cleaned up sentences.

        Arguments:
            ccat_output (str): plain text output of ccat.

        Yields:
            str: a cleaned up sentence
        """
        pipeline = self.setup_pipeline()
        preprocessed = pipeline.run(ccat_output.encode('utf8'))

        token_buffer = []
        for token in io.StringIO(preprocessed):
            token_buffer.append(token)
            if token.strip() in self.stops:
                yield self.clean_sentence(''.join(token_buffer))
                token_buffer[:] = []

    def make_valid_sentences(self, ccat_output):
        """Turn ccat output into full sentences.

        Arguments:
            ccat_output (str): the plain text output of ccat

        Returns:
            list of str: The ccat output has been turned into a list
                of full sentences.
        """
        sentences = [
            sentence.replace(' ¶', '')
            for sentence in self.make_sentences(ccat_output)
            if sentence not in self.stops]

        invalid_sentence_re = re.compile('^\W+$')
        valid_sentences = []
        for sentence in sentences:
            if invalid_sentence_re.fullmatch(sentence):
                valid_sentences[-1] = ''.join([valid_sentences[-1] + sentence])
            else:
                valid_sentences.append(sentence)

        return valid_sentences


class Tca2SentenceDivider(object):
    """Make tca2 compatible input files.

    It spits out an xml document that has divided the text into sentences.
    Each sentence is encased in an s tag, and has an id number
    """

    @staticmethod
    def make_sentence_xml(lang, xmlfile):
        """Make sentence xml that tca2 can use.

        Arguments:
            lang (str): three character name of main language of document.
            filename (str): name of the xmlfile

        Returns:
            lxml.etree._Element: an xml element containing all sentences.
        """
        document = etree.Element('document')

        divider = SentenceDivider(lang)
        for index, sentence in enumerate(divider.make_valid_sentences(
                to_plain_text(lang, xmlfile))):
            s_elem = etree.Element("s")
            s_elem.attrib["id"] = str(index)
            s_elem.text = sentence
            document.append(s_elem)

        return document

    def make_sentence_file(self, lang, xmlfile, outfile):
        """Make input document for tca2.

        Arguments:
            lang (str): three character name for main language of document.
            xmlfile (str): name of the xmlfile
            outfile (str): name of the input file for tca2
        """
        o_path, _ = os.path.split(outfile)
        o_rel_path = o_path.replace(os.getcwd() + '/', '', 1)
        with util.ignored(OSError):
            os.makedirs(o_rel_path)
        with open(outfile, 'wb') as sentence_file:
            tree = etree.ElementTree(self.make_sentence_xml(lang, xmlfile))
            tree.write(sentence_file,
                       pretty_print=True,
                       encoding='utf8',
                       xml_declaration=True)


class Parallelize(object):
    """A class to parallelize two files.

    Input is the xml file that should be parallellized and the language that it
    should be parallellized with.
    The language of the input file is found in the metadata of the input file.
    The other file is found via the metadata in the input file
    """

    def __init__(self, origfile1, lang2, anchor_file=None, quiet=False):
        """Initialise the Parallelize class.

        Args:
            origfile1 (str): path the one of the files that should be
                sentence aligned.
            lang2 (str): language of the other file that should be
                sentence aligned.
            anchor_file (str): path to the anchor file. Defaults to None.
                A real file is only needed when using tca2 for sentence
                alignment.
            quiet (bool): If True, be verbose. Otherwise, be quiet.
        """
        self.quiet = quiet
        self.origfiles = []

        self.origfiles.append(corpusxmlfile.CorpusXMLFile(
            os.path.abspath(origfile1)))

        para_file = self.origfiles[0].get_parallel_filename(lang2)
        if para_file is not None:
            self.origfiles.append(corpusxmlfile.CorpusXMLFile(para_file))
        else:
            raise IOError("{} doesn't have a parallel file in {}".format(
                origfile1, lang2))

        self.consistency_check(self.origfiles[1], self.origfiles[0])

        # As stated in --help, we assume user-specified anchor file
        # has columns based on input files, where --parallel_file is
        # column two regardless of what file was translated from what,
        # therefore we set this before reshuffling:
        if self.is_translated_from_lang2():
            (self.origfiles[1], self.origfiles[0]) = (self.origfiles[0],
                                                      self.origfiles[1])

        self.gal = self.setup_anchors(anchor_file)

    def setup_anchors(self, path):
        """Setup anchor file.

        Args:
            path (str): where the anchor file will be written.
            cols (list of str): list of all the possible langs.

        Returns:
            generate_anchor_list.GenerateAnchorList
        """
        if path is None:
            path1 = os.path.join(
                os.environ['GTHOME'],
                'gt/common/src/anchor-{}-{}.txt'.format(self.lang1,
                                                        self.lang2))
            path2 = os.path.join(
                os.environ['GTHOME'],
                'gt/common/src/anchor-{}-{}.txt'.format(self.lang2,
                                                        self.lang1))
            if os.path.exists(path1):

                return generate_anchor_list.GenerateAnchorList(
                    self.lang1, self.lang2,
                    [self.lang1, self.lang2], path1)
            elif os.path.exists(path2):
                return generate_anchor_list.GenerateAnchorList(
                    self.lang1, self.lang2,
                    [self.lang2, self.lang1], path2)
            else:
                if not self.quiet:
                    util.note(
                        'No anchor file for the {}/{} combo. '
                        'Making a fake anchor file'.format(self.lang1,
                                                           self.lang2))

    @staticmethod
    def consistency_check(file0, file1):
        """Warn if parallel_text of f0 is not f1."""
        lang1 = file1.lang
        para0 = file0.get_parallel_basename(lang1)
        base1 = file1.basename_noext
        if para0 != base1:
            if para0 is None:
                util.note(
                    "WARNING: {} missing from {} parallel_texts in {}!".format(
                        base1, lang1, file0.name))
            else:
                util.note(
                    "WARNING: {}, not {}, in {} parallel_texts of {}!".format(
                        para0, base1, lang1, file0.name))

    @property
    def outfile_name(self):
        """Compute the name of the final tmx file."""
        orig_path_part = '/converted/{}/'.format(self.origfiles[0].lang)
        # First compute the part that shall replace /orig/ in the path
        replace_path_part = '/tmx/{}2{}/'.format(
            self.origfiles[0].lang,
            self.origfiles[1].lang)
        # Then set the outdir
        out_dirname = self.origfiles[0].dirname.replace(
            orig_path_part, replace_path_part)
        # Replace xml with tmx in the filename
        out_filename = self.origfiles[0].basename_noext + '.tmx'

        return os.path.join(out_dirname, out_filename)

    @property
    def lang1(self):
        """Get language 1."""
        return self.origfiles[0].lang

    @property
    def lang2(self):
        """Get language 2."""
        return self.origfiles[1].lang

    @property
    def origfile1(self):
        """Name of the original file 1."""
        return self.origfiles[0].name

    @property
    def origfile2(self):
        """Name of the original file 2."""
        return self.origfiles[1].name

    def is_translated_from_lang2(self):
        """Find out if the given doc is translated from lang2."""
        translated_from = self.origfiles[0].translated_from

        if translated_from is not None:
            return translated_from == self.lang2
        else:
            return False

    def parallelize_files(self):
        """Parallelize two files."""
        if not self.quiet:
            util.note("Aligning files …")
        return self.align()

    def run_command(self, command):
        """Run a parallelize command and return its output."""
        if not self.quiet:
            util.note("Running {}".format(" ".join(command)))
        subp = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            raise UserWarning(
                'Could not parallelize {} and {} into '
                'sentences\n{}\n\n{}\n'.format(
                    self.origfiles[0].basename, self.origfiles[1].basename,
                    output, error))

        return output, error

    def align(self):
        """Sentence align two corpus files."""
        raise NotImplementedError('You have to subclass and override align')


class ParallelizeHunalign(Parallelize):
    """Use hunalign to parallelise two converted corpus files."""

    split_anchors_on = re.compile(r' *, *')

    def anchor_to_dict(self, words_pairs):
        """Turn anchorfile tuples into a dictionary."""
        # turn [("foo, bar", "fie")] into [("foo", "fie"), ("bar", "fie")]:
        expanded_pairs = [(w1, w2)
                          for w1s, w2s in words_pairs
                          for w1 in re.split(self.split_anchors_on, w1s)
                          for w2 in re.split(self.split_anchors_on, w2s)
                          if w1 and w2]
        return expanded_pairs

    def make_dict(self):
        """Turn an anchorlist to a dictionary."""
        if self.gal is not None:
            assert self.gal.lang1 == self.lang1
            assert self.gal.lang2 == self.lang2
            words_pairs = self.gal.read_anchors(quiet=self.quiet)
            expanded_pairs = self.anchor_to_dict(words_pairs)
            cleaned_pairs = [(w1.replace('*', ''), w2.replace('*', ''))
                             for w1, w2 in expanded_pairs]
        else:
            cleaned_pairs = [(self.lang1, self.lang2)]
        # Hunalign expects the _reverse_ format for the dictionary!
        # See Dictionary under http://mokk.bme.hu/resources/hunalign/
        return "\n".join(["{} @ {}".format(w2, w1)
                          for w1, w2 in cleaned_pairs]) + "\n"

    @staticmethod
    def to_sents(origfile):
        """Divide the content of origfile to sentences."""
        divider = SentenceDivider(origfile.lang)
        return '\n'.join(divider.make_valid_sentences(
            to_plain_text(origfile.lang, origfile.name)))

    def align(self):
        """Parallelize two files using hunalign."""
        def tmp():
            """Temporary filename.

            Returns:
                str: name of the temporary file
            """
            return tempfile.NamedTemporaryFile('wb')
        with tmp() as dict_f, tmp() as sent0_f, tmp() as sent1_f:
            dict_f.write(self.make_dict().encode('utf8'))
            sent0_f.write(self.to_sents(
                self.origfiles[0]).encode('utf8'))
            sent1_f.write(self.to_sents(
                self.origfiles[1]).encode('utf8'))
            dict_f.flush()
            sent0_f.flush()
            sent1_f.flush()

            command = ['hunalign',
                       '-utf',
                       '-realign',
                       '-text',
                       dict_f.name,
                       sent0_f.name, sent1_f.name]
            output, _ = self.run_command(command)

        tmx = HunalignToTmx(self.origfiles, output.decode('utf-8'))
        return tmx


class ParallelizeTCA2(Parallelize):
    """Use tca2 to parallelise two converted corpus files."""

    def generate_anchor_file(self, outpath):
        """Generate an anchor file with lang1 and lang2."""
        if self.gal is not None:
            assert self.gal.lang1 == self.lang1
            assert self.gal.lang2 == self.lang2
            self.gal.generate_file(outpath, quiet=self.quiet)
        else:
            with open(outpath, 'w') as outfile:
                print('{} / {}'.format(self.lang1, self.lang2),
                      file=outfile)

    def divide_p_into_sentences(self):
        """Tokenize the text in the given file and reassemble it again."""
        for pfile in self.origfiles:
            divider = Tca2SentenceDivider()
            divider.make_sentence_file(pfile.lang, pfile.name,
                                       self.get_sent_filename(pfile))

    @property
    def sentfiles(self):
        """Get files containing the sentences."""
        return [self.get_sent_filename(name)
                for name in self.origfiles]

    def get_sent_filename(self, pfile):
        """Compute the name of the sentence file.

        Arguments:
            pfile (str): name of converted corpus file (produced by
                convert2xml)

        Returns:
            str: the name of the tca2 input file
        """
        origfilename = pfile.basename_noext
        # Ensure we have 20 bytes of leeway to let TCA2 append
        # lang_sent_new.txt without going over the 255 byte limit:
        origfilename = self.crop_to_bytes(origfilename, (255 - 20))
        return os.path.join(
            os.environ['GTFREE'], 'tmp',
            '{}{}_sent.xml'.format(origfilename, pfile.lang))

    @staticmethod
    def crop_to_bytes(name, max_bytes):
        """Ensure `name` is less than `max_bytes` bytes.

        Do not split name in the middle of a wide byte.
        """
        while len(name.encode('utf-8')) > max_bytes:
            name = name[:-1]
        return name

    def align(self):
        """Parallelize two files using tca2."""
        if not self.quiet:
            util.note("Adding sentence structure for the aligner …")
        self.divide_p_into_sentences()

        tca2_jar = os.path.join(HERE, 'tca2/dist/lib/alignment.jar')
        # util.sanity_check([tca2_jar])

        with tempfile.NamedTemporaryFile('w') as anchor_file:
            self.generate_anchor_file(anchor_file.name)
            anchor_file.flush()
            command = (
                'java -Xms512m -Xmx1024m -jar {} -cli-plain -anchor={} '
                '-in1={} -in2={}'.format(
                    tca2_jar,
                    anchor_file.name,
                    self.get_sent_filename(self.origfiles[0]),
                    self.get_sent_filename(self.origfiles[1])
                )
            )

            self.run_command(command.split())

        tmx = Tca2ToTmx(self.origfiles, self.sentfiles)
        return tmx


class Tmx(object):
    """A tmx file handler.

    A class that reads a tmx file, and implements a bare minimum of
    functionality to be able to compare two tmx's.
    It also contains functions to manipulate the tmx in several ways.
    """

    def __init__(self, tmx):
        """Input is a tmx element."""
        self.tmx = tmx

    @property
    def src_lang(self):
        """Get the srclang from the header element."""
        return self.tmx.find(".//header").attrib['srclang'][:3]

    @staticmethod
    def tu_to_string(transl_unit):
        """Extract the two strings of a tu element."""
        string = ""
        with util.ignored(AttributeError):
            string = string + transl_unit[0][0].text.strip()

        string += '\t'

        with util.ignored(AttributeError):
            string = string + transl_unit[1][0].text.strip()

        string += '\n'
        return string

    @staticmethod
    def tuv_to_string(tuv):
        """Extract the string from the tuv element."""
        string = ""
        with util.ignored(AttributeError):
            string = tuv[0].text.strip()

        return string

    def lang_to_stringlist(self, lang):
        """Find all sentences of lang."""
        all_tuv = self.tmx.\
            xpath('.//tuv[@xml:lang="' + lang + '"]',
                  namespaces={'xml': 'http://www.w3.org/XML/1998/namespace'})

        strings = []
        for tuv in all_tuv:
            strings.append(self.tuv_to_string(tuv))

        return strings

    def tmx_to_stringlist(self):
        """Extract all string pairs in a tmx to a list of strings."""
        all_tu = self.tmx.findall('.//tu')
        strings = []
        for transl_unit in all_tu:
            strings.append(self.tu_to_string(transl_unit))

        return strings

    @staticmethod
    def prettify_segs(transl_unit):
        """Strip white space from start and end of the strings.

        Input is a tu element
        Output is a tu element with white space stripped strings
        """
        with util.ignored(AttributeError):
            string = transl_unit[0][0].text.strip()
            transl_unit[0][0].text = string

        with util.ignored(AttributeError):
            string = transl_unit[1][0].text.strip()
            transl_unit[1][0].text = string

        return transl_unit

    # to debug here
    def reverse_langs(self):
        """Reverse the langs in a tmx.

        Return the reverted tmx
        """
        all_tu = self.tmx.findall('.//tu')
        body = etree.Element('body')
        for transl_unit in all_tu:
            tmp = etree.Element('tu')
            tmp.append(transl_unit[1])
            tmp.append(transl_unit[0])
            tmp = self.prettify_segs(tmp)
            body.append(tmp)

        tmx = etree.Element('tmx')
        tmx.append(body)

        self.tmx = tmx

    def remove_unwanted_space(self):
        """Remove unwanted spaces from sentences.

        The SentenceDivider adds spaces before and after punctuation,
        quotemarks, parentheses and so on.
        Remove those spaces so that the tmxes are more appropriate for real
        world™ use cases.
        """
        root = self.tmx
        for transl_unit in root.iter("tu"):
            transl_unit = self.remove_unwanted_space_from_segs(transl_unit)

    def remove_unwanted_space_from_segs(self, transl_unit):
        """Remove unwanted spaces.

        Remove spaces before and after punctuation,
        quotemarks, parentheses and so on as appropriate in the seg elements
        in the tu elements.
        Input is a tu element
        Output is a tu element with modified seg elements
        """
        with util.ignored(AttributeError):
            string = transl_unit[0][0].text.strip()
            string = self.remove_unwanted_space_from_string(string)
            transl_unit[0][0].text = string

        with util.ignored(AttributeError):
            string = transl_unit[1][0].text.strip()
            string = self.remove_unwanted_space_from_string(string)
            transl_unit[1][0].text = string

        return transl_unit

    @staticmethod
    def remove_unwanted_space_from_string(input_string):
        """Remove unwanted space from string.

        Args:
            input_string (str): the string we would like to remove
                unwanted space from:

        Returns:
            str without unwanted space.
        """
        result = input_string

        # regex to find space followed by punctuation
        space_punctuation = re.compile(
            r"(?P<space>\s)(?P<punctuation>[\)\]\.»:;,])")
        # for every match in the result string, replace the match
        # (space+punctuation) with the punctuation part
        result = space_punctuation.sub(lambda match: match.group(
            'punctuation'), result)

        # regex to find punctuation followed by space
        punctuation_space = re.compile(
            r"(?P<punctuation>[\[\(«])(?P<space>\s)+")
        result = punctuation_space.sub(lambda match: match.group(
            'punctuation'), result)

        # regex which matches multiple spaces
        multiple_space = re.compile(r"\s+")
        result = multiple_space.sub(lambda match: ' ', result)

        return result

    def write_tmx_file(self, out_filename):
        """Write a tmx file given a tmx etree element and a filename."""
        out_dir = os.path.dirname(out_filename)
        with util.ignored(OSError):
            os.makedirs(out_dir)

        with open(out_filename, "wb") as tmx_file:
            string = etree.tostring(self.tmx,
                                    pretty_print=True,
                                    encoding="utf-8",
                                    xml_declaration=True)
            tmx_file.write(string)

    def remove_tu_with_empty_seg(self):
        """Remove tu elements that contain empty seg element."""
        root = self.tmx
        for transl_unit in root.iter("tu"):
            try:
                self.check_if_emtpy_seg(transl_unit)
            except AttributeError:
                transl_unit.getparent().remove(transl_unit)

    @staticmethod
    def check_if_emtpy_seg(transl_units):
        """Check if a tu element contains empty strings.

        If there are any empty elements an AttributeError is raised
        """
        for transl_unit in transl_units:
            if not transl_unit[0].text.strip():
                raise AttributeError('Empty translation unit')

    def clean_toktmx(self):
        """Do the cleanup of the toktmx file."""
        self.remove_unwanted_space()
        self.remove_tu_with_empty_seg()


class AlignmentToTmx(Tmx):
    """A class to make tmx files based on the output of an aligner.

    This just implements some common methods for the TCA2 and hunalign
    subclasses.
    """

    def __init__(self, origfiles):
        """Input is a list of CorpusXMLFile objects."""
        self.origfiles = origfiles
        super(AlignmentToTmx, self).__init__(self.make_tmx())

    def make_tu(self, line1, line2):
        """Make a tmx tu element based on line1 and line2 as input."""
        transl_unit = etree.Element("tu")

        transl_unit.append(self.make_tuv(line1, self.origfiles[0].lang))
        transl_unit.append(self.make_tuv(line2, self.origfiles[1].lang))

        return transl_unit

    @staticmethod
    def make_tuv(line, lang):
        """Make a tuv element given an input line and a lang variable."""
        tuv = etree.Element("tuv")
        tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
        seg = etree.Element("seg")
        seg.text = line.strip()
        tuv.append(seg)

        return tuv

    @staticmethod
    def add_filename_id(filename):
        """Add the tmx filename as an prop element in the header."""
        prop = etree.Element('prop')
        prop.attrib['type'] = 'x-filename'
        prop.text = os.path.basename(filename)

        return prop

    def make_tmx_header(self, filename, lang):
        """Make a tmx header based on the lang variable."""
        header = etree.Element("header")

        # Set various attributes
        header.attrib["segtype"] = "sentence"
        header.attrib["o-tmf"] = "OmegaT TMX"
        header.attrib["adminlang"] = "en-US"
        header.attrib["srclang"] = lang
        header.attrib["datatype"] = "plaintext"

        header.append(self.add_filename_id(filename))

        return header

    def make_tmx(self):
        """Make tmx file based on the output of the aligner."""
        tmx = etree.Element("tmx")
        header = self.make_tmx_header(
            self.origfiles[0].basename,
            self.origfiles[0].lang)
        tmx.append(header)

        pfile1_data, pfile2_data = self.parse_alignment_results()

        body = etree.SubElement(tmx, "body")
        for line1, line2 in six.moves.zip(pfile1_data, pfile2_data):
            transl_unit = self.make_tu(line1, line2)
            body.append(transl_unit)

        return tmx

    def parse_alignment_results(self):
        """Meta function."""
        raise NotImplementedError(
            'You have to subclass and override parse_alignment_results')


class HunalignToTmx(AlignmentToTmx):
    """A class to make tmx files based on the output from hunalign."""

    def __init__(self, origfiles, output, threshold=0.0):
        """Input is a list of CorpusXMLFile objects."""
        self.output = output
        self.threshold = threshold
        super(HunalignToTmx, self).__init__(origfiles)

    def parse_alignment_results(self):
        """Return parsed output files of tca2."""
        pairs = [line.split("\t")
                 for line in self.output.split("\n")
                 if line]
        pairs = [pair for pair in pairs
                 if self.is_good_line(pair)]

        src_lines = [self.clean_line(l[0])
                     for l in pairs]
        trg_lines = [self.clean_line(l[1])
                     for l in pairs]
        return src_lines, trg_lines

    def is_good_line(self, line):
        """Determine whether this line should be used."""
        return (len(line) == 3 and
                line[0] != "<p>" and
                line[1] != "<p>" and
                float(line[2]) > self.threshold)

    @staticmethod
    def clean_line(line):
        """Remove the ~~~ occuring in multi-sentence alignments."""
        multi_sep = re.compile(r' *~~~ *')
        return multi_sep.sub(' ', line)


class Tca2ToTmx(AlignmentToTmx):
    """A class to make tmx files based on the output from tca2."""

    def __init__(self, origfiles, sentfiles):
        """Input is a list of CorpusXMLFile objects."""
        self.sentfiles = sentfiles
        super(Tca2ToTmx, self).__init__(origfiles)

    def parse_alignment_results(self):
        """Return parsed output files of tca2."""
        return (self.read_tca2_output(self.sentfiles[0]),
                self.read_tca2_output(self.sentfiles[1]))

    def read_tca2_output(self, sentfile):
        """Read the output of tca2.

        Arguments:
            sentfile (str): name of the output file of convert2xml

        Returns:
            list of str: The sentences found in the tca2 file
        """
        sentfile_name = sentfile.replace('.xml', '_new.txt')

        with codecs.open(sentfile_name, encoding='utf8') as tca2_output:
            return [self.remove_s_tag(line) for line in tca2_output]

    @staticmethod
    def remove_s_tag(line):
        """Remove the s tags that tca2 has added."""
        sregex = re.compile('<s id="[^ ]*">')
        line = line.replace('</s>', '')
        line = sregex.sub('', line)
        return line


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Sentence align file pairs.')

    parser.add_argument('sources',
                        nargs='+',
                        help='Files or directories to search for '
                        'parallelisable files')
    parser.add_argument('-s', '--stdout',
                        help='Whether output of the parallelisation '
                        'should be written to stdout or a files. '
                        'Defaults to '
                        'tmx/{lang1}2{lang2}/{GENRE}/.../{BASENAME}.tmx',
                        action="store_true")
    parser.add_argument('-f', '--force',
                        help="Overwrite output file if it already exists."
                        "The default is to skip parallelizing existing files.",
                        action="store_true")
    parser.add_argument('-q', '--quiet',
                        help="Don't mention anything out of the ordinary.",
                        action="store_true")
    parser.add_argument('-a', '--aligner',
                        choices=['hunalign', 'tca2'],
                        default='tca2',
                        help="Either hunalign or tca2 (the default).")
    parser.add_argument('-d', '--dict',
                        default=None,
                        help="Use a different bilingual seed dictionary. "
                        "Must have two columns, with input_file language "
                        "first, and --parallel_language second, separated "
                        "by `/'. By default, "
                        "$GTHOME/gt/common/src/anchor.txt is used, but this "
                        "file only supports pairings between "
                        "sme/sma/smj/fin/eng/nob. ")
    parser.add_argument('-l1', '--lang1',
                        help='The first language of a pair where '
                        'parallelisation should be done.',
                        required=True)
    parser.add_argument('-l2', '--lang2',
                        help='The second language of a pair where '
                        'parallelisation should be done.',
                        required=True)

    args = parser.parse_args()
    return args


def parallelise_file(input_file, lang2, dictionary, quiet, aligner, stdout,
                     force):
    """Align sentences of two parallel files."""
    try:
        if aligner == "hunalign":
            parallelizer = ParallelizeHunalign(origfile1=input_file,
                                               lang2=lang2,
                                               anchor_file=dictionary,
                                               quiet=quiet)
        elif aligner == "tca2":
            parallelizer = ParallelizeTCA2(origfile1=input_file,
                                           lang2=lang2,
                                           anchor_file=dictionary,
                                           quiet=quiet)
    except IOError as error:
        if not quiet:
            util.note(error.message)

    else:

        outfile = '/dev/stdout' if stdout else parallelizer.outfile_name

        if (outfile == "/dev/stdout" or not os.path.exists(outfile) or
                (os.path.exists(outfile) and force)):
            if not quiet:
                util.note("Aligning {} and its parallel file".format(
                    input_file))
            tmx = parallelizer.parallelize_files()
            tmx.clean_toktmx()
            if not quiet:
                util.note("Generating the tmx file {}".format(outfile))
            tmx.write_tmx_file(outfile)
            if not quiet:
                util.note("Wrote {}\n".format(outfile))
        else:
            util.note("{} already exists, skipping …".format(outfile))


def main():
    """Parallelise files."""
    args = parse_options()

    for source in args.sources:
        if os.path.isfile(source):
            parallelise_file(source, args.lang2,
                             args.dict, args.quiet, args.aligner,
                             args.stdout, args.force)
        elif os.path.isdir(source):
            for root, _, files in os.walk(source):
                for converted in files:
                    path = os.path.join(root, converted)
                    try:
                        parallelise_file(path, args.lang2, args.dict,
                                         args.quiet, args.aligner,
                                         args.stdout, args.force)
                    except UserWarning as error:
                        print(str(error))
