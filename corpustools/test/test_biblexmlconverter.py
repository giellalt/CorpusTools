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
#   Copyright © 2014-2018 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test the BiblexmlConverter class."""

from __future__ import absolute_import

import doctest
import os

import lxml.doctestcompare
import lxml.etree
import six
from testfixtures import TempDirectory

from corpustools import biblexmlconverter

TESTS = {
    'book_chapter_section_verse': {
        'orig': (u'<document>'
                 u'  <head/>'
                 u'  <body>'
                 u'    <book title="Book title">'
                 u'      <chapter title="Kapittel 1">'
                 u'        <section title="Section 1">'
                 u'          <verse number="1">Vearsa 1 </verse>'
                 u'          <verse number="2">Vearsa 2 </verse>'
                 u'        </section>'
                 u'      </chapter>'
                 u'    </book>'
                 u'  </body>'
                 u'</document>'),
        'converted': ('<document>'
                      '  <body>'
                      '    <section>'
                      '      <p type="title">Book title</p>'
                      '      <section>'
                      '        <p type="title">Kapittel 1</p>'
                      '        <section>'
                      '          <p type="title">Section 1</p>'
                      '          <p>Vearsa 1 Vearsa 2 </p>'
                      '        </section>'
                      '      </section>'
                      '    </section>'
                      '  </body>'
                      '</document>'),
    },
    'book_chapter_verse': {
        'orig': (u'<document>'
                 u'  <header>'
                 u'    <title>1</title>'
                 u'  </header>'
                 u'  <body>'
                 u'    <book title="1 Sálmmaid girji ">'
                 u'      <chapter number="1">'
                 u'        <verse number="1">Vearsa1, </verse>'
                 u'        <verse number="2">vearsa2. </verse>'
                 u'      </chapter>'
                 u'    </book>'
                 u'  </body>'
                 u'</document>'),
        'converted': ('<document>'
                      '  <body>'
                      '    <section>'
                      '      <p type="title">1 Sálmmaid girji</p>'
                      '      <section>'
                      '        <p type="title">1</p>'
                      '        <p>Vearsa1, </p>'
                      '        <p>vearsa2. </p>'
                      '      </section>'
                      '    </section>'
                      '  </body>'
                      '</document>'),
    },
    'book_chapter_section_p': {
        'orig': (u'<document>'
                 u'  <header>'
                 u'    <title>1</title>'
                 u'  </header>'
                 u'  <body>'
                 u'    <book title="1 Sálmmaid girji ">'
                 u'      <chapter number="1">'
                 u'        <section title="Section title">'
                 u'          <verse number="1">Vearsa1 </verse>'
                 u'          <p>'
                 u'            <verse number="2">Vearsa2, </verse>'
                 u'            <verse number="3">vearsa3. </verse>'
                 u'          </p>'
                 u'          <verse number="4">Vearsa 4.</verse>'
                 u'        </section>'
                 u'      </chapter>'
                 u'    </book>'
                 u'  </body>'
                 u'</document>'),
        'converted': ('<document>'
                      '  <body>'
                      '    <section>'
                      '      <p type="title">1 Sálmmaid girji</p>'
                      '      <section>'
                      '        <p type="title">1</p>'
                      '        <section>'
                      '          <p type="title">Section title</p>'
                      '          <p>Vearsa1 </p>'
                      '          <p>Vearsa2, vearsa3.</p>'
                      '          <p>Vearsa 4.</p>'
                      '        </section>'
                      '      </section>'
                      '    </section>'
                      '  </body>'
                      '</document>'),
    },
}


def assertXmlEqual(got, want):
    """Check if two xml snippets are equal."""
    got = lxml.etree.tostring(got, encoding='unicode')
    want = lxml.etree.tostring(want, encoding='unicode')
    checker = lxml.doctestcompare.LXMLOutputChecker()
    if not checker.check_output(want, got, 0):
        message = checker.output_difference(doctest.Example("", want), got, 0)
        raise AssertionError(message)


def test_conversion():
    """Test conversion of bible xml elements."""
    for testname, bible_xml in six.iteritems(TESTS):
        yield check_conversion, testname, bible_xml


def check_conversion(testname, bible_xml):
    """Check that the bible xml is correctly converted."""
    with TempDirectory() as temp_dir:
        corpusfilename = 'orig/sme/bible/nt/bogus.bible.xml'
        temp_dir.write(corpusfilename, bible_xml['orig'].encode('utf8'))

        got = biblexmlconverter.convert2intermediate(
            os.path.join(temp_dir.path, corpusfilename))
        want = lxml.etree.fromstring(bible_xml['converted'])

        assertXmlEqual(got, want)
