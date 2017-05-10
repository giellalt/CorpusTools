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

u"""Test conversion of pdf files."""

import collections
import os
import unittest

import lxml.etree as etree

from corpustools import pdfconverter, xslsetter
from corpustools.test import xmltester

HERE = os.path.dirname(__file__)

class TestPDFTextElement(xmltester.XMLTester):

    def test_font_property(self):
        """When top is the same, two text elements are on the same line."""
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="354" left="332" width="6" height="22" font="2"> '
            '</text>'))

        self.assertEqual(t1.font, '2')

    def test_is_text_on_same_line_1(self):
        """When top is the same, two text elements are on the same line."""
        prev_t = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="354" left="119" width="205" height="22" font="2">'
            '1.1.   RIEKTEJOAVKKU</text>'))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="354" left="332" width="6" height="22" font="2"> '
            '</text>'))

        self.assertTrue(t1.is_text_on_same_line(prev_t))

    def test_is_text_on_same_line_2(self):
        ''''''
        prev_t = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="354" left="332" width="6" height="22" font="2"> '
            '</text>'))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="350" left="339" width="4" height="16" font="7"> '
            '</text>'))

        self.assertTrue(t1.is_text_on_same_line(prev_t))

    def test_is_text_on_same_line_3(self):
        ''''''
        prev_t = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="350" left="339" width="4" height="16" font="7"> '
            '</text>'))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="354" left="343" width="104" height="22" font="2">'
            'MANDÁHTA</text>'))

        self.assertTrue(t1.is_text_on_same_line(prev_t))

    def test_is_text_on_same_line_4(self):
        ''''''
        prev_t = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="354" left="615" width="13" height="22" font="2">  '
            '</text>'))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="376" left="119" width="6" height="22" font="2"> '
            '</text>'))

        self.assertFalse(t1.is_text_on_same_line(prev_t))

    def test_merge_text_elements(self):
        """Merge two text elements."""
        prev_t = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="354" left="119" width="205" height="22" font="2">'
            '1.1. RIEKTEJOAVKKU</text>'))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="354" left="332" width="6" height="22" font="2"> '
            '</text>'))

        prev_t.merge_text_elements(t1)
        self.assertXmlEqual(prev_t.t,
                            etree.fromstring('<text top="354" left="119" '
                                             'width="211" height="22" font="2">'
                                             '1.1. RIEKTEJOAVKKU </text>'))


class TestPDFParagraph(xmltester.XMLTester):
    """Test the PDFParagraph class."""

    def setUp(self):
        self.textelements = [
            pdfconverter.PDFTextElement(etree.fromstring(
                u'<text top="1078" left="86" width="347" height="15" font="4">'
                u'guoh-</text>')),
            pdfconverter.PDFTextElement(etree.fromstring(
                u'<text top="1095" left="85" width="349" height="15" font="4">'
                u'tuma </text>')),
            pdfconverter.PDFTextElement(etree.fromstring(
                u'<text top="112" left="464" width="347" height="15" font="4">'
                u'main</text>'))
        ]

    def test_append_first_textelement(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(self.textelements[0])

        self.assertListEqual(pp.textelements, self.textelements[:-2])
        self.assertEqual(pp.boundingboxes[-1].top, self.textelements[0].top)
        self.assertEqual(pp.boundingboxes[-1].left, self.textelements[0].left)
        self.assertEqual(
            pp.boundingboxes[-1].bottom, self.textelements[0].bottom)
        self.assertEqual(
            pp.boundingboxes[-1].right, self.textelements[0].right)
        self.assertEqual(len(pp.boundingboxes), 1)

    def test_append_textelement_from_same_column(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(self.textelements[0])
        pp.append_textelement(self.textelements[1])

        self.assertListEqual(pp.textelements, self.textelements[:-1])
        self.assertEqual(len(pp.boundingboxes), 1)
        self.assertEqual(pp.boundingboxes[-1].top, self.textelements[0].top)
        self.assertEqual(pp.boundingboxes[-1].left, self.textelements[1].left)
        self.assertEqual(
            pp.boundingboxes[-1].bottom, self.textelements[1].bottom)
        self.assertEqual(
            pp.boundingboxes[-1].right, self.textelements[1].right)

    def test_append_textelement_from_different_column(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(self.textelements[0])
        pp.append_textelement(self.textelements[1])
        pp.append_textelement(self.textelements[2])

        self.assertListEqual(pp.textelements, self.textelements)

        self.assertEqual(len(pp.boundingboxes), 2)
        self.assertEqual(pp.boundingboxes[-2].top, self.textelements[0].top)
        self.assertEqual(pp.boundingboxes[-2].left, self.textelements[1].left)
        self.assertEqual(
            pp.boundingboxes[-2].bottom, self.textelements[1].bottom)
        self.assertEqual(
            pp.boundingboxes[-2].right, self.textelements[1].right)
        self.assertEqual(pp.boundingboxes[-1].top, self.textelements[2].top)
        self.assertEqual(pp.boundingboxes[-1].left, self.textelements[2].left)
        self.assertEqual(
            pp.boundingboxes[-1].bottom, self.textelements[2].bottom)
        self.assertEqual(
            pp.boundingboxes[-1].right, self.textelements[2].right)

    def test_append_first_textelement_with_list_character_F0B7(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="961" left="152" width="334" height="26" font="0">  '
            'Bajásšaddan</text>')))

        self.assertTrue(pp.is_listitem)

    def test_append_first_textelement_with_list_character_F071(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="961" left="152" width="334" height="26" font="0">  '
            'Bajásšaddan</text>')))

        self.assertTrue(pp.is_listitem)

    def test_append_first_textelement_with_list_character_25A0(self):
        """Test if 'BLACK SQUARE' is recognised as bullet char."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="961" left="152" width="334" height="26" font="0">'
            '■Bajásšaddan</text>')))

        self.assertTrue(pp.is_listitem)

    def test_append_first_textelement_with_list_character_bullet(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="961" left="152" width="334" height="26" font="0">•  '
            'Bajásšaddan</text>')))

        self.assertTrue(pp.is_listitem)

    def test_is_same_paragraph_1(self):
        """Two text elements, x distance less 1.5 times their height."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="2">'
                'Text1 </text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="126" left="117" width="305" height="19" font="2">text2'
            '</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_2(self):
        """Two text elements, x distance larger 1.5 times their height."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="2">a'
                '</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="140" left="117" width="305" height="19" font="2">b'
            '</text>'))

        self.assertFalse(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_3(self):
        """Two text elements, different heights."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="2">a</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="126" left="117" width="305" height="20" font="2">b</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_4(self):
        """Two text elements, different fonts."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="1">'
                'Text1</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="126" left="117" width="305" height="19" font="2">'
            'Text2</text>'))

        self.assertFalse(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_5(self):
        """List characters signal a new paragraph start."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" '
                'font="2"/>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="126" left="117" width="305" height="19" font="2">'
            '• </text>'))

        self.assertFalse(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_6(self):
        """Upper case char and in_list=True signals new paragraph start."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="300" left="104" width="324" height="18" font="1">'
                'linnjá</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="321" left="121" width="40" height="18" font="1">'
            'Nubbi dábáláš linnjá</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_7(self):
        """and in_list=True signals same paragraph."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="300" left="104" width="324" height="18" font="1">'
                'linnjá</text>')))
        pp.in_list = True
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="321" left="121" width="40" height="18" font="1">'
            ' nubbi dábáláš linnjá</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_8(self):
        """List characters signal a new paragraph start."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" '
                'font="2"/>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            u'<text top="961" left="152" width="334" height="26" font="0">'
            u'\xF0B7  Bajásšaddan, oahpahusa ja dutkama </text>'))

        self.assertFalse(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_on_different_column_or_page1(self):
        """Not same paragraph if first letter in second element is number."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1143" left="168" width="306" height="18" '
                'font="1">Kopp</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="492" left="523" width="309" height="18" '
            'font="1">2.</text>'))

        self.assertFalse(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_on_different_column(self):
        """Same paragraph if first letter in second element is lower case."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1143" left="168" '
                'width="306" height="18" font="1">skuvl-</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="492" left="523" width="309" '
            'height="18" font="1">lain</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_second_line_in_list_paragraph_starts_with_lower(self):
        """List lines, different height, same font, second starts with lower."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="361" left="133" width="555" height="21" font="1">'
                ' sáhttá earret eará rávvet ja bagadit mánáidgárddiid ja '
                'skuvllaid dan hárrái, mo </text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="382" left="160" width="330" height="20" font="1">'
            'pedagogalaččat jođihit joavko- ja oahppanbirrasa</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_second_line_in_list_paragraph_starts_with_upper(self):
        """List lines, different height, same font, second starts with uower."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="361" left="133" width="555" height="21" font="1">'
                ' lea lágas geatnegahttojuvvon gieldda bálvalus, man láhkavuođđun '
                'lea oahpahuslága § 5-6. </text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="382" left="160" width="330" height="20" font="1">'
            'Gielddat sáhttet lágidit bálvalusa ovttas.</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_next_line_in_list_paragraph_starts_with_lower(self):
        """List lines, same height, same font, second starts with lower."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="991" left="85" width="347" height="15" font="4">'
                '• Ásahit  sierra  siidda  mas  leat  searveeallu  ovttain'
                '</text>')))
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1009" left="106" width="325" height="15" font="4">'
                'čearuin/dahje eambbogiiguin Ruoŧabealde ránnjá-</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="112" left="483" width="325" height="15" font="4">'
            'čearuiguin.</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_ends_with_stop_next_line_in_list_paragraph_starts_with_number(self):
        """List lines, same height, same font, second starts with lower."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="991" left="85" width="347" height="15" font="4">'
                '• Ásahit  sierra  siidda  mas  leat  searveeallu  ovttain'
                '</text>')))
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1009" left="106" width="325" height="15" font="4">'
                'čearuin/dahje eambbogiiguin Ruoŧabealde ránnjá.</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="112" left="483" width="325" height="15" font="4">'
            '2 čearuiguin.</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_next_line_in_list_paragraph_starts_with_upper(self):
        """List lines, same height, same font, second starts with upper."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="991" left="85" width="347" height="15" font="4">'
                '• Ásahit  sierra  siidda  mas  leat  searveeallu  ovttain'
                '</text>')))
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1009" left="106" width="325" height="15" font="4">'
                'čearuin/dahje eambbogiiguin Ruoŧabealde ránnjá.</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="112" left="483" width="325" height="15" font="4">'
            'Čearuiguin.</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_next_line_in_list_paragraph_starts_with_number(self):
        """List lines, same height, same font, second starts with upper."""
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="991" left="85" width="347" height="15" font="4">'
                '• Ásahit  sierra  siidda  mas  leat  searveeallu  ovttain'
                '</text>')))
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1009" left="106" width="325" height="15" font="4">'
                'čearuin/dahje eambbogiiguin Ruoŧabealde ránnjá.</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="112" left="483" width="325" height="15" font="4">'
            '2 čearuiguin.</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_list_paragraph_no_indent_but_space(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="342" left="104" width="295" height="18" font="1">'
                '•   Buohkain       galgá   leat    vuoigatvuohta   oahppat '
                '</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="363" left="104" width="80" height="18" font="1">  '
            'sámegiela</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_list_paragraph_same_font_different_height(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1049" left="152" width="542" height="26" font="0">'
                '  Dearvvašvuođa ja sosiála, dákko bakte olmmošlogu rievdan, '
                '</text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="1079" left="179" width="177" height="23" font="0">'
            'demografiija, dienas </text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_indented_paragraph_start(self):
        pp = pdfconverter.PDFParagraph(1.5)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="586" left="149" width="324" height="20" font="6">'
                'nuppástuvvan maŋimuš logijagiid áigge olu. </text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="606" left="174" width="604" height="20" font="6">'
            'Bargomárkanat  leat  juohkásan  albmáid  ja  nissoniid  '
            'ámmátsurggiide.  Dušše  15 </text>'))

        self.assertFalse(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_larger_than_default_linespacing(self):
        pp = pdfconverter.PDFParagraph(2.0)
        pp.append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="2">'
                'Text1 </text>')))
        t1 = pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="136" left="117" width="305" height="19" font="2">text2'
            '</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))


class TestPDFFontspecs(unittest.TestCase):

    def test_add_fontspec(self):
        f1 = etree.fromstring(
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>')
        f2 = etree.fromstring(
            '<fontspec id="5" size="19" family="Times" color="#231f20"/>')
        f3 = etree.fromstring(
            '<fontspec id="6" size="13" family="Times" color="#231f20"/>')

        pdffontspecs = pdfconverter.PDFFontspecs()
        pdffontspecs.add_fontspec(f1)
        pdffontspecs.add_fontspec(f2)
        pdffontspecs.add_fontspec(f3)

        self.assertListEqual(
            sorted([id for p, id in pdffontspecs.pdffontspecs.items()]),
            ["1", "5"])
        self.assertDictEqual(pdffontspecs.duplicates, {"6": "1"})

    def test_corrected_id(self):
        page = etree.fromstring(
            '''
            <page number="3" position="absolute" top="0" left="0" height="1325" width="955">
                <fontspec id="1" size="13" family="Times" color="#231f20"/>
                <fontspec id="5" size="19" family="Times" color="#231f20"/>
                <fontspec id="6" size="13" family="Times" color="#231f20"/>
                <text top="634" left="104" width="178" height="26" font="5"><i><b>Politihkalaš vuođđu </b></i></text>
                <text top="666" left="104" width="312" height="18" font="1">Ráđđehusbellodagaid politihkalaš vuođđu – <i>Soria </i></text>
                <text top="687" left="104" width="318" height="18" font="6"><i>Moria-julggaštus</i> – almmuha ulbmilin dakkár sáme-</text>
            </page>
        ''')  # nopep8
        pfs = pdfconverter.PDFFontspecs()
        for xmlfontspec in page.iter('fontspec'):
            pfs.add_fontspec(xmlfontspec)
        ppage = pdfconverter.PDFPage(page)
        ppage.fix_font_id(pfs)

        self.assertListEqual([pdftextelement.font
                              for pdftextelement in ppage.textelements],
                             ["5", "1", "1"])


class TestPDFTextExtractor(xmltester.XMLTester):

    def test_extract_textelement1(self):
        """Extract text from a plain pdf2xml text element."""
        p2x = pdfconverter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="649" left="545" width="269" height="14" font="20">'
            'berret bargat. </text>')
        p2x.extract_textelement(input)
        self.assertXmlEqual(p2x.p,
                            etree.fromstring('<p>berret bargat. </p>'))

    def test_extract_textelement3(self):
        """Extract text from a pdf2xml text that contains an <i> element."""
        p2x = pdfconverter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i>Ei </i></text>')
        p2x.extract_textelement(input)
        self.assertXmlEqual(p2x.p,
                            etree.fromstring('<p><em type="italic">Ei </em></p>'))

    def test_extract_textelement4(self):
        """Extract text from a pdf2xml text that contains a <b> element."""
        p2x = pdfconverter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<b>Ei </b></text>')
        p2x.extract_textelement(input)
        self.assertXmlEqual(p2x.p,
                            etree.fromstring('<p><em type="bold">Ei </em></p>'))

    def test_extract_textelement5(self):
        """Text that contains a <b> element inside the <i> element."""
        p2x = pdfconverter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i><b>Eiš </b></i></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(p2x.p,
                            etree.fromstring('<p><em type="italic">Eiš </em></p>'))

    def test_extract_textelement6(self):
        """Text that contains a <b> element including a tail."""
        p2x = pdfconverter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<b>E</b> a</text>')
        p2x.extract_textelement(input)
        self.assertXmlEqual(p2x.p,
                            etree.fromstring('<p><em type="bold">E</em> a</p>'))

    def test_extract_textelement7(self):
        """Extract text from a pdf2xml text that contains two <i> elements."""
        p2x = pdfconverter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i>E</i> a <i>b</i></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(p2x.p,
                            etree.fromstring('<p><em type="italic">E</em> a '
                                             '<em type="italic">b</em></p>'))

    def test_extract_textelement8(self):
        """Text that contains one <i> element with several <b> elements."""
        p2x = pdfconverter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="837" left="57" width="603" height="11" font="7">'
            '<i><b>Å.</b> B <b>F.</b> A </i></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(p2x.p,
                            etree.fromstring('<p><em type="italic">Å. B F. A '
                                             '</em></p>'))

    def test_extract_textelement9(self):
        """Text that contains one <b> element with several <i> elements."""
        p2x = pdfconverter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="837" left="57" width="603" height="11" font="7">'
            '<b><i>Å.</i> B <i>F.</i> A </b></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(p2x.p,
                            etree.fromstring('<p><em type="bold">Å. B F. A '
                                             '</em></p>'))

    def test_get_body(self):
        """Test the initial values when the class is initiated."""
        p2x = pdfconverter.PDFTextExtractor()

        self.assertXmlEqual(p2x.body, etree.fromstring('<body><p/></body>'))

    def test_handle_line_ending_shy(self):
        p2x = pdfconverter.PDFTextExtractor()
        p2x.extract_textelement(etree.fromstring(u'<text>a\xAD</text>'))
        p2x.handle_line_ending()

        self.assertXmlEqual(
            p2x.p, etree.fromstring(u'<p>a\xAD</p>'))

    def test_handle_line_ending_hyphen(self):
        p2x = pdfconverter.PDFTextExtractor()
        p2x.extract_textelement(etree.fromstring(u'<text>a-</text>'))
        p2x.handle_line_ending()

        self.assertXmlEqual(
            p2x.p, etree.fromstring(u'<p>a\xAD</p>'))

    def test_handle_line_ending_hyphen_last_child_has_no_tail(self):
        p2x = pdfconverter.PDFTextExtractor()
        p2x.extract_textelement(etree.fromstring(u'<text><i>a-</i></text>'))
        p2x.handle_line_ending()

        self.assertXmlEqual(
            p2x.p, etree.fromstring(u'<p><em type="italic">a\xAD</em></p>'))

    def test_handle_line_ending_hyphen_last_child_has_tail(self):
        p2x = pdfconverter.PDFTextExtractor()
        p2x.extract_textelement(etree.fromstring(u'<text><i>a</i>-</text>'))
        p2x.handle_line_ending()

        self.assertXmlEqual(
            p2x.p, etree.fromstring(u'<p><em type="italic">a</em>\xAD</p>'))

    def test_handle_line_ending_hyphen_space(self):
        """If - is not the last char, do not replace it by a soft hyphen."""
        for test_text in ['a-\t', 'a- ']:
            p2x = pdfconverter.PDFTextExtractor()
            p2x.extract_textelement(etree.fromstring(u'<text>a- </text>'))
            p2x.handle_line_ending()

            self.assertXmlEqual(
                p2x.p, etree.fromstring('<p>a-</p>'))

    def test_handle_line_not_shy_nor_hyphen(self):
        p2x = pdfconverter.PDFTextExtractor()
        p2x.extract_textelement(etree.fromstring(u'<text>a</text>'))
        p2x.handle_line_ending()

        self.assertXmlEqual(
            p2x.p, etree.fromstring('<p>a </p>'))

    def test_handle_upper_case_on_new_page(self):
        """If the first paragraph begins with an uppercase letter, start a new p."""
        p2x = pdfconverter.PDFTextExtractor()
        p2x.p.text = 'not ending with sentence stop character'

        paragraphs = [pdfconverter.PDFParagraph(1.5)]
        paragraphs[-1].append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1" left="1" width="1" height="1">Upper case.'
                '</text>')))

        p2x.extract_text_from_page(paragraphs)

        self.assertXmlEqual(p2x.body,
                            etree.fromstring('''
                            <body>
                                <p>not ending with sentence stop character</p>
                                <p>Upper case.</p>
                            </body>'''))

    def test_handle_number_on_new_page(self):
        """If the first paragraph begins with a number, start a new p."""
        p2x = pdfconverter.PDFTextExtractor()
        p2x.p.text = 'not ending with sentence stop character'

        paragraphs = [pdfconverter.PDFParagraph(1.5)]
        paragraphs[-1].append_textelement(
            pdfconverter.PDFTextElement(etree.fromstring(
                '<text top="1" left="1" width="1" height="1">1 element.'
                '</text>')))

        p2x.extract_text_from_page(paragraphs)

        self.assertXmlEqual(p2x.body,
                            etree.fromstring('''
                            <body>
                                <p>not ending with sentence stop character</p>
                                <p>1 element.</p>
                            </body>'''))

    def test_add_list_paragraphs(self):
        listtemplate = ('<text top="961" left="152" width="334" height="26" '
                        'font="0">{}</text>')
        listchars = [
            '&#61623; ',  # U+F0B7: <private use>
            '&#61553; ',  # U+F071: <private use>
            '•\t',  # U+2022: BULLET
            '– ',  # U+2013: EN DASH
            '- ',  # U+002D: HYPHEN-MINUS
            u'■ ',  # U+25A0: BLACK SQUARE
            ' &#61692; ',  # U+F0FC: <private use>
        ]

        paragraphs = []
        for listchar in listchars:
            pp = pdfconverter.PDFParagraph(1.5)
            pp.append_textelement(
                pdfconverter.PDFTextElement(etree.fromstring(
                    listtemplate.format(listchar))))
            paragraphs.append(pp)

        p2x = pdfconverter.PDFTextExtractor()
        p2x.extract_text_from_page(paragraphs)

        self.assertXmlEqual(p2x.body,
                            etree.fromstring(
                                '<body>'
                                '<p type="listitem">&#61623; </p>'
                                '<p type="listitem">&#61553; </p>'
                                '<p type="listitem">&#8226;\t</p>'
                                '<p type="listitem">&#8211; </p>'
                                '<p type="listitem">- </p>'
                                '<p type="listitem">■ </p>'
                                '<p type="listitem"> &#61692; </p>'
                                '</body>'))

    def test_add_space_list(self):
        listtemplate = ('<text top="961" left="152" width="334" height="26" '
                        'font="0">{}</text>')
        alternatives = [
            '•test',
            '<i>•test</i>',
            '<b><i>•test</i></b>',
        ]

        paragraphs = []
        for alternative in alternatives:
            pp = pdfconverter.PDFParagraph(1.5)
            pp.append_textelement(
                pdfconverter.PDFTextElement(etree.fromstring(
                    listtemplate.format(alternative))))
            paragraphs.append(pp)

        p2x = pdfconverter.PDFTextExtractor()
        p2x.extract_text_from_page(paragraphs)

        self.assertXmlEqual(p2x.body,
                            etree.fromstring(
                                '<body>'
                                '<p type="listitem">• test</p>'
                                '<p type="listitem">'
                                '   <em type="italic">• test</em>'
                                '</p>'
                                '<p type="listitem">'
                                '   <em type="bold">• test</em>'
                                '</p>'
                                '</body>'))


class TestPDFSection(xmltester.XMLTester):

    def test_is_same_section_paragraph_following_listitems(self):
        section_elements = [
            '<text top="478" left="51" width="245" height="18" font="1">Leat '
            'geatnegahtton kártengeahččaleamit:</text>',
            '<text top="496" left="51" width="163" height="18" font="1">• '
            'Lohkamis 1., 2. ja 3. ceahkis</text>',
            '<text top="514" left="51" width="153" height="18" font="1">• '
            'Rehkenastimis 2. ceahkis </text>',
        ]
        section = pdfconverter.PDFSection()
        for element in section_elements:
            p1 = pdfconverter.PDFParagraph(1.5)
            p1.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
                element)))
            section.append_paragraph(p1)

        paragraph_elements = [
            '<text top="550" left="51" width="193" height="18" font="1">Buot '
            'oahppit galget váldit daid </text>',
            '<text top="568" left="51" width="230" height="18" font="1">'
            'geatnegahtton kártengeahččalemiid. </text>',
            '<text top="586" left="51" width="214" height="18" font="1">'
            'Oahppit geat leat eret geahččalan- </text>',
            '<text top="604" left="51" width="228" height="18" font="1">'
            'beaivvi, galget čađahit geahččaleami </text>',
            '<text top="622" left="51" width="45" height="18" font="1">'
            'maŋŋil.</text>'
        ]
        p2 = pdfconverter.PDFParagraph(1.5)
        for element in paragraph_elements:
            p2.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
                element)))

        self.assertTrue(section.is_same_section(p2))

    def test_is_same_section_listitem_following_standard_paragraph(self):
        """list items are often narrower than previous standard paragraphs."""
        p1 = pdfconverter.PDFParagraph(1.5)
        p1.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="460" left="51" width="242" height="18" font="0"><b>'
            'Geatnegahtton kártengeahččaleamit</b></text>')))
        p1.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="478" left="51" width="245" height="18" font="1">Leat '
            'geatnegahtton kártengeahččaleamit:</text>')))
        section = pdfconverter.PDFSection()
        section.append_paragraph(p1)

        p2 = pdfconverter.PDFParagraph(1.5)
        p2.append_textelement(pdfconverter.PDFTextElement(etree.fromstring(
            '<text top="496" left="51" width="163" height="18" font="1">'
            '• Lohkamis 1., 2. ja 3. ceahkis</text>')))

        self.assertTrue(section.is_same_section(p2))

Interval = collections.namedtuple('Interval', ['start', 'end'])


class TestProblematicPageTwoColumnsTablesHeaderLast(xmltester.XMLTester):

    def setUp(self):
        self.start_page = etree.fromstring('''
            <page number="258" position="absolute" top="0" left="0" height="1261" width="892">
                <text top="51" left="85" width="25" height="15" font="4">258</text>
                <text top="72" left="85" width="62" height="12" font="5">1. Mielddus</text>
                <text top="377" left="85" width="86" height="15" font="9"><i><b>6.1. tabealla.</b></i></text>
                <text top="403" left="274" width="113" height="15" font="4">Doalloovttadagat</text>
                <text top="403" left="496" width="51" height="15" font="4">Olbmot</text>
                <text top="403" left="642" width="127" height="15" font="4">Alimus boazolohku</text>
                <text top="428" left="85" width="32" height="15" font="4">Elgå </text>
                <text top="428" left="331" width="8" height="15" font="4">6</text>
                <text top="428" left="517" width="17" height="15" font="4">30</text>
                <text top="428" left="690" width="38" height="15" font="4">3 000</text>
                <text top="446" left="85" width="86" height="15" font="4">Riast/Hylling</text>
                <text top="446" left="323" width="17" height="15" font="4">10</text>
                <text top="446" left="517" width="17" height="15" font="4">51</text>
                <text top="446" left="690" width="38" height="15" font="4">4 500</text>
                <text top="463" left="85" width="49" height="15" font="4">Essand </text>
                <text top="463" left="323" width="17" height="15" font="4">10</text>
                <text top="463" left="517" width="17" height="15" font="4">43</text>
                <text top="463" left="690" width="38" height="15" font="4">4 500</text>
                <text top="480" left="85" width="79" height="15" font="4">Trollheimen</text>
                <text top="480" left="331" width="8" height="15" font="4">5</text>
                <text top="480" left="517" width="17" height="15" font="4">20</text>
                <text top="480" left="690" width="38" height="15" font="4">1 600</text>
                <text top="506" left="85" width="45" height="15" font="4">Submi </text>
                <text top="506" left="323" width="17" height="15" font="4">31</text>
                <text top="506" left="509" width="25" height="15" font="4">144</text>
                <text top="506" left="682" width="46" height="15" font="4">13 600</text>
                <text top="560" left="85" width="347" height="15" font="4">Femunddas  lea  alimus  mearriduvvon  boazolohku</text>
                <text top="577" left="85" width="347" height="15" font="4">9 000  bohcco.  Boazolohku  lea  juhkkojuvvon  ovt-</text>
                <text top="595" left="85" width="347" height="15" font="4">tamađe Riast/Hylling ja Essand orohagaid gaskka. Go</text>
                <text top="560" left="461" width="347" height="15" font="4"><b>6.2. tabeallas </b>meroštallá boazoeatnatvuođa ja buvtta-</text>
                <text top="577" left="461" width="347" height="15" font="4">deami juohke areálovttadaga nammii, leat Femundda</text>
                <text top="595" left="461" width="283" height="15" font="4">areálat juogáduvvon dán guovtti orohahkii.</text>
                <text top="638" left="85" width="560" height="15" font="9"><i><b>6.2. tabealla. </b>Lulli-Trøndelága/Hedmark boazodoalloguovllu eatnamiid geavaheapmi.</i></text>
                <text top="666" left="299" width="42" height="15" font="4">Areála</text>
                <text top="663" left="446" width="78" height="15" font="4">Boazolohku</text>
                <text top="663" left="665" width="90" height="15" font="4">Buvttadeapmi</text>
                <text top="684" left="308" width="21" height="15" font="4">km</text>
                <text top="684" left="328" width="5" height="9" font="12">2</text>
                <text top="687" left="392" width="58" height="15" font="4">01.04.98</text>
                <text top="687" left="500" width="69" height="15" font="4">juohke km</text>
                <text top="687" left="569" width="5" height="9" font="12">2</text>
                <text top="687" left="627" width="41" height="15" font="4">kg/km</text>
                <text top="687" left="667" width="5" height="9" font="12">2</text>
                <text top="687" left="724" width="59" height="15" font="4">kg/boazu</text>
                <text top="713" left="85" width="28" height="15" font="4">Elgå</text>
                <text top="713" left="304" width="33" height="15" font="4">1007</text>
                <text top="713" left="405" width="33" height="15" font="4">3026</text>
                <text top="713" left="526" width="21" height="15" font="4">3,0</text>
                <text top="713" left="635" width="29" height="15" font="4">32,4</text>
                <text top="713" left="745" width="17" height="15" font="4">11</text>
                <text top="730" left="85" width="183" height="15" font="4">Femund (dálvejagi guohtun)</text>
                <text top="730" left="304" width="33" height="15" font="4">1103</text>
                <text top="730" left="400" width="43" height="15" font="4">(8887)</text>
                <text top="747" left="85" width="171" height="15" font="4">Riast/Hylling (bievlajahki)</text>
                <text top="747" left="304" width="33" height="15" font="4">2481</text>
                <text top="747" left="405" width="33" height="15" font="4">4314</text>
                <text top="747" left="526" width="21" height="15" font="4">1,7</text>
                <text top="747" left="635" width="29" height="15" font="4">22,6</text>
                <text top="747" left="739" width="29" height="15" font="4">12,3</text>
                <text top="764" left="85" width="130" height="15" font="4">Essand (bievlajahki)</text>
                <text top="764" left="304" width="33" height="15" font="4">2876</text>
                <text top="764" left="405" width="33" height="15" font="4">4573</text>
                <text top="764" left="526" width="21" height="15" font="4">1,6</text>
                <text top="764" left="635" width="29" height="15" font="4">17,3</text>
                <text top="764" left="739" width="29" height="15" font="4">10,5</text>
                <text top="782" left="85" width="79" height="15" font="4">Trollheimen</text>
                <text top="782" left="304" width="33" height="15" font="4">2235</text>
                <text top="782" left="405" width="33" height="15" font="4">1630</text>
                <text top="782" left="526" width="21" height="15" font="4">0,7</text>
                <text top="782" left="639" width="21" height="15" font="4">7,9</text>
                <text top="782" left="739" width="29" height="15" font="4">10,7</text>
                <text top="807" left="304" width="33" height="15" font="4">8598</text>
                <text top="807" left="401" width="42" height="15" font="4">13543</text>
                <text top="807" left="526" width="21" height="15" font="4">1,6</text>
                <text top="807" left="635" width="207" height="15" font="4">18,211,2</text>
                <text top="853" left="85" width="347" height="15" font="4">Lea mihá eambo boazoeatnatvuohta go Davvi-Trøn-</text>
                <text top="871" left="85" width="347" height="15" font="4">delágas, Nordlánddas ja Romssas. Duogážin lea dál-</text>
                <text top="888" left="85" width="347" height="15" font="4">vejagi  guohtumiid  vejolašvuohta,  ja  áigodaga  iešgu-</text>
                <text top="905" left="85" width="347" height="15" font="4">đetlágan  guođohanvejolašvuohta.  Earret  Elgå,  leat</text>
                <text top="922" left="85" width="347" height="15" font="4">Lulli-Trøndelága/Hedmark  orohagaid  boazoeatnat-</text>
                <text top="940" left="85" width="318" height="15" font="4">vuohta  vuollelis  go  Kárášjogas  (2,4  bohcco/km</text>
                <text top="940" left="403" width="5" height="9" font="12">2</text>
                <text top="940" left="408" width="23" height="15" font="4">)  ja</text>
                <text top="957" left="85" width="239" height="15" font="4">Oarje-Finnmárkkus  (3,1  bohcco/km</text>
                <text top="957" left="324" width="5" height="9" font="12">2</text>
                <text top="957" left="329" width="102" height="15" font="4">).  Riast/Hylling</text>
                <text top="974" left="85" width="347" height="15" font="4">orohagas lea eambbo buvttadeapmi bohcco ektui go</text>
                <text top="991" left="85" width="347" height="15" font="4">dáin earáin, muhto buot orohagaid dássi lea vuollelis</text>
                <text top="1009" left="85" width="347" height="15" font="4">go ovdal. Elgå:s lea mearkkašahtti alla boazolohku ja</text>
                <text top="1026" left="85" width="347" height="15" font="4">buvttadeapmi  juohke  areálovttadaga  nammii.  Eará</text>
                <text top="853" left="461" width="347" height="15" font="4">orohagain Norggas ii dáidde leat ná stuora areálbuvt-</text>
                <text top="871" left="461" width="64" height="15" font="4">tadeapmi.</text>
                <text top="888" left="478" width="329" height="15" font="4">Maŋemus  golmma  jagi  njuovvandeattuid  oaidnit</text>
                <text top="905" left="461" width="347" height="15" font="4"><b>6.2. tabeallas. </b>Das oaidnit orohagaid siskkáldas ero-</text>
                <text top="922" left="461" width="347" height="15" font="4">husaid jagis jahkái. Dás boahtá ovdan ahte dássi lea</text>
                <text top="940" left="461" width="347" height="15" font="4">veahá vuollelis go Nordlánddas ja Davvi-Trøndelágas</text>
                <text top="957" left="461" width="347" height="15" font="4">ja arvat vuollelis Romssa. Orohagaid siskkáldas ero-</text>
                <text top="974" left="461" width="347" height="15" font="4">husat jagis jahkái leat luonddudilálašvuođaid erohu-</text>
                <text top="991" left="461" width="347" height="15" font="4">said  geažil,  muhto  erohusat  sáhttet  maiddái  váikku-</text>
                <text top="1009" left="461" width="347" height="15" font="4">huvvot das makkár bohccuid leat njuovvan ja makkár</text>
                <text top="1026" left="461" width="130" height="15" font="4">ealihanbohccot leat.</text>
                <text top="110" left="85" width="344" height="24" font="10"><b>6.1 Lulli-Trøndelága/Hedmark –</b></text>
                <text top="134" left="136" width="227" height="24" font="10"><b>Jämtlándda leana, lulit</b></text>
                <text top="158" left="136" width="69" height="24" font="10"><b>guovlu</b></text>
                <text top="198" left="85" width="76" height="15" font="9"><i><b>Obbalaččat</b></i></text>
                <text top="215" left="85" width="347" height="15" font="4">Prinsihpas eai leat orohatrájit rievdaduvvon jagi 1894</text>
                <text top="232" left="85" width="347" height="15" font="4">rájes. Rievdadeamit leat váldosaččat dahkkon máŋg-</text>
                <text top="250" left="85" width="347" height="15" font="4">gaid duomuid vuođul maid Alimusriekti lea meannu-</text>
                <text top="267" left="85" width="347" height="15" font="4">dan. Das daddjo ahte orohagat leat ovddasvástádus-</text>
                <text top="284" left="85" width="347" height="15" font="4">suorggit,  ja  dat  ii  dárbbaš  mearkkašit  ahte  dain  lea</text>
                <text top="301" left="85" width="346" height="15" font="4">vuoigatvuohta  guovlluide.  Lávdegotti  mandáhttan</text>
                <text top="319" left="85" width="347" height="15" font="4">ii leat  čiekŋudit  dien  áššái,  muhto  fágalávdegoddi</text>
                <text top="336" left="85" width="347" height="15" font="4">oaidná movt eahpečielga riektedilli lea dagahan labiila</text>
                <text top="112" left="461" width="347" height="15" font="4">dilálašvuođaid.  Dán  geažil  leage  lávdegoddái  váttis</text>
                <text top="129" left="461" width="347" height="15" font="4">suokkardit dálá guohtuneatnamiid geavaheami ja dan</text>
                <text top="146" left="461" width="289" height="15" font="4">vuođul evttohit rievdadusaid guohtunrájiide.</text>
                <text top="163" left="478" width="330" height="15" font="4">Guovllus leat 6 boazoorohaga. Riast ja Hylling lea</text>
                <text top="181" left="461" width="347" height="15" font="4">oktasaš. Essand ja Riast/Hylling orohagain lea oktasaš</text>
                <text top="198" left="461" width="347" height="15" font="4">dálvejagi  guohtun  Femunddas.  Elgå  ja  Trollheimen</text>
                <text top="215" left="461" width="347" height="15" font="4">leat  fas  birrajagiorohagat.  Trollheimen  lea  áidna</text>
                <text top="232" left="461" width="347" height="15" font="4">orohat  mii  ii  leat  riikaráji  guoras,  muhto  lea  sierra</text>
                <text top="250" left="461" width="347" height="15" font="4">eará orohagain eret. Danne eat čilge dárkileappot dán</text>
                <text top="267" left="461" width="347" height="15" font="4">orohaga  birra.  Eará  orohagaid  birra  mii  čilget</text>
                <text top="284" left="461" width="72" height="15" font="4">oktasaččat.</text>
                <text top="301" left="478" width="330" height="15" font="4"><b>6.1.  ja  6.2.  tabeallas </b>oaidnit  boazodoalloguovllu</text>
                <text top="319" left="461" width="190" height="15" font="4">struktuvrra ja eatnamiid anu.</text>
            </page>
        ''')  # nopep8

    def test_make_unordered_paragraphs(self):
        expected_page = etree.fromstring(u'''
            <body>
                <p>
                    <em type="italic">6.1. tabealla.</em>
                </p>
                <p>DoalloovttadagatOlbmotAlimus boazolohku</p>
                <p>Elgå 3 000 Riast/Hylling4 500 Essand 4 500 Trollheimen1 600</p>
                <p>Submi 13 600</p>
                <p>
                Femunddas  lea  alimus  mearriduvvon  boazolohku 9 000  bohcco.  Boazolohku  lea  juhkkojuvvon  ovt­tamađe Riast/Hylling ja Essand orohagaid gaskka. Go
                    <em type="bold">6.2. tabeallas</em>meroštallá boazoeatnatvuođa ja buvtta\xADdeami juohke areálovttadaga nammii, leat Femundda areálat juogáduvvon dán guovtti orohahkii.
                </p>
                <p>
                    <em type="italic">6.2. tabealla. Lulli-Trøndelága/Hedmark boazodoalloguovllu eatnamiid geavaheapmi.</em>
                </p>
                <p>AreálaBoazolohkuBuvttadeapmi km01.04.98juohke kmkg/kmkg/boazu</p>
                <p>Elgå3,032,4 Femund (dálvejagi guohtun)(8887) Riast/Hylling (bievlajahki)1,722,612,3 Essand (bievlajahki)1,617,310,5 Trollheimen0,77,910,7</p>
                <p>1,618,211,2</p>
                <p>
                Lea mihá eambo boazoeatnatvuohta go Davvi-Trøn­delágas, Nordlánddas ja Romssas.
                Duogážin lea dál­vejagi  guohtumiid  vejolašvuohta,  ja  áigodaga  iešgu­đetlágan  guođohanvejolašvuohta.
                Earret  Elgå,  leat Lulli-Trøndelága/Hedmark  orohagaid
                boazoeatnat­vuohta  vuollelis  go  Kárášjogas  (2,4  bohcco/km)
                ja Oarje-Finnmárkkus  (3,1  bohcco/km).  Riast/Hylling orohagas
                lea eambbo buvttadeapmi bohcco ektui go dáin earáin, muhto buot
                orohagaid dássi lea vuollelis go ovdal. Elgå:s lea mearkkašahtti
                alla boazolohku ja buvttadeapmi  juohke  areálovttadaga  nammii.  Eará orohagain Norggas ii dáidde leat ná stuora areálbuvt­tadeapmi.
                Maŋemus  golmma  jagi  njuovvandeattuid  oaidnit
                    <em type="bold">6.2. tabeallas.</em>Das oaidnit orohagaid
                    siskkáldas ero\xADhusaid jagis jahkái. Dás boahtá ovdan ahte
                    dássi lea veahá vuollelis go Nordlánddas ja
                    Davvi-Trøndelágas ja arvat vuollelis Romssa. Orohagaid
                    siskkáldas ero­husat jagis jahkái leat luonddudilálašvuođaid
                    erohu­said  geažil,  muhto  erohusat  sáhttet  maiddái
                    váikku­huvvot das makkár bohccuid leat njuovvan ja makkár
                    ealihanbohccot leat.
                </p>
                <p>
                    <em type="bold">6.1 Lulli-Trøndelága/Hedmark –</em>
                    <em type="bold">Jämtlándda leana, lulit</em>
                    <em type="bold">guovlu</em>
                </p>
                <p><em type="italic">Obbalaččat</em></p>
                <p>
                    Prinsihpas eai leat
                    orohatrájit rievdaduvvon jagi 1894 rájes. Rievdadeamit leat
                    váldosaččat dahkkon máŋg­gaid duomuid vuođul maid
                    Alimusriekti lea meannu­dan. Das daddjo ahte orohagat leat
                    ovddasvástádus­suorggit,  ja  dat  ii  dárbbaš  mearkkašit
                    ahte  dain  lea vuoigatvuohta  guovlluide.  Lávdegotti
                    mandáhttan ii leat  čiekŋudit  dien  áššái,  muhto
                    fágalávdegoddi oaidná movt eahpečielga riektedilli lea
                    dagahan labiila dilálašvuođaid.  Dán  geažil  leage
                    lávdegoddái  váttis suokkardit dálá guohtuneatnamiid
                    geavaheami ja dan vuođul evttohit rievdadusaid
                    guohtunrájiide. Guovllus leat 6 boazoorohaga. Riast ja
                    Hylling lea oktasaš. Essand ja Riast/Hylling orohagain lea
                    oktasaš dálvejagi  guohtun  Femunddas.  Elgå  ja
                    Trollheimen leat  fas  birrajagiorohagat.  Trollheimen  lea
                    áidna orohat  mii  ii  leat  riikaráji  guoras,  muhto  lea
                    sierra eará orohagain eret. Danne eat čilge dárkileappot dán
                    orohaga  birra.  Eará  orohagaid  birra  mii  čilget
                    oktasaččat. <em type="bold">6.1.  ja  6.2.  tabeallas</em>oaidnit
                    boazodoalloguovllu struktuvrra ja eatnamiid anu.
                </p>
            </body>
        ''')  # nopep8
        pp = pdfconverter.PDFPage(self.start_page)
        pp.adjust_line_heights()
        pp.remove_elements_not_within_margin()
        pp.remove_footnotes_superscript()
        pp.merge_elements_on_same_line()
        pp.remove_invalid_elements()

        paragraphs = pp.make_unordered_paragraphs()

        extractor = pdfconverter.PDFTextExtractor()
        extractor.extract_text_from_page(paragraphs)
        self.assertXmlEqual(extractor.body,
                            expected_page)

    def test_make_ordered_sections(self):
        expected_page = etree.fromstring(u'''
            <body>
                <p>
                    <em type="bold">6.1 Lulli-Trøndelága/Hedmark –</em>
                    <em type="bold">Jämtlándda leana, lulit</em>
                    <em type="bold">guovlu</em>
                </p>
                <p><em type="italic">Obbalaččat</em></p>
                <p>
                    Prinsihpas eai leat
                    orohatrájit rievdaduvvon jagi 1894 rájes. Rievdadeamit leat
                    váldosaččat dahkkon máŋg­gaid duomuid vuođul maid
                    Alimusriekti lea meannu­dan. Das daddjo ahte orohagat leat
                    ovddasvástádus­suorggit,  ja  dat  ii  dárbbaš  mearkkašit
                    ahte  dain  lea vuoigatvuohta  guovlluide.  Lávdegotti
                    mandáhttan ii leat  čiekŋudit  dien  áššái,  muhto
                    fágalávdegoddi oaidná movt eahpečielga riektedilli lea
                    dagahan labiila dilálašvuođaid.  Dán  geažil  leage
                    lávdegoddái  váttis suokkardit dálá guohtuneatnamiid
                    geavaheami ja dan vuođul evttohit rievdadusaid
                    guohtunrájiide. Guovllus leat 6 boazoorohaga. Riast ja
                    Hylling lea oktasaš. Essand ja Riast/Hylling orohagain lea
                    oktasaš dálvejagi  guohtun  Femunddas.  Elgå  ja
                    Trollheimen leat  fas  birrajagiorohagat.  Trollheimen  lea
                    áidna orohat  mii  ii  leat  riikaráji  guoras,  muhto  lea
                    sierra eará orohagain eret. Danne eat čilge dárkileappot dán
                    orohaga  birra.  Eará  orohagaid  birra  mii  čilget
                    oktasaččat. <em type="bold">6.1.  ja  6.2.  tabeallas</em>
                    oaidnit boazodoalloguovllu struktuvrra ja eatnamiid anu.
                </p>
                <p>
                    <em type="italic">6.1. tabealla.</em>
                </p>
                <p>DoalloovttadagatOlbmotAlimus boazolohku</p>
                <p>Elgå 3 000 Riast/Hylling4 500 Essand 4 500 Trollheimen1 600</p>
                <p>Submi 13 600</p>
                <p>
                Femunddas  lea  alimus  mearriduvvon  boazolohku 9 000  bohcco.
                Boazolohku  lea  juhkkojuvvon  ovt­tamađe Riast/Hylling ja Essand
                orohagaid gaskka. Go
                    <em type="bold">6.2. tabeallas</em>meroštallá
                    boazoeatnatvuođa ja buvtta\xADdeami juohke areálovttadaga
                    nammii, leat Femundda areálat juogáduvvon dán guovtti
                    orohahkii.
                </p>
                <p>
                    <em type="italic">6.2. tabealla. Lulli-Trøndelága/Hedmark
                    boazodoalloguovllu eatnamiid geavaheapmi.</em>
                </p>
                <p>AreálaBoazolohkuBuvttadeapmi km01.04.98juohke kmkg/kmkg/boazu</p>
                <p>Elgå3,032,4 Femund (dálvejagi guohtun)(8887) Riast/Hylling
                (bievlajahki)1,722,612,3 Essand (bievlajahki)1,617,310,5
                Trollheimen0,77,910,7</p>
                <p>1,618,211,2</p>
                <p>
                    Lea mihá eambo boazoeatnatvuohta go Davvi-Trøn­delágas,
                    Nordlánddas ja Romssas. Duogážin lea dál­vejagi  guohtumiid
                    vejolašvuohta,  ja  áigodaga  iešgu­đetlágan
                    guođohanvejolašvuohta.  Earret  Elgå,
                    leat Lulli-Trøndelága/Hedmark  orohagaid  boazoeatnat­vuohta
                    vuollelis  go  Kárášjogas  (2,4  bohcco/km)  ja
                    Oarje-Finnmárkkus  (3,1  bohcco/km).  Riast/Hylling orohagas lea
                    eambbo buvttadeapmi bohcco ektui go dáin earáin, muhto buot
                    orohagaid dássi lea vuollelis go ovdal. Elgå:s lea mearkkašahtti
                    alla boazolohku ja buvttadeapmi  juohke  areálovttadaga  nammii.
                    Eará orohagain Norggas ii dáidde leat ná stuora
                    areálbuvt­tadeapmi. Maŋemus  golmma  jagi  njuovvandeattuid
                    oaidnit <em type="bold">6.2. tabeallas.</em>Das oaidnit orohagaid
                    siskkáldas ero\xADhusaid jagis jahkái. Dás boahtá ovdan ahte
                    dássi lea veahá vuollelis go Nordlánddas ja
                    Davvi-Trøndelágas ja arvat vuollelis Romssa. Orohagaid
                    siskkáldas ero­husat jagis jahkái leat luonddudilálašvuođaid
                    erohu­said  geažil,  muhto  erohusat  sáhttet  maiddái
                    váikku­huvvot das makkár bohccuid leat njuovvan ja makkár
                    ealihanbohccot leat.
                </p>
            </body>
        ''')  # nopep8
        pp = pdfconverter.PDFPage(self.start_page)
        pp.adjust_line_heights()
        pp.remove_elements_not_within_margin()
        pp.remove_footnotes_superscript()
        pp.merge_elements_on_same_line()
        pp.remove_invalid_elements()

        extractor = pdfconverter.PDFTextExtractor()
        extractor.extract_text_from_page(pp.make_ordered_sections().paragraphs)
        self.assertXmlEqual(extractor.body,
                            expected_page,)


class TestProblematicPageTwoColumnsHeaderLast(xmltester.XMLTester):

    def setUp(self):
        self.start_page = etree.fromstring(u'''
            <page height="1261" left="0" number="258" position="absolute" top="0" width="892">
                <text top="51" left="85" width="17" height="15" font="4">12</text>
                <text top="72" left="85" width="62" height="12" font="5">1. Mielddus</text>
                <text top="193" left="85" width="213" height="24" font="10"><b>1.1 Bohcco dárbbut</b></text>
                <text top="232" left="85" width="347" height="15" font="4">Miehtá  Davvikálohta  leat  asehis  guohtoneatnamat</text>
                <text top="250" left="85" width="347" height="15" font="4">bohccuide. Boazu lea luonddudilálašvuođaid hálddus</text>
                <text top="267" left="85" width="347" height="15" font="4">birra jagi. Guohtunšattut leat iešguđetláganat jagi ieš-</text>
                <text top="284" left="85" width="347" height="15" font="4">guđetge áiggis, ja guohtundilli váikkuhage dasto man</text>
                <text top="301" left="85" width="347" height="15" font="4">ollu boazu guohtu ja movt johtala. Dákko dáfus lea</text>
                <text top="319" left="85" width="347" height="15" font="4">boazu  sierralágan  dilis,  Skandinávia  eará  dábmojuv-</text>
                <text top="336" left="85" width="347" height="15" font="4">von  elliid  suktii.  Go  mii  árvvoštállat  guohtumiid,</text>
                <text top="353" left="85" width="347" height="15" font="4">bidjat  bohcco  fysiologalaš  dárbbuid  vuođđun  ja</text>
                <text top="370" left="85" width="231" height="15" font="4">makkár guohtuma boazu dárbbaša.</text>
                <text top="433" left="85" width="215" height="18" font="11"><i><b>1.1.1 Fysiologalaš dárbbut</b></i></text>
                <text top="457" left="85" width="347" height="15" font="4">Boazu maiddái, nu movt earáge eallit, dárbbaša kar-</text>
                <text top="474" left="85" width="347" height="15" font="4">bohydráhtaid ja buoiddi, maid joraha álšan ja doalaha</text>
                <text top="491" left="85" width="347" height="15" font="4">goruda doaimmaid, oažžu lieggasa ja sáhttá lihkadit.</text>
                <text top="508" left="85" width="347" height="15" font="4">Proteiinnat,  vitamiinnat  ja  minerálat  adnojit  hukset</text>
                <text top="526" left="85" width="347" height="15" font="4">dehkiid  ja  eará  gorutgođđosiid,  ja  mielkki  buvtta-</text>
                <text top="543" left="85" width="59" height="15" font="4">deapmái.</text>
                <text top="560" left="102" width="330" height="15" font="4">Boazu lea, nu movt eará smirezasti eallit nai, ere-</text>
                <text top="577" left="85" width="347" height="15" font="4">noamážit heivehuvvon smoldet guohtunšattuid. Alm-</text>
                <text top="595" left="85" width="347" height="15" font="4">matge smoaldanit duššefal okta oasáš das maid boazu</text>
                <text top="612" left="85" width="347" height="15" font="4">guohtu. Dakkár guohtunšattut mat smoaldanit geahp-</text>
                <text top="629" left="85" width="347" height="15" font="4">pasit,  leat  buorit  guohtun.  Ruonasšattut  smoaldanit</text>
                <text top="646" left="85" width="347" height="15" font="4">álkimusat dalle go leat beallešattus ja smoaldaneapmi</text>
                <text top="664" left="85" width="347" height="15" font="4">hedjona  dađi  mielde  go  šattuid  šaddandássi  ovdána.</text>
                <text top="681" left="85" width="347" height="15" font="4">Go biebmu smoaldahuvvá unnán, ii oaččo boazu nu</text>
                <text top="698" left="85" width="347" height="15" font="4">ollu energiija dehe álšša. Maiddái biebmojohtin čoliid</text>
                <text top="715" left="85" width="142" height="15" font="4">čađa mánná njozebut.</text>
                <text top="733" left="102" width="330" height="15" font="4">Boazu lea mihá buorebut, go eará smirezasti eallit,</text>
                <text top="750" left="85" width="347" height="15" font="4">heivehuvvon  smoldet  jeahkála.  Jeahkála  smoalda-</text>
                <text top="767" left="85" width="347" height="15" font="4">neapmi  lea  buorre  birra  jagi.  Dainna  lágiin  nagoda</text>
                <text top="784" left="85" width="347" height="15" font="4">boazu  doalahit  buorren  obbalaš  biebmosmoldema,</text>
                <text top="802" left="85" width="347" height="15" font="4">vaikko vel eará guohtun leage vánis ja maiddái kvali-</text>
                <text top="819" left="85" width="347" height="15" font="4">tehta lea rievddalmas. Dađistaga go čavččabeallái hed-</text>
                <text top="836" left="85" width="347" height="15" font="4">jona  ruonasšattuid  smoaldaneapmi,  guohtugoahtá</text>
                <text top="853" left="85" width="347" height="15" font="4">boazu  eambbo  jeahkála,  iige  guođo  nu  ollu  ruonas-</text>
                <text top="871" left="85" width="347" height="15" font="4">šattuid,  ja  nu  nagoda  almmatge  doalahit  dássedis</text>
                <text top="888" left="85" width="118" height="15" font="4">biebmosmoldema.</text>
                <text top="905" left="102" width="330" height="15" font="4">Jeagil smoaldana geahppasit, muhto lea ovttagear-</text>
                <text top="922" left="85" width="347" height="15" font="4">dánis fuođđar. Jeagelšlájain oažžu boazu nu ollu álšša</text>
                <text top="940" left="85" width="347" height="15" font="4">(karbohydráhtaid)  ahte  ceavzá  badjel  dálvvi,  muhto</text>
                <text top="957" left="85" width="347" height="15" font="4">váilot  proteiinnat,  vitamiinnat  ja  minerálat.  Bohcco</text>
                <text top="974" left="85" width="346" height="15" font="4">guomočoavjebaktearat  dárbbašit  dađistaga  ee.  pro-</text>
                <text top="991" left="85" width="347" height="15" font="4">teiinnat,  ja  danne  váikkuha  smolden  čoavjjis  ahte</text>
                <text top="1009" left="85" width="347" height="15" font="4">boazu, mii lea jeagelguohtumis, deahkkehuvvá dálvet.</text>
                <text top="1026" left="85" width="347" height="15" font="4">Boazu deahkkehuvvagoahtá dakkaviđe go boahtá jea-</text>
                <text top="1043" left="85" width="347" height="15" font="4">gelguohtumii. Muhto bohccos lea sierralágan vuohki</text>
                <text top="1060" left="85" width="347" height="15" font="4">mainna easttada vai ii deahkkehuva, go boazu sáhttá</text>
                <text top="1078" left="85" width="347" height="15" font="4">“nuppádassii  geavahit”  nitrogena,  maid  eará  smire-</text>
                <text top="1095" left="85" width="129" height="15" font="4">zasti eallit eai sáhte.</text>
                <text top="198" left="478" width="330" height="15" font="4">Vaikko  boazu  deahkkehuvváge,  sáhttá  dat  liikká</text>
                <text top="215" left="461" width="347" height="15" font="4">lossut  dálvet,  jus  fal  lea  buorre  jeagelguohtun,  mas</text>
                <text top="232" left="461" width="347" height="15" font="4">boazu oažžu eambbo energiija go dat man loaktá. Dát</text>
                <text top="250" left="461" width="347" height="15" font="4">energiija jorrá buoidin gorudii ja čoggo dohko nu ahte</text>
                <text top="267" left="461" width="107" height="15" font="4">boazu ii geahpo.</text>
                <text top="284" left="478" width="330" height="15" font="4">Boazu guoira gal dábálaččat dálvvis. Rávis njiŋŋe-</text>
                <text top="301" left="461" width="347" height="15" font="4">las  geahppu  giđđii  15  %  čakčadeattu  ektui,  vaikko</text>
                <text top="319" left="461" width="347" height="15" font="4">leage čoavjjehin ja miessi deaddá 4-5 kg šattadettiin.</text>
                <text top="336" left="461" width="347" height="15" font="4">Sarvát  sáhttet  geahpput  30  %  čakčamánus  juovla-</text>
                <text top="353" left="461" width="347" height="15" font="4">mánnui. Dálvvi mielde gehppot bohccot dađistaga ja</text>
                <text top="370" left="461" width="347" height="15" font="4">erenoamáš heajos guohtumis sáhttet geahpput gitta 50</text>
                <text top="388" left="461" width="347" height="15" font="4">% rádjái. Jus guohtun hedjona nu sakka ahte čoavje-</text>
                <text top="405" left="461" width="347" height="15" font="4">liepma goiká, dehe nuppeládje dadjat ahte mikroorga-</text>
                <text top="422" left="461" width="347" height="15" font="4">nismmat  nohket,  nealgugoahtá  boazu.  Lassin  dasa</text>
                <text top="439" left="461" width="347" height="15" font="4">ahte boazu dárbbaša eallámuša (proteiinnaid ja mine-</text>
                <text top="457" left="461" width="347" height="15" font="4">rálaid),  gollada  boazu  deahkkemássa  ja  joraha  dán</text>
                <text top="474" left="461" width="347" height="15" font="4">energiijan. Guhkálmas nealgumiin ii nagat šat boazu</text>
                <text top="491" left="461" width="283" height="15" font="4">doalahit dábálaš gorutdoaimmaid ja jápmá.</text>
                <text top="508" left="478" width="330" height="15" font="4">Miesit  ja  boarrasit  varrásat  nelgot  bahábut  go</text>
                <text top="526" left="461" width="347" height="15" font="4">njiŋŋelasat ja čearpmahat. Sarvát rávžet ragatáiggi, ja</text>
                <text top="543" left="461" width="347" height="15" font="4">nuolppot  manahit  maiddái  bohccuidgaskasaš  árvo-</text>
                <text top="560" left="461" width="347" height="15" font="4">dási.  Nuolppot  eai  bálle  guohtut  ráfis,  dannego</text>
                <text top="577" left="461" width="347" height="15" font="4">njiŋŋelasat doroldahttet nulpobohccuid eret suvnnjiin.</text>
                <text top="595" left="461" width="347" height="15" font="4">Gehppes  miesit  sáhttet  nealgut.  Smávva  áldduin  leat</text>
                <text top="612" left="461" width="347" height="15" font="4">dávjá  gehppes  miesit,  mii  fas  dagaha  stuorit  miesse-</text>
                <text top="629" left="461" width="347" height="15" font="4">jámu. Heajos dálveguohtun dagaha fas áldduid mielk-</text>
                <text top="646" left="461" width="347" height="15" font="4">keheabbon  go  dábálaš  dan  vuosttaš  geasi,  ja  dat  fas</text>
                <text top="664" left="461" width="347" height="15" font="4">váikkuha ahte miesit leat geahppaseappot čakčat. Boa-</text>
                <text top="681" left="461" width="347" height="15" font="4">zomassimat, mat bohciidit fysiologalaš beliid sivas, eai</text>
                <text top="698" left="461" width="347" height="15" font="4">leat  nu  oidnosis  dannego  boraspirevahágat  lassánit</text>
                <text top="715" left="461" width="66" height="15" font="4">dađistaga.</text>
                <text top="733" left="478" width="330" height="15" font="4">Bohccuid  sáhttá  biebmat  fuođđariiguin  dálvet</text>
                <text top="750" left="461" width="347" height="15" font="4">heajos guohtumiid áigge, ja dustet váttisvuođa dáinna-</text>
                <text top="767" left="461" width="347" height="15" font="4">lágiin.  Guomočoavjji  mikrobat  dahket  almmatge</text>
                <text top="784" left="461" width="347" height="15" font="4">duššin dáid iešguđetlágan fuođđaršlájaid. Danne dárb-</text>
                <text top="802" left="461" width="347" height="15" font="4">bašit bohccot dagalduvvat fuođđariidda hui árrat, dan</text>
                <text top="819" left="461" width="347" height="15" font="4">bále go mikroorganismmat leat olleslogus čoavjjis ja</text>
                <text top="836" left="461" width="347" height="15" font="4">nákcejit smoldegoahtit ođđa fuođđariid. Eanas boazo-</text>
                <text top="853" left="461" width="347" height="15" font="4">eaiggádat eai almmatge biebmagoađe bohccuid áiggil,</text>
                <text top="871" left="461" width="347" height="15" font="4">muhto vurdet eaigo guohtumat buorrán. Doloža rájes</text>
                <text top="888" left="461" width="347" height="15" font="4">lei  vierrun  diktit  ealu  lávdat  jus  heajos  guohtumat</text>
                <text top="905" left="461" width="347" height="15" font="4">biste guhkit áiggi. Dalle boazu ieš ohcá guohtuma mii</text>
                <text top="922" left="461" width="58" height="15" font="4">gávdnoš.</text> <text top="940" left="478" width="330" height="15" font="4">Dálvet  guohtu  eallu  eanas  áigge,  lea  lodji,  iige</text>
                <text top="957" left="461" width="347" height="15" font="4">manat álššaid duššái. Lihkadeapmái adnojit álššat, ja</text>
                <text top="974" left="461" width="347" height="15" font="4">joavdelas  lihkahallan  dehe  lihkadeapmi  manaha</text>
                <text top="991" left="461" width="347" height="15" font="4">álššaid.  Lihkahallan  sáhttá  ovdamearkka  dihte  leat</text>
                <text top="1009" left="461" width="347" height="15" font="4">čohkkemat,  boraspiret  ja  mátkkošteaddjit  muose-</text>
                <text top="1026" left="461" width="347" height="15" font="4">huhttet ealu, dehe eallu ruvgala jna. Lassin dasa gask-</text>
                <text top="1043" left="461" width="347" height="15" font="4">kalduvvá  guohtumiin.  Álšamanaheami  ii  sáhte  šat</text>
                <text top="1060" left="461" width="347" height="15" font="4">buhttet maŋŋil eambbo guohtumiin. Danne geahppu</text>
                <text top="1078" left="461" width="347" height="15" font="4">boazu,  ja  jus  hui  hejot  manná,  sáhttet  váibbahat</text>
                <text top="1095" left="461" width="316" height="15" font="4">jápmit go oalát nohkkojit duksejuvvon buoiddis.</text>
                <text top="110" left="239" width="416" height="30" font="6"><b>1. Boazoguohtumat Skandinavias</b></text>
            </page>
        ''')  # nopep8

    def test_unordered_paragraphs(self):
        expected_page = etree.fromstring(u'''
            <body>
                <p>
                <em type="bold">1.1 Bohcco dárbbut</em>
                </p>
                <p>Miehtá  Davvikálohta  leat  asehis  guohtoneatnamat
                bohccuide. Boazu lea luonddudilálašvuođaid hálddus birra jagi.
                Guohtunšattut leat iešguđetláganat jagi ieš­guđetge áiggis, ja
                guohtundilli váikkuhage dasto man ollu boazu guohtu ja movt
                johtala. Dákko dáfus lea boazu  sierralágan  dilis,  Skandinávia
                eará  dábmojuv­von  elliid  suktii.  Go  mii  árvvoštállat
                guohtumiid, bidjat  bohcco  fysiologalaš  dárbbuid  vuođđun  ja
                makkár guohtuma boazu dárbbaša.</p>
                <p>
                <em type="italic">1.1.1 Fysiologalaš dárbbut</em>
                </p>
                <p>Boazu maiddái, nu movt earáge eallit, dárbbaša
                kar­bohydráhtaid ja buoiddi, maid joraha álšan ja doalaha goruda
                doaimmaid, oažžu lieggasa ja sáhttá lihkadit. Proteiinnat,
                vitamiinnat  ja  minerálat  adnojit  hukset dehkiid  ja  eará
                gorutgođđosiid,  ja  mielkki  buvtta­deapmái. Boazu lea, nu movt
                eará smirezasti eallit nai, ere­noamážit heivehuvvon smoldet
                guohtunšattuid. Alm­matge smoaldanit duššefal okta oasáš das maid
                boazu guohtu. Dakkár guohtunšattut mat smoaldanit geahp­pasit,
                leat  buorit  guohtun.  Ruonasšattut  smoaldanit álkimusat dalle
                go leat beallešattus ja smoaldaneapmi hedjona  dađi  mielde  go
                šattuid  šaddandássi  ovdána. Go biebmu smoaldahuvvá unnán, ii
                oaččo boazu nu ollu energiija dehe álšša. Maiddái biebmojohtin
                čoliid čađa mánná njozebut. Boazu lea mihá buorebut, go eará
                smirezasti eallit, heivehuvvon  smoldet  jeahkála.  Jeahkála
                smoalda­neapmi  lea  buorre  birra  jagi.  Dainna  lágiin  nagoda
                boazu  doalahit  buorren  obbalaš  biebmosmoldema, vaikko vel
                eará guohtun leage vánis ja maiddái kvali­tehta lea rievddalmas.
                Dađistaga go čavččabeallái hed­jona  ruonasšattuid
                smoaldaneapmi,  guohtugoahtá boazu  eambbo  jeahkála,  iige
                guođo  nu  ollu  ruonas­šattuid,  ja  nu  nagoda  almmatge
                doalahit  dássedis biebmosmoldema. Jeagil smoaldana geahppasit,
                muhto lea ovttagear­dánis fuođđar. Jeagelšlájain oažžu boazu nu
                ollu álšša (karbohydráhtaid)  ahte  ceavzá  badjel  dálvvi,
                muhto váilot  proteiinnat,  vitamiinnat  ja  minerálat.  Bohcco
                guomočoavjebaktearat  dárbbašit  dađistaga  ee.  pro­teiinnat,
                ja  danne  váikkuha  smolden  čoavjjis  ahte boazu, mii lea
                jeagelguohtumis, deahkkehuvvá dálvet. Boazu deahkkehuvvagoahtá
                dakkaviđe go boahtá jea­gelguohtumii. Muhto bohccos lea
                sierralágan vuohki mainna easttada vai ii deahkkehuva, go boazu
                sáhttá “nuppádassii  geavahit” nitrogena,  maid  eará
                smire­zasti eallit eai sáhte. Vaikko  boazu  deahkkehuvváge,
                sáhttá  dat  liikká lossut  dálvet,  jus  fal  lea  buorre
                jeagelguohtun,  mas boazu oažžu eambbo energiija go dat man
                loaktá. Dát energiija jorrá buoidin gorudii ja čoggo dohko nu
                ahte boazu ii geahpo. Boazu guoira gal dábálaččat dálvvis. Rávis
                njiŋŋe­las  geahppu  giđđii  15  %  čakčadeattu  ektui,  vaikko
                leage čoavjjehin ja miessi deaddá 4-5 kg šattadettiin. Sarvát
                sáhttet  geahpput  30  %  čakčamánus  juovla­mánnui. Dálvvi
                mielde gehppot bohccot dađistaga ja erenoamáš heajos guohtumis
                sáhttet geahpput gitta 50 % rádjái. Jus guohtun hedjona nu sakka ahte čoavje­liepma goiká, dehe nuppeládje dadjat ahte
                mikroorga­nismmat  nohket,  nealgugoahtá  boazu.  Lassin  dasa
                ahte boazu dárbbaša eallámuša (proteiinnaid ja mine­rálaid),
                gollada  boazu  deahkkemássa  ja  joraha  dán energiijan.
                Guhkálmas nealgumiin ii nagat šat boazu doalahit dábálaš
                gorutdoaimmaid ja jápmá. Miesit  ja  boarrasit  varrásat  nelgot
                bahábut  go njiŋŋelasat ja čearpmahat. Sarvát rávžet ragatáiggi,
                ja nuolppot  manahit  maiddái  bohccuidgaskasaš  árvo­dási.
                Nuolppot  eai  bálle  guohtut  ráfis,  dannego njiŋŋelasat
                doroldahttet nulpobohccuid eret suvnnjiin. Gehppes  miesit
                sáhttet  nealgut.  Smávva  áldduin  leat dávjá  gehppes  miesit,
                mii  fas  dagaha  stuorit  miesse­jámu. Heajos dálveguohtun
                dagaha fas áldduid mielk­keheabbon  go  dábálaš  dan  vuosttaš
                geasi,  ja  dat  fas váikkuha ahte miesit leat geahppaseappot
                čakčat. Boa­zomassimat, mat bohciidit fysiologalaš beliid sivas,
                eai leat  nu  oidnosis  dannego  boraspirevahágat  lassánit
                dađistaga. Bohccuid  sáhttá  biebmat  fuođđariiguin  dálvet
                heajos guohtumiid áigge, ja dustet váttisvuođa dáinna­lágiin.
                Guomočoavjji  mikrobat  dahket  almmatge duššin dáid
                iešguđetlágan fuođđaršlájaid. Danne dárb­bašit bohccot
                dagalduvvat fuođđariidda hui árrat, dan bále go mikroorganismmat
                leat olleslogus čoavjjis ja nákcejit smoldegoahtit ođđa
                fuođđariid. Eanas boazo­eaiggádat eai almmatge biebmagoađe
                bohccuid áiggil, muhto vurdet eaigo guohtumat buorrán. Doloža
                rájes lei  vierrun  diktit  ealu  lávdat  jus  heajos  guohtumat
                biste guhkit áiggi. Dalle boazu ieš ohcá guohtuma mii gávdnoš.
                Dálvet  guohtu  eallu  eanas  áigge,  lea  lodji,  iige manat
                álššaid duššái. Lihkadeapmái adnojit álššat, ja joavdelas
                lihkahallan  dehe  lihkadeapmi  manaha álššaid.  Lihkahallan
                sáhttá  ovdamearkka  dihte  leat čohkkemat,  boraspiret  ja
                mátkkošteaddjit  muose­huhttet ealu, dehe eallu ruvgala jna.
                Lassin dasa gask­kalduvvá  guohtumiin.  Álšamanaheami  ii  sáhte
                šat buhttet maŋŋil eambbo guohtumiin. Danne geahppu boazu,  ja
                jus  hui  hejot  manná,  sáhttet  váibbahat jápmit go oalát
                nohkkojit duksejuvvon buoiddis.</p>
                <p>
                <em type="bold">1. Boazoguohtumat Skandinavias</em>
                </p>
            </body>
        ''')  # nopep8

        pp = pdfconverter.PDFPage(self.start_page)
        pp.adjust_line_heights()
        pp.remove_elements_not_within_margin()
        pp.remove_footnotes_superscript()
        pp.merge_elements_on_same_line()
        pp.remove_invalid_elements()

        paragraphs = pp.make_unordered_paragraphs()

        extractor = pdfconverter.PDFTextExtractor()
        extractor.extract_text_from_page(paragraphs)
        self.assertXmlEqual(extractor.body,
                            expected_page)

    def test_make_ordered_sections(self):
        expected_page = etree.fromstring(u'''
            <body>
                <p>
                    <em type="bold">1. Boazoguohtumat Skandinavias</em>
                </p>
                <p>
                    <em type="bold">1.1 Bohcco dárbbut</em>
                </p>
                <p>Miehtá  Davvikálohta  leat  asehis  guohtoneatnamat
                bohccuide. Boazu lea luonddudilálašvuođaid hálddus birra jagi.
                Guohtunšattut leat iešguđetláganat jagi ieš­guđetge áiggis, ja
                guohtundilli váikkuhage dasto man ollu boazu guohtu ja movt
                johtala. Dákko dáfus lea boazu  sierralágan  dilis,  Skandinávia
                eará  dábmojuv­von  elliid  suktii.  Go  mii  árvvoštállat
                guohtumiid, bidjat  bohcco  fysiologalaš  dárbbuid  vuođđun  ja
                makkár guohtuma boazu dárbbaša.</p>
                <p>
                    <em type="italic">1.1.1 Fysiologalaš dárbbut</em>
                </p>
                <p>Boazu maiddái, nu movt earáge eallit, dárbbaša
                kar­bohydráhtaid ja buoiddi, maid joraha álšan ja doalaha goruda
                doaimmaid, oažžu lieggasa ja sáhttá lihkadit. Proteiinnat,
                vitamiinnat  ja  minerálat  adnojit  hukset dehkiid  ja  eará
                gorutgođđosiid,  ja  mielkki  buvtta­deapmái. Boazu lea, nu movt
                eará smirezasti eallit nai, ere­noamážit heivehuvvon smoldet
                guohtunšattuid. Alm­matge smoaldanit duššefal okta oasáš das maid
                boazu guohtu. Dakkár guohtunšattut mat smoaldanit geahp­pasit,
                leat  buorit  guohtun.  Ruonasšattut  smoaldanit álkimusat dalle
                go leat beallešattus ja smoaldaneapmi hedjona  dađi  mielde  go
                šattuid  šaddandássi  ovdána. Go biebmu smoaldahuvvá unnán, ii
                oaččo boazu nu ollu energiija dehe álšša. Maiddái biebmojohtin
                čoliid čađa mánná njozebut. Boazu lea mihá buorebut, go eará
                smirezasti eallit, heivehuvvon  smoldet  jeahkála.  Jeahkála
                smoalda­neapmi  lea  buorre  birra  jagi.  Dainna  lágiin  nagoda
                boazu  doalahit  buorren  obbalaš  biebmosmoldema, vaikko vel
                eará guohtun leage vánis ja maiddái kvali­tehta lea rievddalmas.
                Dađistaga go čavččabeallái hed­jona  ruonasšattuid
                smoaldaneapmi,  guohtugoahtá boazu  eambbo  jeahkála,  iige
                guođo  nu  ollu  ruonas­šattuid,  ja  nu  nagoda  almmatge
                doalahit  dássedis biebmosmoldema. Jeagil smoaldana geahppasit,
                muhto lea ovttagear­dánis fuođđar. Jeagelšlájain oažžu boazu nu
                ollu álšša (karbohydráhtaid)  ahte  ceavzá  badjel  dálvvi,
                muhto váilot  proteiinnat,  vitamiinnat  ja  minerálat.  Bohcco
                guomočoavjebaktearat  dárbbašit  dađistaga  ee.  pro­teiinnat,
                ja  danne  váikkuha  smolden  čoavjjis  ahte boazu, mii lea
                jeagelguohtumis, deahkkehuvvá dálvet. Boazu deahkkehuvvagoahtá
                dakkaviđe go boahtá jea­gelguohtumii. Muhto bohccos lea
                sierralágan vuohki mainna easttada vai ii deahkkehuva, go boazu
                sáhttá “nuppádassii  geavahit” nitrogena,  maid  eará
                smire­zasti eallit eai sáhte. Vaikko  boazu  deahkkehuvváge,
                sáhttá  dat  liikká lossut  dálvet,  jus  fal  lea  buorre
                jeagelguohtun,  mas boazu oažžu eambbo energiija go dat man
                loaktá. Dát energiija jorrá buoidin gorudii ja čoggo dohko nu
                ahte boazu ii geahpo. Boazu guoira gal dábálaččat dálvvis. Rávis
                njiŋŋe­las  geahppu  giđđii  15  %  čakčadeattu  ektui,  vaikko
                leage čoavjjehin ja miessi deaddá 4-5 kg šattadettiin. Sarvát
                sáhttet  geahpput  30  %  čakčamánus  juovla­mánnui. Dálvvi
                mielde gehppot bohccot dađistaga ja erenoamáš heajos guohtumis
                sáhttet geahpput gitta 50 % rádjái. Jus guohtun hedjona nu sakka
                ahte čoavje­liepma goiká, dehe nuppeládje dadjat ahte
                mikroorga­nismmat  nohket,  nealgugoahtá  boazu.  Lassin  dasa
                ahte boazu dárbbaša eallámuša (proteiinnaid ja mine­rálaid),
                gollada  boazu  deahkkemássa  ja  joraha  dán energiijan.
                Guhkálmas nealgumiin ii nagat šat boazu doalahit dábálaš
                gorutdoaimmaid ja jápmá. Miesit  ja  boarrasit  varrásat  nelgot
                bahábut  go njiŋŋelasat ja čearpmahat. Sarvát rávžet ragatáiggi,
                ja nuolppot  manahit  maiddái  bohccuidgaskasaš  árvo­dási.
                Nuolppot  eai  bálle  guohtut  ráfis,  dannego njiŋŋelasat
                doroldahttet nulpobohccuid eret suvnnjiin. Gehppes  miesit
                sáhttet  nealgut.  Smávva  áldduin  leat dávjá  gehppes  miesit,
                mii  fas  dagaha  stuorit  miesse­jámu. Heajos dálveguohtun
                dagaha fas áldduid mielk­keheabbon  go  dábálaš  dan  vuosttaš
                geasi,  ja  dat  fas váikkuha ahte miesit leat geahppaseappot
                čakčat. Boa­zomassimat, mat bohciidit fysiologalaš beliid sivas,
                eai leat  nu  oidnosis  dannego  boraspirevahágat  lassánit
                dađistaga. Bohccuid  sáhttá  biebmat  fuođđariiguin  dálvet
                heajos guohtumiid áigge, ja dustet váttisvuođa dáinna­lágiin.
                Guomočoavjji  mikrobat  dahket  almmatge duššin dáid
                iešguđetlágan fuođđaršlájaid. Danne dárb­bašit bohccot
                dagalduvvat fuođđariidda hui árrat, dan bále go mikroorganismmat
                leat olleslogus čoavjjis ja nákcejit smoldegoahtit ođđa
                fuođđariid. Eanas boazo­eaiggádat eai almmatge biebmagoađe
                bohccuid áiggil, muhto vurdet eaigo guohtumat buorrán. Doloža
                rájes lei  vierrun  diktit  ealu  lávdat  jus  heajos  guohtumat
                biste guhkit áiggi. Dalle boazu ieš ohcá guohtuma mii gávdnoš.
                Dálvet  guohtu  eallu  eanas  áigge,  lea  lodji,  iige manat
                álššaid duššái. Lihkadeapmái adnojit álššat, ja joavdelas
                lihkahallan  dehe  lihkadeapmi  manaha álššaid.  Lihkahallan
                sáhttá  ovdamearkka  dihte  leat čohkkemat,  boraspiret  ja
                mátkkošteaddjit  muose­huhttet ealu, dehe eallu ruvgala jna.
                Lassin dasa gask­kalduvvá  guohtumiin.  Álšamanaheami  ii  sáhte
                šat buhttet maŋŋil eambbo guohtumiin. Danne geahppu boazu,  ja
                jus  hui  hejot  manná,  sáhttet  váibbahat jápmit go oalát
                nohkkojit duksejuvvon buoiddis.</p>
            </body>
        ''')

        pp = pdfconverter.PDFPage(self.start_page)
        pp.adjust_line_heights()
        pp.remove_elements_not_within_margin()
        pp.remove_footnotes_superscript()
        pp.merge_elements_on_same_line()
        pp.remove_invalid_elements()

        extractor = pdfconverter.PDFTextExtractor()
        extractor.extract_text_from_page(pp.make_ordered_sections().paragraphs)
        self.assertXmlEqual(extractor.body,
                            expected_page)


class TestProblematicPageThreeColumns(xmltester.XMLTester):
    """This page has three columns, a couple of headings above them and a table

    Test that
    * unwanted parts of the document is removed
    * paragraphs are made correctly
    * the ordering of paragraphs is done correctly.
    """

    def setUp(self):
        self.start_page = etree.fromstring(u'''
            <page number="1" position="absolute" top="0" left="0" height="1262" width="892">
                <text top="298" left="51" width="234" height="19" font="0"><b>Dán giđa kártengeahččalemiid birra</b></text>
                <text top="316" left="51" width="194" height="18" font="1">2015 giđa galget skuvllat čađahit </text>
                <text top="334" left="51" width="246" height="18" font="1">geatnegahtton kártengeahččalemiid 1., 2. </text>
                <text top="352" left="51" width="240" height="18" font="1">ja 3. ceahkis. Oahpahusdirektoráhtta fállá </text>
                <text top="370" left="51" width="245" height="18" font="1">maid eaktodáhtolaš kártengeahččalemiid </text>
                <text top="388" left="51" width="225" height="18" font="1">1., 3. ja 4. ceahkis. 2015 giđa fállojuvvo  </text>
                <text top="406" left="51" width="218" height="18" font="1">vel lassin ođđa eaktodáhtolaš kárten- </text>
                <text top="424" left="51" width="248" height="18" font="1">geahččaleamit eŋgelasgielas 3. ceahkkái.    </text>
                <text top="460" left="51" width="242" height="19" font="0"><b>Geatnegahtton kártengeahččaleamit</b></text>
                <text top="478" left="51" width="245" height="18" font="1">Leat geatnegahtton kártengeahččaleamit:</text>
                <text top="496" left="51" width="163" height="18" font="1">• Lohkamis 1., 2. ja 3. ceahkis</text>
                <text top="514" left="51" width="153" height="18" font="1">• Rehkenastimis 2. ceahkis </text>
                <text top="550" left="51" width="193" height="18" font="1">Buot oahppit galget váldit daid </text>
                <text top="568" left="51" width="230" height="18" font="1">geatnegahtton kártengeahččalemiid. </text>
                <text top="586" left="51" width="214" height="18" font="1">Oahppit geat leat eret geahččalan- </text>
                <text top="604" left="51" width="228" height="18" font="1">beaivvi, galget čađahit geahččaleami </text>
                <text top="622" left="51" width="45" height="18" font="1">maŋŋil.</text>
                <text top="658" left="51" width="202" height="18" font="1">Kártengeahččalemiide leat sierra </text>
                <text top="676" left="51" width="225" height="18" font="1">luvvennjuolggadusat. Vaikko oahppi </text>
                <text top="694" left="51" width="241" height="18" font="1">deavddášii luvvema eavttuid, de sáhttá </text>
                <text top="712" left="51" width="241" height="18" font="1">oahppi ieš dahje su váhnemat dattetge </text>
                <text top="730" left="51" width="222" height="18" font="1">mearridit ahte oahppi galgá čađahit </text>
                <text top="748" left="51" width="88" height="18" font="1">geahččaleami.</text>
                <text top="784" left="51" width="236" height="19" font="0"><b>Eaktodáhtolaš kártengeahččaleamit</b></text>
                <text top="802" left="51" width="231" height="18" font="1">Geatnegahtton kártengeahččalemiide </text>
                <text top="820" left="51" width="206" height="18" font="1">lassin fállá Oahpahusdirektoráhtta </text>
                <text top="838" left="51" width="220" height="18" font="1">eaktodáhtolaš kártengeahččalemiid. </text>
                <text top="856" left="51" width="187" height="18" font="1">Jus skuvla dahje skuvlaeaiggát  </text>
                <text top="874" left="51" width="192" height="18" font="1">mearrida čađahit eaktodáhtolaš </text>
                <text top="892" left="51" width="224" height="18" font="1">kártengeahččalemiid, de fertejit buot </text>
                <text top="910" left="51" width="228" height="18" font="1">oahppit dan ceahkis masa dát guoská </text>
                <text top="928" left="51" width="122" height="18" font="1">váldit geahččaleami.</text>
                <text top="964" left="51" width="163" height="18" font="1">Fállojuvvojit eaktodáhtolaš </text>
                <text top="982" left="51" width="129" height="18" font="1">kártengeahččaleamit:</text>
                <text top="1000" left="51" width="185" height="18" font="1">• Rehkenastimis 1. ja 3. ceahkis</text>
                <text top="1018" left="51" width="152" height="18" font="1">• Eŋgelasgielas 3. ceahkis</text>
                <text top="1036" left="51" width="173" height="18" font="1">• Digitála gálggain 4. ceahkis</text>
                <text top="1072" left="51" width="177" height="19" font="0"><b>Dieđut geahččalemiid birra</b></text>
                <text top="1090" left="51" width="230" height="18" font="1">Kártengeahččalemiid galget skuvla ja </text>
                <text top="1108" left="51" width="245" height="18" font="1">oahpaheaddjit geavahit gávnnahit geat </text>
                <text top="1126" left="51" width="239" height="18" font="1">dárbbašit lasi čuovvoleami álgooahpa- </text>
                <text top="1144" left="51" width="216" height="18" font="1">husas. Eanaš oahppit máhttet buot </text>
                <text top="1162" left="51" width="246" height="18" font="1">hárjehusaid, ja máŋgasiid mielas ges lea </text>
                <text top="1180" left="51" width="238" height="18" font="1">geahččaleapmi álki. Geahččaleamit eai </text>
                <text top="298" left="322" width="216" height="18" font="1">muital olus ohppiid birra geain leat </text>
                <text top="316" left="322" width="91" height="18" font="1">buorit gálggat.</text>
                <text top="352" left="322" width="180" height="18" font="1">Kártengeahččaleamit eai leat </text>
                <text top="370" left="322" width="175" height="18" font="1">geahččaleamit fágas, muhto </text>
                <text top="388" left="322" width="182" height="18" font="1">vuođđogálggain fágaid rastá. </text>
                <text top="406" left="322" width="223" height="18" font="1">Oahppoplánain leat vuođđogálggat </text>
                <text top="424" left="322" width="114" height="18" font="1">definerejuvvon ná:</text>
                <text top="442" left="322" width="128" height="18" font="1">• njálmmálaš gálggat</text>
                <text top="460" left="322" width="94" height="18" font="1">• máhttit lohkat</text>
                <text top="478" left="322" width="84" height="18" font="1">• máhttit čállit</text>
                <text top="496" left="322" width="124" height="18" font="1">• máhttit rehkenastit</text>
                <text top="514" left="322" width="103" height="18" font="1">• digitála gálggat</text>
                <text top="550" left="322" width="213" height="18" font="1">Rehkenastinbihtáid ovdamearkkat </text>
                <text top="568" left="322" width="236" height="18" font="1">sáhttet leat lohkat, sirret loguid sturro- </text>
                <text top="586" left="322" width="218" height="18" font="1">dagaid mielde, loahpahit lohkogur- </text>
                <text top="604" left="322" width="210" height="18" font="1">gadasaid ja rehkenastit plussain ja </text>
                <text top="622" left="322" width="225" height="18" font="1">minusiin. Lohkamis sáhttá leat sáhka </text>
                <text top="640" left="322" width="235" height="18" font="1">ovdamearkka dihtii bustávaid čállimis, </text>
                <text top="658" left="322" width="237" height="18" font="1">sániid lohkamis ja cealkagiid lohkamis. </text>
                <text top="676" left="322" width="239" height="18" font="1">Guovddážis digitála gálggaid geahčča- </text>
                <text top="694" left="322" width="237" height="18" font="1">leami bihtáin lea háhkat ja meannudit, </text>
                <text top="712" left="322" width="249" height="18" font="1">buvttadit ja divodit, gulahallat ja digitála </text>
                <text top="730" left="322" width="202" height="18" font="1">árvvoštallannávccat. Guovddážis </text>
                <text top="748" left="322" width="241" height="18" font="1">eŋgelasgiellageahččaleamis lea dovdat </text>
                <text top="766" left="322" width="247" height="18" font="1">ja ipmirdit oahpes ja beaivválaš sániid ja </text>
                <text top="784" left="322" width="208" height="18" font="1">dajaldagaid, njálmmálaččat dahje </text>
                <text top="802" left="322" width="233" height="18" font="1">čálalaččat. Geahččaleamis leat guokte </text>
                <text top="820" left="322" width="209" height="18" font="1">oasi, guldalanoassi ja lohkanoassi. </text>
                <text top="838" left="322" width="212" height="18" font="1">Ohppiin ferte leat oaivetelefovdna </text>
                <text top="856" left="322" width="93" height="18" font="1">guldalanoasis.  </text>
                <text top="298" left="593" width="170" height="19" font="0"><b>Bohtosat ja čuovvoleapmi</b></text>
                <text top="316" left="593" width="249" height="18" font="1">Kártengeahččalemiid bohtosiid ii galgga </text>
                <text top="334" left="593" width="248" height="18" font="1">rapporteret Oahpahusdirektoráhttii ii ge </text>
                <text top="352" left="593" width="207" height="18" font="1">geavahit buohtastahttit skuvllaid, </text>
                <text top="370" left="593" width="149" height="18" font="1">gielddaid dahje fylkkaid.</text>
                <text top="406" left="593" width="241" height="18" font="1">Bohtosiid galgá vuosttažettiin geavahit </text>
                <text top="424" left="593" width="197" height="18" font="1">siskkáldasat skuvllas láhčin dihti </text>
                <text top="442" left="593" width="208" height="18" font="1">oahpahusa nu, ahte oahppit, geat </text>
                <text top="460" left="593" width="252" height="18" font="1">dárbbašit dan, ožžot lassi bagadallama ja </text>
                <text top="478" left="593" width="230" height="18" font="1">doarjaga. Oahpaheddjiide leat ráhka- </text>
                <text top="496" left="593" width="211" height="18" font="1">duvvon bagadallanmateriálat mat </text>
                <text top="514" left="593" width="225" height="18" font="1">čilgehit mo geahččalemiid bohtosiid </text>
                <text top="532" left="593" width="100" height="18" font="1">sáhttá čuovvolit.</text>
                <text top="568" left="593" width="225" height="18" font="1">Jus čađaheami bohtosat čájehit ahte </text>
                <text top="586" left="593" width="242" height="18" font="1">oahppis lea dárbu lassi čuovvoleapmái, </text>
                <text top="604" left="593" width="190" height="18" font="1">de galgá váhnemiidda dieđihit </text>
                <text top="622" left="593" width="226" height="18" font="1">geahččalanbohtosiid birra ja muitalit </text>
                <text top="640" left="593" width="213" height="18" font="1">makkár doaimmaid áigot álggahit. </text>
                <text top="658" left="593" width="217" height="18" font="1">Váhnemat sáhttet váldit oktavuođa </text>
                <text top="676" left="593" width="186" height="18" font="1">skuvllain jus ležžet gažaldagat.</text>
                <text top="712" left="593" width="84" height="19" font="0"><b>Eanet dieđut</b></text>
                <text top="730" left="593" width="244" height="18" font="1">Eanet dieđut kártengeahččalemiid birra </text>
                <text top="748" left="593" width="80" height="18" font="1">leat dáppe:    </text>
                <text top="766" left="593" width="189" height="18" font="2">http://www.udir.no/Vurdering/</text>
                <text top="784" left="593" width="96" height="18" font="2">Kartlegging-gs/</text>
                <text top="820" left="593" width="230" height="18" font="1">Máhttoloktema oahppoplánabuvttus </text>
                <text top="838" left="593" width="69" height="18" font="1">lea dáppe:  </text>
                <text top="856" left="593" width="193" height="18" font="2">http://www.udir.no/Lareplaner/</text>
                <text top="874" left="593" width="104" height="18" font="2">Kunnskapsloftet/</text>
                <text top="209" left="147" width="605" height="39" font="3"><b>Diehtu 2015 giđa kártengeahččalemiid birra</b></text>
                <text top="262" left="306" width="286" height="19" font="4"><b>Váhnemiidda geain leat mánát 1.- 4. ceahkis</b></text>
                <text top="967" left="443" width="281" height="19" font="0"><b>2015 giđa kártengeahččalemiid bajilgovva </b></text>
                <text top="1006" left="326" width="41" height="15" font="5"><b>Ceahkki</b></text>
                <text top="1006" left="390" width="78" height="15" font="5"><b>Geahččaleapmi</b></text>
                <text top="999" left="577" width="82" height="15" font="5"><b>Geatnegahtton/</b></text>
                <text top="1013" left="577" width="73" height="15" font="5"><b>eaktodáhtolaš</b></text>
                <text top="1006" left="718" width="26" height="15" font="5"><b>Goas</b></text>
                <text top="1035" left="326" width="48" height="14" font="6">1. ceahkki</text>
                <text top="1035" left="390" width="36" height="14" font="6">Lohkan</text>
                <text top="1035" left="577" width="75" height="14" font="6">Geatnegahtton</text>
                <text top="1035" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1056" left="326" width="48" height="14" font="6">2. ceahkki</text>
                <text top="1056" left="390" width="36" height="14" font="6">Lohkan</text>
                <text top="1056" left="577" width="75" height="14" font="6">Geatnegahtton</text>
                <text top="1056" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1077" left="326" width="48" height="14" font="6">3. ceahkki</text>
                <text top="1077" left="390" width="36" height="14" font="6">Lohkan</text>
                <text top="1077" left="577" width="75" height="14" font="6">Geatnegahtton</text>
                <text top="1077" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1098" left="326" width="48" height="14" font="6">1. ceahkki</text>
                <text top="1098" left="390" width="60" height="14" font="6">Rehkenastin</text>
                <text top="1098" left="577" width="69" height="14" font="6">Eaktodáhtolaš</text>
                <text top="1098" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1119" left="326" width="48" height="14" font="6">2. ceahkki</text>
                <text top="1119" left="390" width="60" height="14" font="6">Rehkenastin</text>
                <text top="1119" left="577" width="75" height="14" font="6">Geatnegahtton</text>
                <text top="1119" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1140" left="326" width="48" height="14" font="6">3. ceahkki</text>
                <text top="1140" left="390" width="60" height="14" font="6">Rehkenastin</text>
                <text top="1140" left="577" width="69" height="14" font="6">Eaktodáhtolaš</text>
                <text top="1140" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1161" left="326" width="48" height="14" font="6">3. ceahkki</text>
                <text top="1161" left="390" width="160" height="14" font="6">Eŋgelasgiella (elektrovnnalaččat)</text>
                <text top="1161" left="577" width="69" height="14" font="6">Eaktodáhtolaš</text>
                <text top="1161" left="718" width="115" height="14" font="6">njukčamánu 2.b. - 20. b.</text>
                <text top="1182" left="326" width="48" height="14" font="6">4. ceahkki</text>
                <text top="1182" left="390" width="256" height="14" font="6">Digitála gálggat (elektrovnnalaččat) Eaktodáhtolaš</text>
                <text top="1182" left="718" width="115" height="14" font="6">njukčamánu 2.b. - 20. b.</text>
                <text top="143" left="398" width="97" height="18" font="0"><b>Davvisámegillii</b></text>
            </page>
        ''')  # nopep8

    def test_adjust_line_heights(self):
        adjusted_page = etree.fromstring(u'''
            <page number="1" position="absolute" top="0" left="0" height="1262" width="892">
                <text top="298" left="51" width="234" height="18" font="0"><b>Dán giđa kártengeahččalemiid birra</b></text>
                <text top="316" left="51" width="194" height="18" font="1">2015 giđa galget skuvllat čađahit </text>
                <text top="334" left="51" width="246" height="18" font="1">geatnegahtton kártengeahččalemiid 1., 2. </text>
                <text top="352" left="51" width="240" height="18" font="1">ja 3. ceahkis. Oahpahusdirektoráhtta fállá </text>
                <text top="370" left="51" width="245" height="18" font="1">maid eaktodáhtolaš kártengeahččalemiid </text>
                <text top="388" left="51" width="225" height="18" font="1">1., 3. ja 4. ceahkis. 2015 giđa fállojuvvo  </text>
                <text top="406" left="51" width="218" height="18" font="1">vel lassin ođđa eaktodáhtolaš kárten- </text>
                <text top="424" left="51" width="248" height="18" font="1">geahččaleamit eŋgelasgielas 3. ceahkkái.    </text>
                <text top="460" left="51" width="242" height="18" font="0"><b>Geatnegahtton kártengeahččaleamit</b></text>
                <text top="478" left="51" width="245" height="18" font="1">Leat geatnegahtton kártengeahččaleamit:</text>
                <text top="496" left="51" width="163" height="18" font="1">• Lohkamis 1., 2. ja 3. ceahkis</text>
                <text top="514" left="51" width="153" height="18" font="1">• Rehkenastimis 2. ceahkis </text>
                <text top="550" left="51" width="193" height="18" font="1">Buot oahppit galget váldit daid </text>
                <text top="568" left="51" width="230" height="18" font="1">geatnegahtton kártengeahččalemiid. </text>
                <text top="586" left="51" width="214" height="18" font="1">Oahppit geat leat eret geahččalan- </text>
                <text top="604" left="51" width="228" height="18" font="1">beaivvi, galget čađahit geahččaleami </text>
                <text top="622" left="51" width="45" height="18" font="1">maŋŋil.</text>
                <text top="658" left="51" width="202" height="18" font="1">Kártengeahččalemiide leat sierra </text>
                <text top="676" left="51" width="225" height="18" font="1">luvvennjuolggadusat. Vaikko oahppi </text>
                <text top="694" left="51" width="241" height="18" font="1">deavddášii luvvema eavttuid, de sáhttá </text>
                <text top="712" left="51" width="241" height="18" font="1">oahppi ieš dahje su váhnemat dattetge </text>
                <text top="730" left="51" width="222" height="18" font="1">mearridit ahte oahppi galgá čađahit </text>
                <text top="748" left="51" width="88" height="18" font="1">geahččaleami.</text>
                <text top="784" left="51" width="236" height="18" font="0"><b>Eaktodáhtolaš kártengeahččaleamit</b></text>
                <text top="802" left="51" width="231" height="18" font="1">Geatnegahtton kártengeahččalemiide </text>
                <text top="820" left="51" width="206" height="18" font="1">lassin fállá Oahpahusdirektoráhtta </text>
                <text top="838" left="51" width="220" height="18" font="1">eaktodáhtolaš kártengeahččalemiid. </text>
                <text top="856" left="51" width="187" height="18" font="1">Jus skuvla dahje skuvlaeaiggát  </text>
                <text top="874" left="51" width="192" height="18" font="1">mearrida čađahit eaktodáhtolaš </text>
                <text top="892" left="51" width="224" height="18" font="1">kártengeahččalemiid, de fertejit buot </text>
                <text top="910" left="51" width="228" height="18" font="1">oahppit dan ceahkis masa dát guoská </text>
                <text top="928" left="51" width="122" height="18" font="1">váldit geahččaleami.</text>
                <text top="964" left="51" width="163" height="18" font="1">Fállojuvvojit eaktodáhtolaš </text>
                <text top="982" left="51" width="129" height="18" font="1">kártengeahččaleamit:</text>
                <text top="1000" left="51" width="185" height="18" font="1">• Rehkenastimis 1. ja 3. ceahkis</text>
                <text top="1018" left="51" width="152" height="18" font="1">• Eŋgelasgielas 3. ceahkis</text>
                <text top="1036" left="51" width="173" height="18" font="1">• Digitála gálggain 4. ceahkis</text>
                <text top="1072" left="51" width="177" height="18" font="0"><b>Dieđut geahččalemiid birra</b></text>
                <text top="1090" left="51" width="230" height="18" font="1">Kártengeahččalemiid galget skuvla ja </text>
                <text top="1108" left="51" width="245" height="18" font="1">oahpaheaddjit geavahit gávnnahit geat </text>
                <text top="1126" left="51" width="239" height="18" font="1">dárbbašit lasi čuovvoleami álgooahpa- </text>
                <text top="1144" left="51" width="216" height="18" font="1">husas. Eanaš oahppit máhttet buot </text>
                <text top="1162" left="51" width="246" height="18" font="1">hárjehusaid, ja máŋgasiid mielas ges lea </text>
                <text top="1180" left="51" width="238" height="18" font="1">geahččaleapmi álki. Geahččaleamit eai </text>
                <text top="298" left="322" width="216" height="18" font="1">muital olus ohppiid birra geain leat </text>
                <text top="316" left="322" width="91" height="18" font="1">buorit gálggat.</text>
                <text top="352" left="322" width="180" height="18" font="1">Kártengeahččaleamit eai leat </text>
                <text top="370" left="322" width="175" height="18" font="1">geahččaleamit fágas, muhto </text>
                <text top="388" left="322" width="182" height="18" font="1">vuođđogálggain fágaid rastá. </text>
                <text top="406" left="322" width="223" height="18" font="1">Oahppoplánain leat vuođđogálggat </text>
                <text top="424" left="322" width="114" height="18" font="1">definerejuvvon ná:</text>
                <text top="442" left="322" width="128" height="18" font="1">• njálmmálaš gálggat</text>
                <text top="460" left="322" width="94" height="18" font="1">• máhttit lohkat</text>
                <text top="478" left="322" width="84" height="18" font="1">• máhttit čállit</text>
                <text top="496" left="322" width="124" height="18" font="1">• máhttit rehkenastit</text>
                <text top="514" left="322" width="103" height="18" font="1">• digitála gálggat</text>
                <text top="550" left="322" width="213" height="18" font="1">Rehkenastinbihtáid ovdamearkkat </text>
                <text top="568" left="322" width="236" height="18" font="1">sáhttet leat lohkat, sirret loguid sturro- </text>
                <text top="586" left="322" width="218" height="18" font="1">dagaid mielde, loahpahit lohkogur- </text>
                <text top="604" left="322" width="210" height="18" font="1">gadasaid ja rehkenastit plussain ja </text>
                <text top="622" left="322" width="225" height="18" font="1">minusiin. Lohkamis sáhttá leat sáhka </text>
                <text top="640" left="322" width="235" height="18" font="1">ovdamearkka dihtii bustávaid čállimis, </text>
                <text top="658" left="322" width="237" height="18" font="1">sániid lohkamis ja cealkagiid lohkamis. </text>
                <text top="676" left="322" width="239" height="18" font="1">Guovddážis digitála gálggaid geahčča- </text>
                <text top="694" left="322" width="237" height="18" font="1">leami bihtáin lea háhkat ja meannudit, </text>
                <text top="712" left="322" width="249" height="18" font="1">buvttadit ja divodit, gulahallat ja digitála </text>
                <text top="730" left="322" width="202" height="18" font="1">árvvoštallannávccat. Guovddážis </text>
                <text top="748" left="322" width="241" height="18" font="1">eŋgelasgiellageahččaleamis lea dovdat </text>
                <text top="766" left="322" width="247" height="18" font="1">ja ipmirdit oahpes ja beaivválaš sániid ja </text>
                <text top="784" left="322" width="208" height="18" font="1">dajaldagaid, njálmmálaččat dahje </text>
                <text top="802" left="322" width="233" height="18" font="1">čálalaččat. Geahččaleamis leat guokte </text>
                <text top="820" left="322" width="209" height="18" font="1">oasi, guldalanoassi ja lohkanoassi. </text>
                <text top="838" left="322" width="212" height="18" font="1">Ohppiin ferte leat oaivetelefovdna </text>
                <text top="856" left="322" width="93" height="18" font="1">guldalanoasis.  </text>
                <text top="298" left="593" width="170" height="18" font="0"><b>Bohtosat ja čuovvoleapmi</b></text>
                <text top="316" left="593" width="249" height="18" font="1">Kártengeahččalemiid bohtosiid ii galgga </text>
                <text top="334" left="593" width="248" height="18" font="1">rapporteret Oahpahusdirektoráhttii ii ge </text>
                <text top="352" left="593" width="207" height="18" font="1">geavahit buohtastahttit skuvllaid, </text>
                <text top="370" left="593" width="149" height="18" font="1">gielddaid dahje fylkkaid.</text>
                <text top="406" left="593" width="241" height="18" font="1">Bohtosiid galgá vuosttažettiin geavahit </text>
                <text top="424" left="593" width="197" height="18" font="1">siskkáldasat skuvllas láhčin dihti </text>
                <text top="442" left="593" width="208" height="18" font="1">oahpahusa nu, ahte oahppit, geat </text>
                <text top="460" left="593" width="252" height="18" font="1">dárbbašit dan, ožžot lassi bagadallama ja </text>
                <text top="478" left="593" width="230" height="18" font="1">doarjaga. Oahpaheddjiide leat ráhka- </text>
                <text top="496" left="593" width="211" height="18" font="1">duvvon bagadallanmateriálat mat </text>
                <text top="514" left="593" width="225" height="18" font="1">čilgehit mo geahččalemiid bohtosiid </text>
                <text top="532" left="593" width="100" height="18" font="1">sáhttá čuovvolit.</text>
                <text top="568" left="593" width="225" height="18" font="1">Jus čađaheami bohtosat čájehit ahte </text>
                <text top="586" left="593" width="242" height="18" font="1">oahppis lea dárbu lassi čuovvoleapmái, </text>
                <text top="604" left="593" width="190" height="18" font="1">de galgá váhnemiidda dieđihit </text>
                <text top="622" left="593" width="226" height="18" font="1">geahččalanbohtosiid birra ja muitalit </text>
                <text top="640" left="593" width="213" height="18" font="1">makkár doaimmaid áigot álggahit. </text>
                <text top="658" left="593" width="217" height="18" font="1">Váhnemat sáhttet váldit oktavuođa </text>
                <text top="676" left="593" width="186" height="18" font="1">skuvllain jus ležžet gažaldagat.</text>
                <text top="712" left="593" width="84" height="18" font="0"><b>Eanet dieđut</b></text>
                <text top="730" left="593" width="244" height="18" font="1">Eanet dieđut kártengeahččalemiid birra </text>
                <text top="748" left="593" width="80" height="18" font="1">leat dáppe:    </text>
                <text top="766" left="593" width="189" height="18" font="2">http://www.udir.no/Vurdering/</text>
                <text top="784" left="593" width="96" height="18" font="2">Kartlegging-gs/</text>
                <text top="820" left="593" width="230" height="18" font="1">Máhttoloktema oahppoplánabuvttus </text>
                <text top="838" left="593" width="69" height="18" font="1">lea dáppe:  </text>
                <text top="856" left="593" width="193" height="18" font="2">http://www.udir.no/Lareplaner/</text>
                <text top="874" left="593" width="104" height="18" font="2">Kunnskapsloftet/</text>
                <text top="209" left="147" width="605" height="39" font="3"><b>Diehtu 2015 giđa kártengeahččalemiid birra</b></text>
                <text top="262" left="306" width="286" height="19" font="4"><b>Váhnemiidda geain leat mánát 1.- 4. ceahkis</b></text>
                <text top="967" left="443" width="281" height="19" font="0"><b>2015 giđa kártengeahččalemiid bajilgovva </b></text>
                <text top="1006" left="326" width="41" height="15" font="5"><b>Ceahkki</b></text>
                <text top="1006" left="390" width="78" height="15" font="5"><b>Geahččaleapmi</b></text>
                <text top="999" left="577" width="82" height="14" font="5"><b>Geatnegahtton/</b></text>
                <text top="1013" left="577" width="73" height="15" font="5"><b>eaktodáhtolaš</b></text>
                <text top="1006" left="718" width="26" height="15" font="5"><b>Goas</b></text>
                <text top="1035" left="326" width="48" height="14" font="6">1. ceahkki</text>
                <text top="1035" left="390" width="36" height="14" font="6">Lohkan</text>
                <text top="1035" left="577" width="75" height="14" font="6">Geatnegahtton</text>
                <text top="1035" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1056" left="326" width="48" height="14" font="6">2. ceahkki</text>
                <text top="1056" left="390" width="36" height="14" font="6">Lohkan</text>
                <text top="1056" left="577" width="75" height="14" font="6">Geatnegahtton</text>
                <text top="1056" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1077" left="326" width="48" height="14" font="6">3. ceahkki</text>
                <text top="1077" left="390" width="36" height="14" font="6">Lohkan</text>
                <text top="1077" left="577" width="75" height="14" font="6">Geatnegahtton</text>
                <text top="1077" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1098" left="326" width="48" height="14" font="6">1. ceahkki</text>
                <text top="1098" left="390" width="60" height="14" font="6">Rehkenastin</text>
                <text top="1098" left="577" width="69" height="14" font="6">Eaktodáhtolaš</text>
                <text top="1098" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1119" left="326" width="48" height="14" font="6">2. ceahkki</text>
                <text top="1119" left="390" width="60" height="14" font="6">Rehkenastin</text>
                <text top="1119" left="577" width="75" height="14" font="6">Geatnegahtton</text>
                <text top="1119" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1140" left="326" width="48" height="14" font="6">3. ceahkki</text>
                <text top="1140" left="390" width="60" height="14" font="6">Rehkenastin</text>
                <text top="1140" left="577" width="69" height="14" font="6">Eaktodáhtolaš</text>
                <text top="1140" left="718" width="117" height="14" font="6">cuoŋománu 13.b. - 30.b.</text>
                <text top="1161" left="326" width="48" height="14" font="6">3. ceahkki</text>
                <text top="1161" left="390" width="160" height="14" font="6">Eŋgelasgiella (elektrovnnalaččat)</text>
                <text top="1161" left="577" width="69" height="14" font="6">Eaktodáhtolaš</text>
                <text top="1161" left="718" width="115" height="14" font="6">njukčamánu 2.b. - 20. b.</text>
                <text top="1182" left="326" width="48" height="14" font="6">4. ceahkki</text>
                <text top="1182" left="390" width="256" height="14" font="6">Digitála gálggat (elektrovnnalaččat) Eaktodáhtolaš</text>
                <text top="1182" left="718" width="115" height="14" font="6">njukčamánu 2.b. - 20. b.</text>
                <text top="143" left="398" width="97" height="18" font="0"><b>Davvisámegillii</b></text>
            </page>
        ''')  # nopep8

        pp = pdfconverter.PDFPage(self.start_page)
        pp.adjust_line_heights()
        expected_page = etree.fromstring(
            '<page number="1" position="absolute" top="0" left="0" '
            'height="1262" width="892"/>')
        for pdftextelement in pp.textelements:
            expected_page.append(pdftextelement.t)

        self.assertXmlEqual(expected_page,
                            adjusted_page)

    def test_not_within_margin_page(self):
        not_within_margin_page = etree.fromstring(u'''
            <page number="1" position="absolute" top="0" left="0" height="1262" width="892">
                <text top="298" left="51" width="234" height="18" font="0"><b>Dán giđa kártengeahččalemiid birra</b></text>
                <text top="316" left="51" width="194" height="18" font="1">2015 giđa galget skuvllat čađahit </text>
                <text top="334" left="51" width="246" height="18" font="1">geatnegahtton kártengeahččalemiid 1., 2. </text>
                <text top="352" left="51" width="240" height="18" font="1">ja 3. ceahkis. Oahpahusdirektoráhtta fállá </text>
                <text top="370" left="51" width="245" height="18" font="1">maid eaktodáhtolaš kártengeahččalemiid </text>
                <text top="388" left="51" width="225" height="18" font="1">1., 3. ja 4. ceahkis. 2015 giđa fállojuvvo  </text>
                <text top="406" left="51" width="218" height="18" font="1">vel lassin ođđa eaktodáhtolaš kárten- </text>
                <text top="424" left="51" width="248" height="18" font="1">geahččaleamit eŋgelasgielas 3. ceahkkái.    </text>
                <text top="460" left="51" width="242" height="18" font="0"><b>Geatnegahtton kártengeahččaleamit</b></text>
                <text top="478" left="51" width="245" height="18" font="1">Leat geatnegahtton kártengeahččaleamit:</text>
                <text top="496" left="51" width="163" height="18" font="1">• Lohkamis 1., 2. ja 3. ceahkis</text>
                <text top="514" left="51" width="153" height="18" font="1">• Rehkenastimis 2. ceahkis </text>
                <text top="550" left="51" width="193" height="18" font="1">Buot oahppit galget váldit daid </text>
                <text top="568" left="51" width="230" height="18" font="1">geatnegahtton kártengeahččalemiid. </text>
                <text top="586" left="51" width="214" height="18" font="1">Oahppit geat leat eret geahččalan- </text>
                <text top="604" left="51" width="228" height="18" font="1">beaivvi, galget čađahit geahččaleami </text>
                <text top="622" left="51" width="45" height="18" font="1">maŋŋil.</text>
                <text top="658" left="51" width="202" height="18" font="1">Kártengeahččalemiide leat sierra </text>
                <text top="676" left="51" width="225" height="18" font="1">luvvennjuolggadusat. Vaikko oahppi </text>
                <text top="694" left="51" width="241" height="18" font="1">deavddášii luvvema eavttuid, de sáhttá </text>
                <text top="712" left="51" width="241" height="18" font="1">oahppi ieš dahje su váhnemat dattetge </text>
                <text top="730" left="51" width="222" height="18" font="1">mearridit ahte oahppi galgá čađahit </text>
                <text top="748" left="51" width="88" height="18" font="1">geahččaleami.</text>
                <text top="784" left="51" width="236" height="18" font="0"><b>Eaktodáhtolaš kártengeahččaleamit</b></text>
                <text top="802" left="51" width="231" height="18" font="1">Geatnegahtton kártengeahččalemiide </text>
                <text top="820" left="51" width="206" height="18" font="1">lassin fállá Oahpahusdirektoráhtta </text>
                <text top="838" left="51" width="220" height="18" font="1">eaktodáhtolaš kártengeahččalemiid. </text>
                <text top="856" left="51" width="187" height="18" font="1">Jus skuvla dahje skuvlaeaiggát  </text>
                <text top="874" left="51" width="192" height="18" font="1">mearrida čađahit eaktodáhtolaš </text>
                <text top="892" left="51" width="224" height="18" font="1">kártengeahččalemiid, de fertejit buot </text>
                <text top="910" left="51" width="228" height="18" font="1">oahppit dan ceahkis masa dát guoská </text>
                <text top="928" left="51" width="122" height="18" font="1">váldit geahččaleami.</text>
                <text top="964" left="51" width="163" height="18" font="1">Fállojuvvojit eaktodáhtolaš </text>
                <text top="982" left="51" width="129" height="18" font="1">kártengeahččaleamit:</text>
                <text top="1000" left="51" width="185" height="18" font="1">• Rehkenastimis 1. ja 3. ceahkis</text>
                <text top="1018" left="51" width="152" height="18" font="1">• Eŋgelasgielas 3. ceahkis</text>
                <text top="1036" left="51" width="173" height="18" font="1">• Digitála gálggain 4. ceahkis</text>
                <text top="1072" left="51" width="177" height="18" font="0"><b>Dieđut geahččalemiid birra</b></text>
                <text top="1090" left="51" width="230" height="18" font="1">Kártengeahččalemiid galget skuvla ja </text>
                <text top="1108" left="51" width="245" height="18" font="1">oahpaheaddjit geavahit gávnnahit geat </text>
                <text top="1126" left="51" width="239" height="18" font="1">dárbbašit lasi čuovvoleami álgooahpa- </text>
                <text top="1144" left="51" width="216" height="18" font="1">husas. Eanaš oahppit máhttet buot </text>
                <text top="1162" left="51" width="246" height="18" font="1">hárjehusaid, ja máŋgasiid mielas ges lea </text>
                <text top="1180" left="51" width="238" height="18" font="1">geahččaleapmi álki. Geahččaleamit eai </text>
                <text top="298" left="322" width="216" height="18" font="1">muital olus ohppiid birra geain leat </text>
                <text top="316" left="322" width="91" height="18" font="1">buorit gálggat.</text>
                <text top="352" left="322" width="180" height="18" font="1">Kártengeahččaleamit eai leat </text>
                <text top="370" left="322" width="175" height="18" font="1">geahččaleamit fágas, muhto </text>
                <text top="388" left="322" width="182" height="18" font="1">vuođđogálggain fágaid rastá. </text>
                <text top="406" left="322" width="223" height="18" font="1">Oahppoplánain leat vuođđogálggat </text>
                <text top="424" left="322" width="114" height="18" font="1">definerejuvvon ná:</text>
                <text top="442" left="322" width="128" height="18" font="1">• njálmmálaš gálggat</text>
                <text top="460" left="322" width="94" height="18" font="1">• máhttit lohkat</text>
                <text top="478" left="322" width="84" height="18" font="1">• máhttit čállit</text>
                <text top="496" left="322" width="124" height="18" font="1">• máhttit rehkenastit</text>
                <text top="514" left="322" width="103" height="18" font="1">• digitála gálggat</text>
                <text top="550" left="322" width="213" height="18" font="1">Rehkenastinbihtáid ovdamearkkat </text>
                <text top="568" left="322" width="236" height="18" font="1">sáhttet leat lohkat, sirret loguid sturro- </text>
                <text top="586" left="322" width="218" height="18" font="1">dagaid mielde, loahpahit lohkogur- </text>
                <text top="604" left="322" width="210" height="18" font="1">gadasaid ja rehkenastit plussain ja </text>
                <text top="622" left="322" width="225" height="18" font="1">minusiin. Lohkamis sáhttá leat sáhka </text>
                <text top="640" left="322" width="235" height="18" font="1">ovdamearkka dihtii bustávaid čállimis, </text>
                <text top="658" left="322" width="237" height="18" font="1">sániid lohkamis ja cealkagiid lohkamis. </text>
                <text top="676" left="322" width="239" height="18" font="1">Guovddážis digitála gálggaid geahčča- </text>
                <text top="694" left="322" width="237" height="18" font="1">leami bihtáin lea háhkat ja meannudit, </text>
                <text top="712" left="322" width="249" height="18" font="1">buvttadit ja divodit, gulahallat ja digitála </text>
                <text top="730" left="322" width="202" height="18" font="1">árvvoštallannávccat. Guovddážis </text>
                <text top="748" left="322" width="241" height="18" font="1">eŋgelasgiellageahččaleamis lea dovdat </text>
                <text top="766" left="322" width="247" height="18" font="1">ja ipmirdit oahpes ja beaivválaš sániid ja </text>
                <text top="784" left="322" width="208" height="18" font="1">dajaldagaid, njálmmálaččat dahje </text>
                <text top="802" left="322" width="233" height="18" font="1">čálalaččat. Geahččaleamis leat guokte </text>
                <text top="820" left="322" width="209" height="18" font="1">oasi, guldalanoassi ja lohkanoassi. </text>
                <text top="838" left="322" width="212" height="18" font="1">Ohppiin ferte leat oaivetelefovdna </text>
                <text top="856" left="322" width="93" height="18" font="1">guldalanoasis.  </text>
                <text top="298" left="593" width="170" height="18" font="0"><b>Bohtosat ja čuovvoleapmi</b></text>
                <text top="316" left="593" width="249" height="18" font="1">Kártengeahččalemiid bohtosiid ii galgga </text>
                <text top="334" left="593" width="248" height="18" font="1">rapporteret Oahpahusdirektoráhttii ii ge </text>
                <text top="352" left="593" width="207" height="18" font="1">geavahit buohtastahttit skuvllaid, </text>
                <text top="370" left="593" width="149" height="18" font="1">gielddaid dahje fylkkaid.</text>
                <text top="406" left="593" width="241" height="18" font="1">Bohtosiid galgá vuosttažettiin geavahit </text>
                <text top="424" left="593" width="197" height="18" font="1">siskkáldasat skuvllas láhčin dihti </text>
                <text top="442" left="593" width="208" height="18" font="1">oahpahusa nu, ahte oahppit, geat </text>
                <text top="460" left="593" width="252" height="18" font="1">dárbbašit dan, ožžot lassi bagadallama ja </text>
                <text top="478" left="593" width="230" height="18" font="1">doarjaga. Oahpaheddjiide leat ráhka- </text>
                <text top="496" left="593" width="211" height="18" font="1">duvvon bagadallanmateriálat mat </text>
                <text top="514" left="593" width="225" height="18" font="1">čilgehit mo geahččalemiid bohtosiid </text>
                <text top="532" left="593" width="100" height="18" font="1">sáhttá čuovvolit.</text>
                <text top="568" left="593" width="225" height="18" font="1">Jus čađaheami bohtosat čájehit ahte </text>
                <text top="586" left="593" width="242" height="18" font="1">oahppis lea dárbu lassi čuovvoleapmái, </text>
                <text top="604" left="593" width="190" height="18" font="1">de galgá váhnemiidda dieđihit </text>
                <text top="622" left="593" width="226" height="18" font="1">geahččalanbohtosiid birra ja muitalit </text>
                <text top="640" left="593" width="213" height="18" font="1">makkár doaimmaid áigot álggahit. </text>
                <text top="658" left="593" width="217" height="18" font="1">Váhnemat sáhttet váldit oktavuođa </text>
                <text top="676" left="593" width="186" height="18" font="1">skuvllain jus ležžet gažaldagat.</text>
                <text top="712" left="593" width="84" height="18" font="0"><b>Eanet dieđut</b></text>
                <text top="730" left="593" width="244" height="18" font="1">Eanet dieđut kártengeahččalemiid birra </text>
                <text top="748" left="593" width="80" height="18" font="1">leat dáppe:    </text>
                <text top="766" left="593" width="189" height="18" font="2">http://www.udir.no/Vurdering/</text>
                <text top="784" left="593" width="96" height="18" font="2">Kartlegging-gs/</text>
                <text top="820" left="593" width="230" height="18" font="1">Máhttoloktema oahppoplánabuvttus </text>
                <text top="838" left="593" width="69" height="18" font="1">lea dáppe:  </text>
                <text top="856" left="593" width="193" height="18" font="2">http://www.udir.no/Lareplaner/</text>
                <text top="874" left="593" width="104" height="18" font="2">Kunnskapsloftet/</text>
                <text top="209" left="147" width="605" height="39" font="3"><b>Diehtu 2015 giđa kártengeahččalemiid birra</b></text>
                <text top="262" left="306" width="286" height="19" font="4"><b>Váhnemiidda geain leat mánát 1.- 4. ceahkis</b></text>
                <text top="143" left="398" width="97" height="18" font="0"><b>Davvisámegillii</b></text>
            </page>
        ''')  # nopep8

        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('left_margin', 'all=3')
        metadata.set_variable('bottom_margin', 'all=3')
        metadata.set_variable('inner_top_margin', '1=76')
        metadata.set_variable('inner_bottom_margin', '1=0')
        metadata.set_variable('inner_left_margin', '1=35')
        metadata.set_variable('inner_right_margin', '1=0')

        pp = pdfconverter.PDFPage(self.start_page, metadata_margins=metadata.margins,
                               metadata_inner_margins=metadata.inner_margins)
        pp.adjust_line_heights()
        pp.remove_elements_not_within_margin()

        expected_page = etree.fromstring(
            '<page number="1" position="absolute" top="0" left="0" '
            'height="1262" width="892"/>')
        for pdftextelement in pp.textelements:
            expected_page.append(pdftextelement.t)

        self.assertXmlEqual(expected_page,
                            not_within_margin_page)

    def test_make_unordered_paragraphs(self):
        expected_page = etree.fromstring(u'''
            <body>
                <p><em type="bold">Dán giđa kártengeahččalemiid birra</em></p>
                <p>2015
                giđa galget skuvllat čađahit geatnegahtton kártengeahččalemiid
                1., 2. ja 3. ceahkis. Oahpahusdirektoráhtta fállá maid
                eaktodáhtolaš kártengeahččalemiid 1., 3. ja 4. ceahkis. 2015
                giđa fállojuvvo vel lassin ođđa eaktodáhtolaš kárten-
                geahččaleamit eŋgelasgielas 3. ceahkkái.</p>
                <p><em type="bold">Geatnegahtton kártengeahččaleamit</em></p>
                <p>Leat
                geatnegahtton kártengeahččaleamit:</p>
                <p type="listitem">• Lohkamis 1., 2. ja 3. ceahkis</p>
                <p type="listitem">• Rehkenastimis 2. ceahkis</p>
                <p>Buot oahppit galget váldit daid geatnegahtton
                kártengeahččalemiid. Oahppit geat leat eret geahččalan- beaivvi,
                galget čađahit geahččaleami maŋŋil.</p>
                <p>Kártengeahččalemiide leat sierra luvvennjuolggadusat. Vaikko
                oahppi deavddášii luvvema eavttuid, de sáhttá oahppi ieš dahje
                su váhnemat dattetge mearridit ahte oahppi galgá čađahit
                geahččaleami.</p>
                <p><em type="bold">Eaktodáhtolaš kártengeahččaleamit</em></p>
                <p>Geatnegahtton kártengeahččalemiide lassin fállá
                Oahpahusdirektoráhtta eaktodáhtolaš kártengeahččalemiid. Jus
                skuvla dahje skuvlaeaiggát mearrida čađahit eaktodáhtolaš
                kártengeahččalemiid, de fertejit buot oahppit dan ceahkis masa
                dát guoská váldit geahččaleami.</p>
                <p>Fállojuvvojit eaktodáhtolaš kártengeahččaleamit:</p>
                <p type="listitem">• Rehkenastimis 1. ja 3. ceahkis</p>
                <p type="listitem">• Eŋgelasgielas 3. ceahkis</p>
                <p type="listitem">• Digitála gálggain 4. ceahkis</p>
                <p><em type="bold">Dieđut geahččalemiid birra</em></p>
                <p>Kártengeahččalemiid galget skuvla ja oahpaheaddjit geavahit
                gávnnahit geat dárbbašit lasi čuovvoleami álgooahpa- husas.
                Eanaš oahppit máhttet buot hárjehusaid, ja máŋgasiid mielas ges
                lea geahččaleapmi álki. Geahččaleamit eai muital olus ohppiid
                birra geain leat buorit gálggat.</p>
                <p>Kártengeahččaleamit eai leat geahččaleamit fágas, muhto
                vuođđogálggain fágaid rastá. Oahppoplánain leat vuođđogálggat
                definerejuvvon ná:</p>
                <p type="listitem">• njálmmálaš gálggat</p>
                <p type="listitem">• máhttit lohkat</p>
                <p type="listitem">• máhttit čállit</p>
                <p type="listitem">• máhttit rehkenastit</p>
                <p type="listitem">• digitála gálggat</p>
                <p>Rehkenastinbihtáid ovdamearkkat sáhttet leat lohkat, sirret
                loguid sturro- dagaid mielde, loahpahit lohkogur- gadasaid ja
                rehkenastit plussain ja minusiin. Lohkamis sáhttá leat sáhka
                ovdamearkka dihtii bustávaid čállimis, sániid lohkamis ja
                cealkagiid lohkamis. Guovddážis digitála gálggaid geahčča- leami
                bihtáin lea háhkat ja meannudit, buvttadit ja divodit,
                gulahallat ja digitála árvvoštallannávccat. Guovddážis
                eŋgelasgiellageahččaleamis lea dovdat ja ipmirdit oahpes ja
                beaivválaš sániid ja dajaldagaid, njálmmálaččat dahje
                čálalaččat. Geahččaleamis leat guokte oasi, guldalanoassi ja
                lohkanoassi. Ohppiin ferte leat oaivetelefovdna guldalanoasis.</p>
                <p><em type="bold">Bohtosat ja čuovvoleapmi</em></p>
                <p>Kártengeahččalemiid
                bohtosiid ii galgga rapporteret Oahpahusdirektoráhttii ii ge
                geavahit buohtastahttit skuvllaid, gielddaid dahje fylkkaid.</p>
                <p>Bohtosiid galgá vuosttažettiin geavahit siskkáldasat skuvllas
                láhčin dihti oahpahusa nu, ahte oahppit, geat dárbbašit dan,
                ožžot lassi bagadallama ja doarjaga. Oahpaheddjiide leat ráhka-
                duvvon bagadallanmateriálat mat čilgehit mo geahččalemiid
                bohtosiid sáhttá čuovvolit.</p>
                <p>Jus čađaheami bohtosat čájehit ahte oahppis lea dárbu lassi
                čuovvoleapmái, de galgá váhnemiidda dieđihit geahččalanbohtosiid
                birra ja muitalit makkár doaimmaid áigot álggahit. Váhnemat
                sáhttet váldit oktavuođa skuvllain jus ležžet gažaldagat.</p>
                <p><em type="bold">Eanet dieđut</em></p>
                <p>Eanet dieđut
                kártengeahččalemiid birra leat dáppe:</p>
                <p>http://www.udir.no/Vurdering/ Kartlegging-gs/</p>
                <p>Máhttoloktema oahppoplánabuvttus lea dáppe:</p>
                <p>http://www.udir.no/Lareplaner/ Kunnskapsloftet/</p>
                <p><em type="bold">Diehtu 2015 giđa kártengeahččalemiid birra</em></p>
                <p><em type="bold">Váhnemiidda geain leat mánát 1.- 4. ceahkis</em></p>
                <p><em type="bold">Davvisámegillii</em></p>
            </body>
            ''')

        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('left_margin', 'all=3')
        metadata.set_variable('bottom_margin', 'all=3')
        metadata.set_variable('inner_top_margin', '1=76')
        metadata.set_variable('inner_bottom_margin', '1=0')
        metadata.set_variable('inner_left_margin', '1=35')
        metadata.set_variable('inner_right_margin', '1=0')

        pp = pdfconverter.PDFPage(self.start_page, metadata_margins=metadata.margins,
                               metadata_inner_margins=metadata.inner_margins)
        pp.adjust_line_heights()
        pp.remove_elements_not_within_margin()
        pp.remove_footnotes_superscript()
        pp.merge_elements_on_same_line()
        pp.remove_invalid_elements()

        paragraphs = pp.make_unordered_paragraphs()

        extractor = pdfconverter.PDFTextExtractor()
        extractor.extract_text_from_page(paragraphs)
        self.assertXmlEqual(extractor.body,
                            expected_page)

    def test_make_ordered_sections(self):
        expected_page = etree.fromstring(u'''
            <body>
                <p><em type="bold">Davvisámegillii</em></p>
                <p><em type="bold">Diehtu 2015 giđa kártengeahččalemiid birra</em></p>
                <p><em type="bold">Váhnemiidda geain leat mánát 1.- 4. ceahkis</em></p>
                <p><em type="bold">Dán giđa kártengeahččalemiid birra</em></p>
                <p>2015
                giđa galget skuvllat čađahit geatnegahtton kártengeahččalemiid
                1., 2. ja 3. ceahkis. Oahpahusdirektoráhtta fállá maid
                eaktodáhtolaš kártengeahččalemiid 1., 3. ja 4. ceahkis. 2015
                giđa fállojuvvo vel lassin ođđa eaktodáhtolaš kárten-
                geahččaleamit eŋgelasgielas 3. ceahkkái.</p>
                <p><em type="bold">Geatnegahtton kártengeahččaleamit</em></p>
                <p>Leat
                geatnegahtton kártengeahččaleamit:</p>
                <p type="listitem">• Lohkamis 1., 2. ja 3. ceahkis</p>
                <p type="listitem">• Rehkenastimis 2. ceahkis</p>
                <p>Buot oahppit galget váldit daid geatnegahtton
                kártengeahččalemiid. Oahppit geat leat eret geahččalan- beaivvi,
                galget čađahit geahččaleami maŋŋil.</p>
                <p>Kártengeahččalemiide leat sierra luvvennjuolggadusat. Vaikko
                oahppi deavddášii luvvema eavttuid, de sáhttá oahppi ieš dahje
                su váhnemat dattetge mearridit ahte oahppi galgá čađahit
                geahččaleami.</p>
                <p><em type="bold">Eaktodáhtolaš kártengeahččaleamit</em></p>
                <p>Geatnegahtton kártengeahččalemiide lassin fállá
                Oahpahusdirektoráhtta eaktodáhtolaš kártengeahččalemiid. Jus
                skuvla dahje skuvlaeaiggát mearrida čađahit eaktodáhtolaš
                kártengeahččalemiid, de fertejit buot oahppit dan ceahkis masa
                dát guoská váldit geahččaleami.</p>
                <p>Fállojuvvojit eaktodáhtolaš kártengeahččaleamit:</p>
                <p type="listitem">• Rehkenastimis 1. ja 3. ceahkis</p>
                <p type="listitem">• Eŋgelasgielas 3. ceahkis</p>
                <p type="listitem">• Digitála gálggain 4. ceahkis</p>
                <p><em type="bold">Dieđut geahččalemiid birra</em></p>
                <p>Kártengeahččalemiid galget skuvla ja oahpaheaddjit geavahit
                gávnnahit geat dárbbašit lasi čuovvoleami álgooahpa- husas.
                Eanaš oahppit máhttet buot hárjehusaid, ja máŋgasiid mielas ges
                lea geahččaleapmi álki. Geahččaleamit eai muital olus ohppiid
                birra geain leat buorit gálggat.</p>
                <p>Kártengeahččaleamit eai leat geahččaleamit fágas, muhto
                vuođđogálggain fágaid rastá. Oahppoplánain leat vuođđogálggat
                definerejuvvon ná:</p>
                <p type="listitem">• njálmmálaš gálggat</p>
                <p type="listitem">• máhttit lohkat</p>
                <p type="listitem">• máhttit čállit</p>
                <p type="listitem">• máhttit rehkenastit</p>
                <p type="listitem">• digitála gálggat</p>
                <p>Rehkenastinbihtáid ovdamearkkat sáhttet leat lohkat, sirret
                loguid sturro- dagaid mielde, loahpahit lohkogur- gadasaid ja
                rehkenastit plussain ja minusiin. Lohkamis sáhttá leat sáhka
                ovdamearkka dihtii bustávaid čállimis, sániid lohkamis ja
                cealkagiid lohkamis. Guovddážis digitála gálggaid geahčča- leami
                bihtáin lea háhkat ja meannudit, buvttadit ja divodit,
                gulahallat ja digitála árvvoštallannávccat. Guovddážis
                eŋgelasgiellageahččaleamis lea dovdat ja ipmirdit oahpes ja
                beaivválaš sániid ja dajaldagaid, njálmmálaččat dahje
                čálalaččat. Geahččaleamis leat guokte oasi, guldalanoassi ja
                lohkanoassi. Ohppiin ferte leat oaivetelefovdna guldalanoasis.</p>
                <p><em type="bold">Bohtosat ja čuovvoleapmi</em></p>
                <p>Kártengeahččalemiid bohtosiid ii galgga rapporteret
                Oahpahusdirektoráhttii ii ge geavahit buohtastahttit skuvllaid,
                gielddaid dahje fylkkaid.</p>
                <p>Bohtosiid galgá vuosttažettiin geavahit siskkáldasat skuvllas
                láhčin dihti oahpahusa nu, ahte oahppit, geat dárbbašit dan,
                ožžot lassi bagadallama ja doarjaga. Oahpaheddjiide leat ráhka-
                duvvon bagadallanmateriálat mat čilgehit mo geahččalemiid
                bohtosiid sáhttá čuovvolit.</p>
                <p>Jus čađaheami bohtosat čájehit ahte oahppis lea dárbu lassi
                čuovvoleapmái, de galgá váhnemiidda dieđihit geahččalanbohtosiid
                birra ja muitalit makkár doaimmaid áigot álggahit. Váhnemat
                sáhttet váldit oktavuođa skuvllain jus ležžet gažaldagat.</p>
                <p><em type="bold">Eanet dieđut</em></p>
                <p>Eanet dieđut kártengeahččalemiid birra leat dáppe:</p>
                <p>http://www.udir.no/Vurdering/ Kartlegging-gs/</p>
                <p>Máhttoloktema oahppoplánabuvttus lea dáppe:</p>
                <p>http://www.udir.no/Lareplaner/ Kunnskapsloftet/</p>
            </body>
            ''')

        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('left_margin', 'all=3')
        metadata.set_variable('bottom_margin', 'all=3')
        metadata.set_variable('inner_top_margin', '1=76')
        metadata.set_variable('inner_bottom_margin', '1=0')
        metadata.set_variable('inner_left_margin', '1=35')
        metadata.set_variable('inner_right_margin', '1=0')

        pp = pdfconverter.PDFPage(self.start_page, metadata_margins=metadata.margins,
                               metadata_inner_margins=metadata.inner_margins)
        pp.adjust_line_heights()
        pp.remove_elements_not_within_margin()
        pp.remove_footnotes_superscript()
        pp.merge_elements_on_same_line()
        pp.remove_invalid_elements()

        extractor = pdfconverter.PDFTextExtractor()
        extractor.extract_text_from_page(pp.make_ordered_sections().paragraphs)
        self.assertXmlEqual(extractor.body,
                            expected_page)


class TestPDFPageMetaData(unittest.TestCase):

    def test_compute_default_margins(self):
        """Test if the default margins are set."""
        page1 = pdfconverter.PDFPageMetadata(page_number=1,
                                          page_height=1263,
                                          page_width=862)

        self.assertEqual(page1.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 801,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1174})

    def test_compute_margins1(self):
        """Test parse_margin_lines."""
        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('left_margin', '7=5')
        metadata.set_variable('right_margin', 'odd=10,even=15,3=5')
        metadata.set_variable('top_margin', '8=8')
        metadata.set_variable('bottom_margin', '9=20')

        page1 = pdfconverter.PDFPageMetadata(
            page_number=1, page_height=1263, page_width=862,
            metadata_margins=metadata.margins)

        self.assertEqual(page1.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 775,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1174})
        page2 = pdfconverter.PDFPageMetadata(
            page_number=2, page_height=1263, page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(page2.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 732,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1174})
        page3 = pdfconverter.PDFPageMetadata(
            page_number=3, page_height=1263, page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(page3.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 818,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1174})
        page7 = pdfconverter.PDFPageMetadata(
            page_number=7, page_height=1263, page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(page7.compute_margins(), {'left_margin': 43,
                                                   'right_margin': 775,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1174})
        page8 = pdfconverter.PDFPageMetadata(
            page_number=8, page_height=1263, page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(page8.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 732,
                                                   'top_margin': 101,
                                                   'bottom_margin': 1174})
        page9 = pdfconverter.PDFPageMetadata(
            page_number=9, page_height=1263, page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(page9.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 775,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1010})

    def test_compute_inner_margins_1(self):
        """Test if inner margins is set for the specified page."""
        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('inner_top_margin', '1=40')
        metadata.set_variable('inner_bottom_margin', '1=40')

        page1 = pdfconverter.PDFPageMetadata(
            page_number=1, page_height=1263, page_width=862,
            metadata_inner_margins=metadata.inner_margins)

        self.assertEqual(page1.compute_inner_margins(),
                         {'inner_top_margin': 505, 'inner_bottom_margin': 757,
                          'inner_left_margin': 0, 'inner_right_margin': 862})

    def test_compute_inner_margins_2(self):
        """Test that inner margins is empty for the specified page."""
        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('inner_top_margin', '1=40')
        metadata.set_variable('inner_bottom_margin', '1=40')

        page1 = pdfconverter.PDFPageMetadata(
            page_number=2, page_height=1263, page_width=862,
            metadata_inner_margins=metadata.inner_margins)

        self.assertEqual(page1.compute_inner_margins(), {})

    def test_width(self):
        page = pdfconverter.PDFPageMetadata(
            page_number=1, page_height=1263, page_width=862)

        self.assertEqual(page.page_number, 1)
        self.assertEqual(page.page_height, 1263)
        self.assertEqual(page.page_width, 862)


class TestPDFPage(xmltester.XMLTester):

    def test_merge_text_elements(self):
        page = etree.fromstring(u'''
            <page number="1" height="1263" width="862">'
                <text top="197" left="257" width="4" height="17" font="8"> </text>
                <text top="195" left="267" width="493" height="20" font="0">Departemeanttat fertejit dahkat vuolit etáhtaid dihtomielalažžan das </text>
            </page>
        ''')  # nopep8
        pdfpage = pdfconverter.PDFPage(page)
        pdfpage.merge_elements_on_same_line()

        self.assertEqual(len(pdfpage.textelements), 1)
        self.assertXmlEqual(
            pdfpage.textelements[0].t,
            etree.fromstring(
                '<text top="197" left="257" width="497" height="20" font="8">'
                'Departemeanttat fertejit dahkat vuolit et&#225;htaid '
                'dihtomielala&#382;&#382;an das </text>'))

    def test_remove_footnotes_superscript_1(self):
        """Footnote superscript is in the middle of a sentence."""
        page = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '   <text top="323" left="117" width="305" height="16" font="2">'
            'gihligotteriektái</text>'
            '   <text top="319" left="422" width="6" height="11" font="7">3'
            '</text>'
            '   <text top="323" left="428" width="220" height="16" font="2">, '
            'sáhtte</text>'
            '</page>'
        )
        pdfpage = pdfconverter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'gihligotteriektái', '', u', sáhtte']

        self.assertListEqual([t.t.xpath('string()')
                              for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_2(self):
        """Footnote superscript is at the end of a sentence."""
        page = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '   <text top="323" left="117" width="305" height="16" font="2">'
            'gihligotteriektái</text>'
            '   <text top="319" left="422" width="6" height="11" font="7">'
            '3</text>'
            '   <text top="344" left="428" width="220" height="16" font="2">,'
            'sáhtte</text>'
            '</page>'
        )
        pdfpage = pdfconverter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'gihligotteriektái', '', u',sáhtte']

        self.assertListEqual([t.t.xpath('string()')
                              for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_3(self):
        """Footnote superscript in between i-elements."""
        page = etree.fromstring('''
            <page number="1" height="1263" width="892">
                <text top="267" left="119" width="164" height="22" font="9"><i>riektedilálašvuođa</i></text>
                <text top="265" left="283" width="15" height="15" font="7">16</text>
                <text top="267" left="298" width="503" height="22" font="9"><i> </i>čielggadeamit&#34; (min deattuhus) ráddjejuvvot dasa mii </text>
            </page>
        ''')  # nopep8
        pdfpage = pdfconverter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'riektedilálašvuođa', u'',
                     u' čielggadeamit" (min deattuhus) ráddjejuvvot dasa mii ']

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_4(self):
        """Footnote superscript contained in i-element."""
        page = etree.fromstring('''
            <page number="1" height="1263" width="892">
               <text top="682" left="119" width="187" height="22" font="9"><i>báhcánvuoigatvuođa</i></text>
               <text top="680" left="306" width="20" height="15" font="11"><i>59</i> </text>
               <text top="704" left="119" width="666" height="22" font="2"> - nuppiin sániiguin dan mii áiggis áigái ii leat čuldon dahje earát váldán. </text>
            </page>
        ''')  # nopep8
        pdfpage = pdfconverter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'báhcánvuoigatvuođa', u' ',
                     u' - nuppiin sániiguin dan mii áiggis áigái ii leat '
                     u'čuldon dahje earát váldán. ']

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_5(self):
        """Footnote superscript at the samel level as other text."""
        page = etree.fromstring('''
            <page number="1" height="1261" width="892">
               <text top="560" left="102" width="231" height="15" font="4">Boazu lea, nu movt eará smirezasti</text>
               <text top="560" left="333" width="8" height="9" font="12">1 </text>
               <text top="560" left="341" width="91" height="15" font="4">eallit nai, ere-</text>
            </page>
        ''')  # nopep8
        pdfpage = pdfconverter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'Boazu lea, nu movt eará smirezasti',
                     u' ', u'eallit nai, ere-']

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_6(self):
        """Footnote superscript inside two levels."""
        page = etree.fromstring('''
            <page number="1" height="1261" width="892">
               <text top="560" left="102" width="231" height="15" font="4">Boazu lea, nu movt eará smirezasti</text>
               <text top="560" left="333" width="8" height="9" font="12"><a><b>34</b></a></text>
               <text top="560" left="341" width="91" height="15" font="4">eallit nai, ere-</text>
            </page>
        ''')  # nopep8
        pdfpage = pdfconverter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u"Boazu lea, nu movt eará smirezasti",
                     u"", u"eallit nai, ere-"]

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_elements_not_within_margin_1(self):
        """Check that elements within inner_margins for a specific page are removed."""
        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('inner_top_margin', '8=40')
        metadata.set_variable('inner_bottom_margin', '8=40')

        page = etree.fromstring('''
            <page number="8" height="1263" width="862">'
                <text top="500" left="80" width="512" height="19" font="0">1</text>
                <text top="600" left="80" width="512" height="19" font="0">2</text>
                <text top="800" left="80" width="512" height="19" font="0">3</text>
            </page>
        ''')  # nopep8
        pdfpage = pdfconverter.PDFPage(page,
                                    metadata_inner_margins=metadata.inner_margins)
        pdfpage.remove_elements_not_within_margin()
        page_want = ["1", "3"]

        self.assertListEqual([t.t.xpath('string()')
                              for t in pdfpage.textelements], page_want)

    def test_remove_elements_not_within_margin_2(self):
        """Check that no elements are removed when inner_margins is not defined for the page."""
        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('inner_top_margin', '1=40')
        metadata.set_variable('inner_bottom_margin', '1=40')

        page = etree.fromstring('''
            <page number="8" height="1263" width="862">
                <text top="500" left="80" width="512" height="19" font="0">1</text>
                <text top="600" left="80" width="512" height="19" font="0">2</text>
                <text top="800" left="80" width="512" height="19" font="0">3</text>
            </page>
        ''')  # nopep8
        pdfpage = pdfconverter.PDFPage(
            page, metadata_inner_margins=metadata.inner_margins)
        pdfpage.remove_elements_not_within_margin()
        page_want = ["1", "2", "3"]

        self.assertListEqual([t.t.xpath('string()')
                              for t in pdfpage.textelements], page_want)

    def test_adjust_line_heights(self):
        page = etree.fromstring('''
            <page number="1" position="absolute" top="0" left="0" height="1262" width="892">
                <text top="298" left="51" width="234" height="19" font="0"><b>Dán giđa kártengeahččalemiid birra</b></text>
                <text top="316" left="51" width="194" height="18" font="1">2015 giđa galget skuvllat čađahit </text>
            </page>
        ''')  # nopep8
        pdfpage = pdfconverter.PDFPage(page)
        pdfpage.adjust_line_heights()

        wanted_heights = [18, 18]
        self.assertListEqual(
            [t.height for t in pdfpage.textelements], wanted_heights)

    def test_is_inside_margins1(self):
        """top and left inside margins."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="109" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="2" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins2(self):
        """top above top margin and left inside margins."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="85" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins3(self):
        """top below bottom margin and left inside margins."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="1178" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins4(self):
        """top inside margins and left outside right margin."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="1000" left="50"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins5(self):
        """top inside margins and left outside left margin."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="1000" left="805"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_skip_page_1(self):
        """Odd page should be skipped when odd is in skip_pages."""
        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="1" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['odd']))

    def test_is_skip_page_2(self):
        """Even page should be skipped when even is in skip_pages."""
        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="2" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['even']))

    def test_is_skip_page_3(self):
        """Even page should not be skipped when odd is in skip_pages."""
        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['odd']))

    def test_is_skip_page_4(self):
        """Odd page should not be skipped when even is in skip_pages."""
        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="1" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['even']))

    def test_is_skip_page_5(self):
        """Page should not be skipped when not in skip_range."""
        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="1" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['even', 3]))

    def test_is_skip_page_6(self):
        """Page should be skipped when in skip_range."""
        p2x = pdfconverter.PDFPage(etree.fromstring(
            '<page number="3" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['even', 3]))

    def test_parse_page_textelement_witdh_zero_not_added(self):
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="649" left="545" width="0" height="14" font="20">'
            'berret bargat. </text>'
            '</page>')

        pp = pdfconverter.PDFPage(page_element)
        pp.remove_invalid_elements()

        self.assertEqual(len(pp.textelements), 0)


class TestPDF2XMLConverter(xmltester.XMLTester):
    """Test the class that converts from pdf2xml to giellatekno/divvun xml."""

    def test_pdf_converter(self):
        pdfdocument = pdfconverter.PDF2XMLConverter(
            os.path.join(HERE, 'converter_data/fakecorpus/orig/sme/riddu/pdf-test.pdf'))
        got = pdfdocument.convert2intermediate()
        want = etree.parse(
            os.path.join(HERE, 'converter_data/pdf-xml2pdf-test.xml'))

        self.assertXmlEqual(got, want)

    def test_parse_page_1(self):
        """Page with one paragraph, three <text> elements."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="106" left="100" width="100" height="19" font="1">a </text>'
            '<text top="126" left="100" width="100" height="19" font="1">b </text>'
            '<text top="145" left="100" width="100" height="19" font="1">c.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>a b c.</p></body>'))

    def test_parse_page_2(self):
        """Page with two paragraphs, four <text> elements."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="106" left="100" width="100" height="19" font="1">a </text>'
            '<text top="126" left="100" width="100" height="19" font="1">b.</text>'
            '<text top="166" left="100" width="100" height="19" font="1">c </text>'
            '<text top="186" left="100" width="100" height="19" font="1">d.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>a b.</p><p>c d.</p></body>'))

    def test_parse_page_3(self):
        """Page with one paragraph, one <text> elements."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_4(self):
        """One text element with a ascii letter, the other one with a non-ascii

        This makes two parts lists. The first list contains one element that is
        of type str, the second list contains one element that is unicode.
        """
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="215" left="100" width="51" height="14" font="1">R</text>'
            '<text top="245" left="100" width="39" height="14" font="1">Ø</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>R</p><p>Ø</p></body>'))

    def test_parse_page_5(self):
        """Test parse pages

        One text element containing a <b>, the other one with a
        non-ascii string. Both belong to the same paragraph.
        """
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="215" left="100" width="51" height="14" font="1"><b>R</b></text>'
            '<text top="235" left="100" width="39" height="14" font="1">Ø</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p><em type="bold">R</em>Ø</p></body>'))

    def test_parse_page_6(self):
        """One text element ending with a hyphen."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="215" left="100" width="51" height="14" font="1">R-</text>'
            '<text top="235" left="100" width="39" height="14" font="1">Ø</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring(u'<body><p>R\xADØ</p></body>'))

    def test_parse_page_7(self):
        """One text element ending with a hyphen."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="215" left="100" width="51" height="14" font="1">R -</text>'
            '<text top="235" left="100" width="39" height="14" font="1">Ø</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>R - Ø</p></body>'))

    def test_parse_page_8(self):
        """One text element ending with a hyphen."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="15" size="13" family="Times" color="#231f20"/>'
            '<text top="196" left="142" width="69" height="21" font="15">'
            '<b>JULE-</b></text>'
            '<text top="223" left="118" width="123" height="21" font="15">'
            '<b>HANDEL</b></text></page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring(u'<body><p><em type="bold">JULE\xADHANDEL</em></p></body>'))

    def test_parse_page_9(self):
        """Two <text> elements. One is above the top margin."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="70" left="100" width="100" height="19" font="1">Page 1</text>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_10(self):
        """Two <text> elements. One is below the bottom margin."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="1200" left="100" width="100" height="19" font="1">Page 1</text>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_11(self):
        """Two <text> elements. One is to the left of the right margin."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="500" left="50" width="100" height="19" font="1">Page 1</text>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_12(self):
        """Two <text> elements. One is to the right of the left margin."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="500" left="850" width="100" height="19" font="1">Page 1</text>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_13(self):
        """Test list detection with • character."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="195" left="104" width="260" height="18" font="1">'
            'vuosttaš dábálaš linnjá</text>'
            '<text top="237" left="104" width="311" height="18" font="1">'
            '• Vuosttaš listolinnjá </text>'
            '<text top="258" left="121" width="296" height="18" font="1">'
            'vuosttaš listolinnjá joaktta</text>'
            '<text top="279" left="104" width="189" height="18" font="1">'
            '• Nubbi listo-</text>'
            '<text top="300" left="121" width="324" height="18" font="1">'
            'linnjá</text>'
            '<text top="321" left="104" width="40" height="18" font="1">'
            'Nubbi dábáláš linnjá</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.maxDiff = None
        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring(u'<body>'
                             u'<p>vuosttaš dábálaš linnjá</p>'
                             u'<p type="listitem">• Vuosttaš listolinnjá  '
                             u'vuosttaš listolinnjá joaktta</p>'
                             u'<p type="listitem">• Nubbi listo\xADlinnjá</p>'
                             u'<p>Nubbi dábáláš linnjá</p>'
                             u'</body>'))

    def test_parse_page_14(self):
        """Test that elements outside margin is not added."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="1104" left="135" width="45" height="16" font="2">'
            '1751, </text>'
            '<text top="1184" left="135" width="4" height="15" font="0"> '
            '</text>'
            '<text top="1184" left="437" width="37" height="15" font="0">'
            '– 1 – </text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body>'
                             '<p>1751, </p>'
                             '</body>'))

    def test_parse_page_soria_moria(self):
        """The last element was not added to the p element."""
        page_element = etree.fromstring('''
            <page number="1" height="1263" width="862">
                <text top="666" left="104" width="312" height="18" font="1">A – <i>b </i></text>
                <text top="687" left="104" width="318" height="18" font="1"><i>c-d</i> – e-</text>
                <text top="708" left="104" width="328" height="18" font="1">f </text>
            </page>
        ''')  # nopep8

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring(u'<body><p>A – <em type="italic">b c-d</em> – '
                             u'e\xADf </p></body>'))

    def test_parse_pdf2xmldoc1(self):
        """Test how a parsing a simplistic pdf2xml document works."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862">
                    <fontspec id="1" size="13" family="Times" color="#231f20"/>
                    <text top="145" left="100" width="100" height="19" font="1">1.</text>
                </page>
                <page number="2" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">2.</text>
                </page>
                <page number="3" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">3.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>1.</p><p>2.</p><p>3.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc2(self):
        """Test if pages really are skipped."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862">
                    <fontspec id="1" size="13" family="Times" color="#231f20"/>
                    <text top="145" left="100" width="100" height="19" font="1">1.</text>
                </page>
                <page number="2" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">2.</text>
                </page>
                <page number="3" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">3.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>2.</p><p>3.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.metadata.set_variable('skip_pages', '1')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc3(self):
        """Check if paragraph is continued from page to page

        Paragraph should continue if the first character on next page is a
        lower case character
        """
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" position="absolute" top="0" left="0" height="1020" width="723">
                    <text top="898" left="80" width="512" height="19" font="0">Dán </text>
                </page>
                <page number="2" position="absolute" top="0" left="0" height="1020" width="723">
                    <text top="43" left="233" width="415" height="16" font="7">Top text </text>
                    <text top="958" left="174" width="921" height="19" font="0">15 </text>
                    <text top="93" left="131" width="512" height="19" font="0">barggus.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>Dán barggus.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc4(self):
        """Check if paragraph is continued from page to page.

        Paragraph should continue if the first character on next page is a
        lower case character
        """
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" position="absolute" top="0" left="0" height="1020" width="723">
                    <text top="898" left="80" width="512" height="19" font="0">Dán ovddidan-</text>
                </page>
                <page number="2" position="absolute" top="0" left="0" height="1020" width="723">
                    <text top="43" left="233" width="415" height="16" font="7">Top text </text>
                    <text top="958" left="174" width="921" height="19" font="0">15 </text>
                    <text top="93" left="131" width="512" height="19" font="0">barggus.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>Dán ovddidan\xADbarggus.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_text_disappears(self):
        """Bug 2115, Store deler av teksten blir borte."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="40" position="absolute" top="0" left="0" height="1263" width="892">
                    <text top="1061" left="106" width="680" height="20" font="7"><i>vuođđooahpa-</i></text>
                    <text top="1085" left="106" width="653" height="20" font="7"><i>hussi. </i></text>
                    <text top="1110" left="106" width="5" height="20" font="7"><i> </i></text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'''<body><p><em type="italic">vuođđooahpa\xADhussi. </em></p></body>'''

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_text_unwanted_line_shift(self):
        """Bug 2107, Linjeskift hvor det ikke skal være."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="40" position="absolute" top="0" left="0" height="1263" width="892">
                    <text top="354" left="119" width="205" height="22" font="2">1.1.   RIEKTEJOAVKKU</text>
                    <text top="352" left="325" width="8" height="15" font="7">1</text>
                    <text top="354" left="332" width="6" height="22" font="2"> </text>
                    <text top="350" left="339" width="4" height="16" font="7"> </text>
                    <text top="354" left="343" width="104" height="22" font="2">MANDÁHTA</text>
                    <text top="352" left="447" width="12" height="15" font="7">2 </text>
                    <text top="354" left="460" width="143" height="22" font="2">JA ČOAHKÁDUS</text>
                    <text top="352" left="603" width="12" height="15" font="7">3 </text>
                    <text top="354" left="615" width="13" height="22" font="2">  </text>
                    <text top="376" left="119" width="6" height="22" font="2"> </text>
                    <text top="398" left="119" width="389" height="22" font="2">1.1.1 Riektejoavkku nammadeami duogáš </text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'''
            <body>
                <p>1.1. RIEKTEJOAVKKU MANDÁHTA JA ČOAHKÁDUS</p>
                <p>1.1.1 Riektejoavkku nammadeami duogáš</p>
            </body>
        '''

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_ends_with_dot(self):
        """If last string on a page ends with ., do not continue paragraph to next page."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862">
                    <fontspec id="1" size="13" family="Times" color="#231f20"/>
                    <text top="145" left="100" width="100" height="19" font="1">1.</text>
                </page>
                <page number="2" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">2.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>1.</p><p>2.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_ends_with_exclam(self):
        """If last string on a page ends with !, do not continue paragraph to next page."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862">
                    <fontspec id="1" size="13" family="Times" color="#231f20"/>
                    <text top="145" left="100" width="100" height="19" font="1">1!</text>
                </page>
                <page number="2" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">2.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>1!</p><p>2.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_ends_with_question(self):
        """If last string on a page ends with ?, do not continue paragraph to next page."""
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="145" left="100" width="100" height="19" font="1">1?</text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19" font="1">2.</text>'
            '</page>'

            '</pdf2xml>')
        want = u'<body><p>1?</p><p>2.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_not_end_of_sentence(self):
        """If last string on a page is not ended, continue paragraph."""
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="145" left="100" width="100" height="19" font="1">a </text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19" font="1">b.</text>'
            '</page>'

            '</pdf2xml>')
        want = u'<body><p>a b.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_text_on_same_line_different_font(self):
        """Test of bug2101."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862"><fontspec/>
                    <text top="187" left="64" width="85" height="14" font="20">bajás</text>
                    <text top="187" left="149" width="6" height="14" font="8">š</text>
                    <text top="187" left="155" width="280" height="14" font="20">addandili</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>bajásšaddandili</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_pp_tjenesten(self):
        """Test of bug2101."""
        pdf2xml = etree.fromstring(u'''
            <pdf2xml>
                <page number="4" position="absolute" top="0" left="0" height="1262" width="892">
                    <text top="942" left="133" width="640" height="23" font="4"> ahte buoridit unnitlogugielagiid oahpahusfálaldaga dási ja buoridit barggu, man olis </text>
                    <text top="965" left="160" width="617" height="22" font="4">ovddidit fátmmasteaddji, máŋggakultuvrralaš oahppansearvevuođaid mánáidgárdái </text>
                    <text top="986" left="160" width="165" height="22" font="4">ja vuođđooahpahussii.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'''
            <body>
                <p type="listitem"> ahte buoridit unnitlogugielagiid oahpahusfálaldaga dási ja buoridit barggu, man olis ovddidit fátmmasteaddji, máŋggakultuvrralaš oahppansearvevuođaid mánáidgárdái ja vuođđooahpahussii.</p>
            </body>'''  # nopep8

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_em_at_end_of_page_and_start_of_next_page(self):
        pdf2xml = etree.fromstring(u'''
            <pdf2xml>
                <page number="1" position="absolute" top="0" left="0" height="1263" width="892">
                    <fontspec id="0" size="18" family="Times" color="#000000"/>
                    <text top="899" left="98" width="719" height="23" font="0">Tabeallas 2.1 oaidnit lohku bissu dássedin mánáidgárddiin main lea </text>
                    <text top="926" left="98" width="703" height="23" font="0">sámegielfálaldat. Lohku mánáidgárddiin maid Sámediggi gohčoda  <i>sámi</i> </text>
                    <text top="954" left="98" width="717" height="23" font="0">mánáidgárdin, gal lea njiedjan maŋemus vihtta jagi ollislaččat, muhto </text>
                    <text top="982" left="98" width="697" height="23" font="0">mánáidgárdefálaldagat gohčoduvvon  <i>sámegielat fálaldat dárogielat mánáid-</i></text>
                </page>
                <page number="1" position="absolute" top="0" left="0" height="1263" width="892">
                    <fontspec id="2" size="18" family="Times" color="#000000"/>
                    <text top="116" left="98" width="710" height="23" font="2"><i>gárddiin</i> leat lassánan, nu ahte fálaldagaid ollislaš lohku lea goitge bisson </text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'''
            <body>
                <p>
                    Tabeallas 2.1 oaidnit lohku bissu dássedin mánáidgárddiin main lea
                    sámegielfálaldat. Lohku mánáidgárddiin maid Sámediggi gohčoda
                    <em type="italic">sámi</em>mánáidgárdin, gal lea njiedjan maŋemus
                    vihtta jagi ollislaččat, muhto mánáidgárdefálaldagat gohčoduvvon
                    <em type="italic">sámegielat fálaldat dárogielat mánáid\xADgárddiin</em>leat
                    lassánan, nu ahte fálaldagaid ollislaš lohku lea goitge bisson
                </p>
            </body>
        '''  # nopep8

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))