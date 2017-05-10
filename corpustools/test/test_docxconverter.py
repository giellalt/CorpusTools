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
#   Copyright © 2014-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Test conversion of docx files."""
import os

from lxml import etree

from corpustools.docxconverter import DocxConverter
from corpustools.test.xmltester import XMLTester

HERE = os.path.dirname(__file__)


class TestDocxConverter(XMLTester):
    """Test docx conversion."""

    def test_convert2intermediate(self):
        """Test docx conversion of a docx file."""
        testdoc = DocxConverter(
            os.path.join(
                HERE,
                'converter_data/fakecorpus/orig/sme/riddu/doc-test.docx'))

        got = testdoc.convert2intermediate()
        want = (
            '<document>'
            '    <header>'
            '        <title/>'
            '    </header>'
            '    <body>'
            '        <p>–Mun lean njeallje jagi boaris.</p>'
            '        <p>Nu beaivvádat.</p>'
            '        <p>oahppat guovttejuvlla nalde sykkelastit.</p>'
            '        <p>njeallje suorpma boaris.</p>'
            '        <p>Olggobealde Áššu</p>'
            '        <p>Lea go dus meahccebiila ?</p>'
            '        <p>–Mii lea suohttaseamos geassebargu dus ?</p>'
            '        <p>Suohkana bearašásodagaid juohkin</p>'
            '        <p>Sámi kulturfestivála 1998</p>'
            '    </body>'
            '</document>')

        self.assertXmlEqual(got, etree.fromstring(want))
