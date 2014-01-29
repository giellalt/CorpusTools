#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#   This file contains routines to sentence align two files
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
#   Copyright 2011-2014 Børre Gaup <borre.gaup@uit.no>
#

import os, errno
import re
import sys
import subprocess
import difflib
from lxml import etree
import datetime
import time
import argparse

import typosfile
import ngram

class CorpusXMLFile:
    """
    A class that contains the info on a file to be parallellized, name and language
    """

    def __init__(self, name, paralang):
        self.name = name
        self.paralang = paralang
        self.eTree = etree.parse(name)

    def geteTree(self):
        return self.eTree

    def getName(self):
        """
        Return the absolute path of the file
        """
        return self.name

    def getDirname(self):
        """
        Return the dirname of the file
        """
        return os.path.dirname(self.name)

    def getBasename(self):
        """
        Return the basename of the file
        """
        return os.path.basename(self.name)

    def getLang(self):
        """
        Get the lang of the file
        """
        return self.eTree.getroot().attrib['{http://www.w3.org/XML/1998/namespace}lang']

    def getWordCount(self):
        root = self.eTree.getroot()
        wordCount = root.find(".//wordcount")
        if wordCount is not None:
            return wordCount.text

    def getParallelBasename(self):
        """
        Get the basename of the parallel file
        Input is the lang of the parallel file
        """
        root = self.eTree.getroot()
        parallelFiles = root.findall(".//parallel_text")
        for p in parallelFiles:
            if p.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == self.paralang:
                return p.attrib['location']

    def getParallelFilename(self):
        """
        Infer the absolute path of the parallel file
        """
        parallelDirname = self.getDirname().replace(self.getLang(), self.paralang)
        if self.getParallelBasename() is not None:
            parallelBasename = self.getParallelBasename() + '.xml'

            return os.path.join(parallelDirname, parallelBasename)

    def getOriginalFilename(self):
        """
        Infer the path of the original file
        """
        return self.getName().replace('prestable/', '').replace('converted/', 'orig/').replace('.xml', '')

    def getTranslatedFrom(self):
        """
        Get the translated_from element from the orig doc
        """
        root = self.eTree.getroot()
        translatedFrom = root.find(".//translated_from")

        if translatedFrom is not None:
            return translatedFrom.attrib['{http://www.w3.org/XML/1998/namespace}lang']

    def removeVersion(self):
        """
        Remove the version element
        This is often the only difference between the otherwise
        identical files in converted and prestable/converted
        """
        root = self.eTree.getroot()
        versionElement = root.find(".//version")
        versionElement.getparent().remove(versionElement)

    def removeSkip(self):
        """
        Remove the skip element
        This contains text that is not wanted in e.g. sentence alignment
        """
        root = self.eTree.getroot()
        skipList = root.findall(".//skip")

        for skipElement in skipList:
            skipElement.getparent().remove(skipElement)

    def moveLater(self):
        """
        Move the later elements to the end of the body element.
        """
        root = self.eTree.getroot()
        body = root.xpath("/document/body")[0]

        laterList = root.xpath(".//later")

        for laterElement in laterList:
            body.append(laterElement)

class SentenceDivider:
    """A class that takes a giellatekno xml document as input.
    It spits out an xml document that has divided the text inside the p tags
    into sentences, but otherwise is unchanged.
    Each sentence is encased in an s tag, and has an id number
    """
    def __init__(self, inputXmlfile, parallelLang):
        """Parse the inputXmlfile, set docLang to lang and read typos from the
        corresponding .typos file if it exists
        """
        self.setUpInputFile(inputXmlfile, parallelLang)
        self.sentenceCounter = 0
        self.typos = {}

        typosname = inputXmlfile.replace('.xml', '.typos')
        if os.path.isfile(typosname):
            t = typosfile.Typos(inputXmlfile.replace('.xml', '.typos'))
            self.typos.update(t.getTypos())

    def setUpInputFile(self, inputXmlfile, parallelLang):
        """
        Initialize the inputfile, skip those parts that are meant to be
        skipped, move <later> elements.
        """
        inFile = CorpusXMLFile(inputXmlfile, parallelLang)
        self.docLang = inFile.getLang()

        inFile.moveLater()
        inFile.removeSkip()
        self.inputEtree = inFile.geteTree()

    def processAllParagraphs(self):
        """Go through all paragraphs in the etree and process them one by one.
        """
        self.document = etree.Element('document')
        body = etree.Element('body')
        self.document.append(body)

        for paragraph in self.inputEtree.findall('//p'):
            body.append(self.processOneParagraph(paragraph))

    def writeResult(self, outfile):
        """Write self.document to the given outfile name
        """
        oPath, oFile = os.path.split(outfile)
        oRelPath = oPath.replace(os.getcwd()+'/', '', 1)
        try:
            os.makedirs(oRelPath)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        f = open(outfile, 'w')
        et = etree.ElementTree(self.document)
        et.write(f, pretty_print = True, encoding = "utf-8", xml_declaration = True)
        f.close()

    def getPreprocessOutput(self, preprocessInput):
        """Send the text in preprocessInput into preprocess, return the result.
        If the process fails, exit the program
        """
        preprocessCommand = []
        if (self.docLang == 'nob'):
            abbrFile = os.path.join(os.environ['GTHOME'], 'st/nob/bin/abbr.txt')
            preprocessCommand = ['preprocess', '--abbr=' + abbrFile]
        else:
            abbrFile = os.path.join(os.environ['GTHOME'], 'gt/sme/bin/abbr.txt')
            corrFile = os.path.join(os.environ['GTHOME'], 'gt/sme/bin/corr.txt')
            preprocessCommand = ['preprocess', '--abbr=' + abbrFile, '--corr=' + corrFile]

        subp = subprocess.Popen(preprocessCommand, stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, error) = subp.communicate(preprocessInput.encode('utf-8').replace('\n', ' '))

        if subp.returncode != 0:
            print >>sys.stderr, 'Could not divide into sentences'
            print >>sys.stderr, output
            print >>sys.stderr, error
            sys.exit()
        else:
            return output

    def processOneParagraph(self, origParagraph):
        """Run the content of the origParagraph through preprocess, make sentences
        Return a new paragraph containing the marked up sentences
        """
        newParagraph = etree.Element("p")

        allText = origParagraph.xpath('.//text()')
        preprocessInput = "".join(allText)

        # Check if there is any text from preprocess
        if (preprocessInput):
            output = self.getPreprocessOutput(preprocessInput)
            sentence = []
            insideQuote = False
            incompleteSentences = ['.', '?', '!', ')', ']', '...', '…','"', '»', '”', '°', '', ':']
            words = output.split('\n')
            i = 0
            while i < len(words):
                word = words[i].strip()

                # If word exists in typos, replace it with the correction
                if word in self.typos:
                    word = self.typos[word]

                sentence.append(word.decode('utf-8'))
                if (word == '.' or word == '?' or word == '!'):
                    while i + 1 < len(words) and words[i + 1].strip() in incompleteSentences:
                        if words[i + 1] != '':
                            sentence.append(words[i + 1].decode('utf-8').strip())
                        i = i + 1

                    # exclude pseudo-sentences, i.e. sentences that don't contain any alphanumeric characters
                    if not re.compile(r"^[\W|\s]*$").match(' '.join(sentence)):
                        newParagraph.append(self.makeSentence(sentence))
                    sentence = []

                i = i + 1

            # exclude pseudo-sentences, i.e. sentences that don't contain any alphanumeric characters
            if len(sentence) > 1 and not re.compile(r"^[\W|\s]*$").match(' '.join(sentence)):
                newParagraph.append(self.makeSentence(sentence))

        return newParagraph

    def makeSentence(self, sentence):
        """Make an s element, set the id and set the text to be the content of
        the list sentence
        """

        # make regex for two or more space characters
        spaces = re.compile(' +')

        s = etree.Element("s")
        s.attrib["id"] = str(self.sentenceCounter)

        # substitute two or more spaces with one space
        s.text = spaces.sub(' ', ' '.join(sentence)).strip()

        self.sentenceCounter += 1

        return s

class Parallelize:
    """
    A class to parallelize two files
    Input is the xml file that should be parallellized and the language that it
    should be parallellized with.
    The language of the input file is found in the metadata of the input file.
    The other file is found via the metadata in the input file
    """

    def __init__(self, origfile1, lang2):
        """
        Set the original file name, the lang of the original file and the
        language that it should parallellized with.
        Parse the original file to get the access to metadata
        """
        self.origfiles = []

        tmpfile = CorpusXMLFile(os.path.abspath(origfile1), lang2)
        self.origfiles.append(tmpfile)

        if self.origfiles[0].getParallelFilename() is not None:
            tmpfile = CorpusXMLFile(self.origfiles[0].getParallelFilename(), self.origfiles[0].getLang())
            self.origfiles.append(tmpfile)
        else:
            raise IOError(origfile1 + " doesn't have a parallel file in " + lang2)

        if self.isTranslatedFromLang2():
            self.reshuffleFiles()

    def reshuffleFiles(self):
        """
        Change the order of the files (so that the translated text is last)
        """
        tmp = self.origfiles[0]
        self.origfiles[0] = self.origfiles[1]
        self.origfiles[1] = tmp

    def getFilelist(self):
        """
        Return the list of (the two) files that are aligned
        """
        return self.origfiles

    def getLang1(self):
        return self.origfiles[0].getLang()

    def getLang2(self):
        return self.origfiles[1].getLang()

    def getOrigfile1(self):
        return self.origfiles[0].getName()

    def getOrigfile2(self):
        return self.origfiles[1].getName()

    def isTranslatedFromLang2(self):
        """
        Find out if the given doc is translated from lang2
        """
        result = False
        origfile1Tree = etree.parse(self.getOrigfile1())
        root = origfile1Tree.getroot()
        translated_from = root.find(".//translated_from")
        if translated_from is not None:
            if translated_from.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == self.getLang2():
                result = True

        return result

    def generateAnchorFile(self):
        """
        Generate an anchor file with lang1 and lang2. Return the path to the anchor file
        """
        infile1 = os.path.join(os.environ['GTHOME'], 'gt/common/src/anchor.txt')
        infile2 = os.path.join(os.environ['GTHOME'], 'gt/common/src/anchor-admin.txt')

        subp = subprocess.Popen(['generate-anchor-list.pl', '--lang1=' + self.getLang1(), '--lang2' + self.getLang2(), '--outdir=' + os.environ['GTFREE'], infile1, infile2], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Could not generate ', pfile.getName(), ' into sentences'
            print >>sys.stderr, output
            print >>sys.stderr, error
            return subp.returncode

        # Return the absolute path of the resulting file
        outFilename = 'anchor-' + self.getLang1() + self.getLang2() + '.txt'
        return os.path.join(os.environ['GTFREE'], outFilename)

    def dividePIntoSentences(self):
        """
        Tokenize the text in the given file and reassemble it again
        """
        for pfile in self.origfiles:
            infile = os.path.join(pfile.getName())
            if os.path.exists(infile):
                outfile = self.getSentFilename(pfile)
                divider = SentenceDivider(infile, pfile.getLang())
                divider.processAllParagraphs()
                divider.writeResult(outfile)
            else:
                print >>sys.stderr, infile, "doesn't exist"
                return 2

        return 0

    def getSentFilename(self, pfile):
        """
        Compute a name for the corpus-analyze output and tca2 input file
        Input is a CorpusXMLFile
        """
        origfilename = pfile.getBasename().replace('.xml', '')
        return os.environ['GTFREE'] + '/tmp/' + origfilename + pfile.getLang() + '_sent.xml'

    def parallelizeFiles(self):
        """
        Parallelize two files using tca2
        """
        anchorName = self.generateAnchorFile()

        subp = subprocess.Popen(['tca2.sh', anchorName, self.getSentFilename(self.getFilelist()[0]), self.getSentFilename(self.getFilelist()[1])], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Could not parallelize', self.getSentFilename(self.getFilelist()[0]), 'and', self.getSentFilename(self.getFilelist()[1]), ' into sentences'
            print >>sys.stderr, output
            print >>sys.stderr, error

        return subp.returncode

class Tmx:
    """
    A class that reads a tmx file, and implements a bare minimum of functionality
    to be able to compare two tmx'es.
    It also contains functions to manipulate the tmx in several ways.
    """

    def __init__(self, tmx):
        """Input is a tmx element
        """
        self.tmx = tmx

        gthome = os.getenv('GTHOME')
        self.language_guesser = ngram.NGram(gthome + '/tools/lang-guesser/LM/')

    def getSrcLang(self):
        """
        Get the srclang from the header element
        """
        return self.tmx.find(".//header").attrib['srclang'][:3]

    def getTmx(self):
        """
        Get the tmx xml element
        """
        return self.tmx

    def tuToString(self, tu):
        """
        Extract the two strings of a tu element
        """
        string = ""
        try:
            string = string + tu[0][0].text.strip()
        except(AttributeError):
            pass

        string += '\t'

        try:
            string = string + tu[1][0].text.strip()
        except(AttributeError):
            pass

        string += '\n'
        return string.encode('utf-8')

    def tuvToString(self, tuv):
        """
        Extract the string from the tuv element
        """
        string = ""
        try:
            string = tuv[0].text.strip()
        except(AttributeError):
            pass

        return string.encode('utf-8')

    def langToStringlist(self, lang):
        """
        Get all the strings in the tmx in language lang, insert them
        into the list strings
        """
        all_tuv = self.getTmx().xpath('.//tuv[@xml:lang="' + lang + '"]',
            namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})

        strings = []
        for tuv in all_tuv:
            strings.append(self.tuvToString(tuv))

        return strings

    def tmxToStringlist(self):
        """
        Extract all string pairs in a tmx to a list of strings
        """
        all_tu = self.getTmx().findall('.//tu')
        strings = []
        for tu in all_tu:
            strings.append(self.tuToString(tu))

        return strings

    def prettifySegs(self, tu):
        """Strip white space from start and end of the strings in the
        seg elements
        Input is a tu element
        Output is a tu element with white space stripped strings
        """
        try:
            string = tu[0][0].text.strip()
            tu[0][0].text = string
        except(AttributeError):
            pass

        try:
            string = tu[1][0].text.strip()
            tu[1][0].text = string
        except(AttributeError):
            pass

        return tu

    # to debug here
    def reverseLangs(self):
        """
        Reverse the langs in a tmx
        Return the reverted tmx
        """
        all_tu = self.getTmx().findall('.//tu')
        body = etree.Element('body')
        for tu in all_tu:
            tmp = etree.Element('tu')
            tmp.append(tu[1])
            tmp.append(tu[0])
            tmp = self.prettifySegs(tmp)
            body.append(tmp)

        tmx = etree.Element('tmx')
        tmx.append(body)

        self.tmx = tmx

    def removeUnwantedSpace(self):
        """The SentenceDivider adds spaces before and after punctuation,
        quotemarks, parentheses and so on.
        Remove those spaces so that the tmxes are more appropriate for real
        world™ use cases.
        """

        root = self.getTmx().getroot()
        for tu in root.iter("tu"):
            tu = self.removeUnwantedSpaceFromSegs(tu)

    def removeUnwantedSpaceFromSegs(self, tu):
        """Remove spaces before and after punctuation,
        quotemarks, parentheses and so on as appropriate in the seg elements
        in the tu elements.
        Input is a tu element
        Output is a tu element with modified seg elements
        """
        try:
            string = tu[0][0].text.strip()
            string = self.removeUnwantedSpaceFromString(string)
            tu[0][0].text = string
        except AttributeError:
            pass

        try:
            string = tu[1][0].text.strip()
            string = self.removeUnwantedSpaceFromString(string)
            tu[1][0].text = string
        except AttributeError:
            pass

        return tu

    def removeUnwantedSpaceFromString(self, inputString):
        """Remove spaces before and after punctuation,
        quotemarks, parentheses and so on as appropriate
        """
        result = inputString

        # regex to find space followed by punctuation
        spacePunctuation = re.compile("(?P<space>\s)(?P<punctuation>[\)\]\.»:;,])")
        # for every match in the result string, replace the match
        # (space+punctuation) with the punctuation part
        result = spacePunctuation.sub(lambda match: match.group('punctuation'), result)

        # regex to find punctuation followed by space
        punctuationSpace = re.compile("(?P<punctuation>[\[\(«])(?P<space>\s)+")
        result = punctuationSpace.sub(lambda match: match.group('punctuation'), result)

        # regex which matches multiple spaces
        multipleSpace = re.compile("\s+")
        result = multipleSpace.sub(lambda match: ' ', result)

        return result

    def writeTmxFile(self, outFilename):
        """
        Write a tmx file given a tmx etree element and a filename
        """
        try:
            f = open(outFilename, "w")

            string = etree.tostring(self.getTmx(), pretty_print = True, encoding = "utf-8", xml_declaration = True)
            f.write(string)
            f.close()
        except IOError, error:
            print "I/O error({0}): {1}".format(errno, strerror), ":", outFilename
            sys.exit(1)

    def removeTuWithEmptySeg(self):
        """Remove tu elements that contain empty seg element
        """
        root = self.getTmx().getroot()
        for tu in root.iter("tu"):
            try:
                self.checkIfEmtpySeg(tu)
            except AttributeError:
                tu.getparent().remove(tu)

    def checkIfEmtpySeg(self, tu):
        """Check if a tu element contains empty strings
        If there are any empty elements an AttributeError is raised
        """
        string = tu[0][0].text.strip()
        string = tu[1][0].text.strip()

    # Commented out this code because language detection doesn't work well enough
    #def removeTuWithWrongLang(self, lang):
        #"""Remove tu elements that have the wrong lang according to the
        #language guesser
        #"""
        #root = self.getTmx().getroot()
        #for tu in root.iter("tu"):
            #if self.checkLanguage(tu, lang) == False:
                #tu.getparent().remove(tu)

    def checkLanguage(self, tu, lang):
        """Get the text of the tuv element with the given lang
        Run the text through the language guesser, return the result
        of this test
        """
        for tuv in tu:
            if tuv.get('{http://www.w3.org/XML/1998/namespace}lang') == lang:
                text = tuv[0].text.encode("ascii", "ignore")
                test_lang = self.language_guesser.classify(text)
                if test_lang != lang:
                    # Remove the comment below for debugging purposes
                    # print "This text is not", lang, "but", test_lang, tuv[0].text
                    return False

        return True

class Tca2ToTmx(Tmx):
    """
    A class to make tmx files based on the output from tca2
    """
    def __init__(self, filelist):
        """
        Input is a list of CorpusXMLFile objects
        """
        self.filelist = filelist
        Tmx.__init__(self, self.setTmx())

    def makeTu(self, line1, line2):
        """
        Make a tmx tu element based on line1 and line2 as input
        """
        tu = etree.Element("tu")

        tu.append(self.makeTuv(line1, self.filelist[0].getLang()))
        tu.append(self.makeTuv(line2, self.filelist[1].getLang()))

        return tu

    def makeTuv(self, line, lang):
        """
        Make a tuv element given an input line and a lang variable
        """
        tuv = etree.Element("tuv")
        tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
        seg = etree.Element("seg")
        seg.text = self.removeSTag(line).strip().decode("utf-8")
        tuv.append(seg)

        return tuv

    def makeTmxHeader(self, lang):
        """
        Make a tmx header based on the lang variable
        """
        header = etree.Element("header")

        # Set various attributes
        header.attrib["segtype"] = "sentence"
        header.attrib["o-tmf"] = "OmegaT TMX"
        header.attrib["adminlang"] = "en-US"
        header.attrib["srclang"] = lang
        header.attrib["datatype"] = "plaintext"

        return header

    def removeSTag(self, line):
        """
        Remove the s tags that tca2 has added
        """
        line = line.replace('</s>','')
        sregex = re.compile('<s id="[^ ]*">')
        line = sregex.sub('', line)

        return line

    def getOutfileName(self):
        """
        Compute the name of the tmx file
        """

        origPathPart = '/converted/' + self.filelist[0].getLang() + '/'
        # First compute the part that shall replace /orig/ in the path
        replacePathPart = '/toktmx/' + self.filelist[0].getLang() + '2' + self.filelist[1].getLang() + '/'
        # Then set the outdir
        outDirname = self.filelist[0].getDirname().replace(origPathPart, replacePathPart)
        # Replace xml with tmx in the filename
        outFilename = self.filelist[0].getBasename().replace('.xml', '.toktmx')

        return os.path.join(outDirname, outFilename)

    def setTmx(self):
        """
        Make tmx file based on the two output files of tca2
        """
        tmx = etree.Element("tmx")
        header = self.makeTmxHeader(self.filelist[0].getLang())
        tmx.append(header)

        pfile1_data = self.readTca2Output(self.filelist[0])
        pfile2_data = self.readTca2Output(self.filelist[1])

        body = etree.SubElement(tmx, "body")
        for line1, line2 in map(None, pfile1_data, pfile2_data):
            tu = self.makeTu(line1, line2)
            body.append(tu)

        return tmx

    def readTca2Output(self, pfile):
        """
        Read the output of tca2
        Input is a CorpusXMLFile
        """
        text = ""
        pfileName = self.getSentFilename(pfile).replace('.xml', '_new.txt')
        try:
            f = open(pfileName, "r")
            text = f.readlines()
            f.close()
        except IOError, error:
            print "I/O error({0}): {1}".format(errno, strerror)
            sys.exit(1)

        return text


    def getSentFilename(self, pfile):
        """
        Compute a name for the corpus-analyze output and tca2 input file
        Input is a CorpusXMLFile
        """
        origfilename = pfile.getBasename().replace('.xml', '')
        return os.environ['GTFREE'] + '/tmp/' + origfilename + pfile.getLang() + '_sent.xml'

class TmxComparator:
    """
    A class to compare two tmx-files
    """
    def __init__(self, wantTmx, gotTmx):
        self.wantTmx = wantTmx
        self.gotTmx = gotTmx


    def getLinesInWantedfile(self):
        """
        Return the number of lines in the reference doc
        """
        return len(self.wantTmx.tmxToStringlist())


    def getNumberOfDifferingLines(self):
        """
        Given a unified_diff, find out how many lines in the reference doc
        differs from the doc to be tested. A return value of -1 means that
        the docs are equal
        """
        # Start at -1 because a unified diff always starts with a --- line
        numDiffLines = -1
        for line in difflib.unified_diff(self.wantTmx.tmxToStringlist(), self.gotTmx.tmxToStringlist(), n = 0):
            if line[:1] == '-':
                numDiffLines += 1

        return numDiffLines

    def getDiffAsText(self):
        """
        Return a stringlist containing the diff lines
        """
        diff = []
        for line in difflib.unified_diff(self.wantTmx.tmxToStringlist(), self.gotTmx.tmxToStringlist(), n = 0):
            diff.append(line)

        return diff

    def getLangDiffAsText(self, lang):
        """
        Return a stringlist containing the diff lines
        """
        diff = []
        for line in difflib.unified_diff(self.wantTmx.langToStringlist(lang), self.gotTmx.langToStringlist(lang), n = 0):
            diff.append(line + '\n')

        return diff

class TmxTestDataWriter():
    """
    A class that writes tmx test data to a file
    """
    def __init__(self, filename):
        self.filename = filename

        try:
            tree = etree.parse(filename)
            self.setParagsTestingElement(tree.getroot())
        except IOError, error:
            print "I/O error({0}): {1}".format(error.errno, error.strerror)
            sys.exit(1)

    def getFilename(self):
        return self.filename

    def makeFileElement(self, name, gspairs, diffpairs):
        """
        Make the element file, set the attributes
        """
        fileElement = etree.Element("file")
        fileElement.attrib["name"] = name
        fileElement.attrib["gspairs"] = gspairs
        fileElement.attrib["diffpairs"] = diffpairs

        return fileElement

    def setParagsTestingElement(self, paragstesting):
        self.paragstesting = paragstesting

    def makeTestrunElement(self, datetime):
        """
        Make the testrun element, set the attribute
        """
        testrunElement = etree.Element("testrun")
        testrunElement.attrib["datetime"] = datetime

        return testrunElement

    def makeParagstestingElement(self):
        """
        Make the paragstesting element
        """
        paragstestingElement = etree.Element("paragstesting")

        return paragstestingElement

    def insertTestrunElement(self, testrun):
        self.paragstesting.insert(0, testrun)

    def writeParagstestingData(self):
        """
        Write the paragstesting data to a file
        """
        try:
            f = open(self.filename, "w")

            et = etree.ElementTree(self.paragstesting)
            et.write(f, pretty_print = True, encoding = "utf-8", xml_declaration = True)
            f.close()
        except IOError, error:
            print "I/O error({0}): {1}".format(errno, strerror)
            sys.exit(1)

class TmxGoldstandardTester:
    """
    A class to test the alignment pipeline against the tmx goldstandard
    """
    def __init__(self, testresult_filename, dateformat_addition = None):
        """
        Set the name where the testresults should be written
        Find all goldstandard tmx files
        """
        self.numberOfDiffLines = 0
        self.testresultWriter = TmxTestDataWriter(testresult_filename)
        if dateformat_addition is None:
            self.date = self.dateformat()
        else:
            self.date = self.dateformat() + dateformat_addition

    def setNumberOfDiffLines(self, diffLines):
        """
        Increase the total number of difflines in this test run
        """
        self.numberOfDiffLines += diffLines

    def getNumberOfDiffLines(self):
        return self.numberOfDiffLines

    def dateformat(self):
        """
        Get the date and time, 20111209-1234. Used in a testrun element
        """
        d = datetime.datetime.fromtimestamp(time.time())

        return d.strftime("%Y%m%d-%H%M")

    def runTest(self):
        # Make a testrun element, which will contain the result of the test
        testrun = self.testresultWriter.makeTestrunElement(self.date)

        paralang = ""
        # Go through each tmx goldstandard file
        for wantTmxFile in self.findGoldstandardTmxFiles():
            print "testing", wantTmxFile, "..."

            # Calculate the parallel lang, to be used in parallelization
            if wantTmxFile.find('nob2sme') > -1:
                paralang = 'sme'
            else:
                paralang = 'nob'

            # Align files
            self.alignFiles(testrun, wantTmxFile, paralang)

        # All files have been tested, insert this run at the top of the paragstest element
        self.testresultWriter.insertTestrunElement(testrun)
        # Write data to file
        self.testresultWriter.writeParagstestingData()

    def alignFiles(self, testrun, wantTmxFile, paralang):
        """
        Align files
        Compare the tmx's of the result of this parallellization and the tmx of the goldstandard file
        Write the result to a file
        Write the diffs of these to tmx's to a separate file
        """

        # Compute the name of the main file to parallelize
        xmlFile = self.computeXmlfilename(wantTmxFile)

        parallelizer = Parallelize(xmlFile, paralang)
        if parallelizer.dividePIntoSentences() == 0:
            if parallelizer.parallelizeFiles() == 0:

                # The result of the alignment is a tmx element
                filelist = parallelizer.getFilelist()
                gotTmx = Tca2ToTmx(filelist)

                # This is the tmx element fetched from the goldstandard file
                wantTmx = Tmx(etree.parse(wantTmxFile))

                # Instantiate a comparator with the two tmxes
                comparator = TmxComparator(wantTmx, gotTmx)

                # Make a fileElement for our results file
                fileElement = self.testresultWriter.makeFileElement(filelist[0].getBasename(), str(comparator.getLinesInWantedfile()), str(comparator.getNumberOfDifferingLines()))

                self.setNumberOfDiffLines(comparator.getNumberOfDifferingLines())

                # Append the result for this file to the testrun element
                testrun.append(fileElement)

                self.writeDiffFiles(comparator, parallelizer, filelist[0].getBasename())

    def computeXmlfilename(self, wantTmxFile):
        """
        Compute the name of the xmlfile which should be aligned
        """
        xmlFile = wantTmxFile.replace('tmx/goldstandard/', 'converted/')
        xmlFile = xmlFile.replace('nob2sme', 'nob')
        xmlFile = xmlFile.replace('sme2nob', 'sme')
        xmlFile = xmlFile.replace('.toktmx', '.xml')

        return xmlFile

    def writeDiffFiles(self, comparator, parallelizer, filename):
        """
        Write diffs to a jspwiki file
        """
        print "writeDiffFiles", filename
        filename = filename + '_' + self.date + '.jspwiki'
        dirname = os.path.join(os.path.dirname(self.testresultWriter.getFilename()), 'tca2testing')

        try:
            f = open(os.path.join(dirname, filename), "w")
        except IOError, error:
            print "I/O error({0}): {1}".format(errno, strerror)
            sys.exit(1)

        f.write('!!!' + filename + '\n')
        f.write("!!TMX diff\n{{{\n")
        f.writelines(comparator.getDiffAsText())
        f.write("\n}}}\n!!" + parallelizer.getLang1() + " diff\n{{{\n")
        f.writelines(comparator.getLangDiffAsText(parallelizer.getLang1()))
        f.write("\n}}}\n!!" + parallelizer.getLang2() + " diff\n{{{\n")
        f.writelines(comparator.getLangDiffAsText(parallelizer.getLang2()))
        f.write("\n}}}\n")
        f.close()

    def findGoldstandardTmxFiles(self):
        """
        Find the goldstandard tmx files, return them as a list
        """
        subp = subprocess.Popen(['find', os.path.join(os.environ['GTFREE'], 'prestable/toktmx/goldstandard'), '-name', '*.toktmx', '-print' ], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Error when searching for goldstandard docs'
            print >>sys.stderr, error
            sys.exit(1)
        else:
            files = output.split('\n')
            return files[:-1]

class TmxFixer:
    """
    A class to reverse the langs and change the name of a tmx file if needed
    Possible errors of a tmx file:
    * the languages can be in the wrong order
    * the name is wrong
    * the file is placed in the wrong lang directory
    """

    def __init__(self, filetofix):
        """
        Input is the tmx file we should consider to fix
        """
        pass

class Toktmx2Tmx:
    """A class to make a tidied up version of toktmx files.
    Removes unwanted spaces around punctuation, parentheses and so on.
    """
    def readToktmxFile(self, toktmxFile):
        """Reads a toktmx file, parses it, sets the tmx file name
        """
        self.tmxfileName = toktmxFile.replace('toktmx', 'tmx')
        self.tmx = Tmx(etree.parse(toktmxFile))
        self.addFilenameID()


    def addFilenameID(self):
        """Add the tmx filename as an prop element in the header
        """
        prop =  etree.Element('prop')
        prop.attrib['type'] = 'x-filename'
        prop.text = os.path.basename(self.tmxfileName).decode('utf-8')

        root = self.tmx.getTmx().getroot()

        for header in root.iter('header'):
            header.append(prop)

    def writeCleanedupTmx(self):
        """Write the cleanup tmx
        """
        print ".",
        self.tmx.writeTmxFile(self.tmxfileName)

    def cleanToktmx(self):
        """Do the cleanup of the toktmx file
        """
        self.tmx.removeUnwantedSpace()
        self.tmx.removeTuWithEmptySeg()

    def findToktmxFiles(self, dirname):
        """
        Find the toktmx files in dirname, return them as a list
        """
        subp = subprocess.Popen(['find', os.path.join(os.environ['GTFREE'], 'prestable/toktmx/' + dirname), '-name', '*.toktmx', '-print' ], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Error when searching for toktmx docs'
            print >>sys.stderr, error
            sys.exit(1)
        else:
            files = output.split('\n')
            return files[:-1]


def parse_options():
    parser = argparse.ArgumentParser(description = 'Sentence align two files. Input is the document containing the main language, and language to parallelize it with.')
    parser.add_argument('input_file', help = "The input file")
    parser.add_argument('-p', '--parallel_language', dest = 'parallel_language', help = "The language to parallelize the input document with", required = True)

    args = parser.parse_args()
    return args


def main():
    args = parse_options()

    try:
        parallelizer = Parallelize(args.input_file, args.parallel_language)
    except IOError as e:
        print e.message
        sys.exit(1)

    print "Aligning", args.input_file, "and its parallel file"
    print "Adding sentence structure that tca2 needs ..."
    if parallelizer.dividePIntoSentences() == 0:
        print "Aligning files ..."
        if parallelizer.parallelizeFiles() == 0:
            tmx = Tca2ToTmx(parallelizer.getFilelist())

            oPath, oFile = os.path.split(tmx.getOutfileName())
            oRelPath = oPath.replace(os.getcwd()+'/', '', 1)
            try:
                os.makedirs(oRelPath)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            print "Generating the tmx file", tmx.getOutfileName()
            tmx.writeTmxFile(tmx.getOutfileName())
