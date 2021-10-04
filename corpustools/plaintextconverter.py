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
#   Copyright © 2012-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert plaintext files to the Giella xml format."""

import codecs
import io
import re

import lxml.etree as etree

from corpustools import basicconverter, util


class PlaintextConverter(basicconverter.BasicConverter):
    """Convert plain text files to the Giella xml format."""

    def to_unicode(self):
        """Read a file into a unicode string.

        If the content of the file is not utf-8, pretend the encoding is
        latin1. The real encoding will be detected later.

        Returns:
            str
        """
        try:
            content = codecs.open(self.orig, encoding="utf8").read()
        except ValueError:
            content = codecs.open(self.orig, encoding="latin1").read()

        content = self.strip_chars(content.replace("\r\n", "\n"))

        return content

    @staticmethod
    def strip_chars(content, extra=""):
        """Remove the characters found in plaintext_oddities from content.

        Args:
            content: a string containing the content of a document.
            extra: a string containg even more characters to remove
            from content.

        Returns:
            A string containing the content sans unwanted characters.
        """
        plaintext_oddities = [
            ("ÊÊ", "\n"),
            (r"<\!q>", ""),
            (r"<\!h>", ""),
            ("<*B>", ""),
            ("<*P>", ""),
            ("<*I>", ""),
            ("\r", "\n"),
            ("<ASCII-MAC>", ""),
            ("<vsn:3.000000>", ""),
            ("<0x010C>", "Č"),
            ("<0x010D>", "č"),
            ("<0x0110>", "Đ"),
            ("<0x0111>", "đ"),
            ("<0x014A>", "Ŋ"),
            ("<0x014B>", "ŋ"),
            ("<0x0160>", "Š"),
            ("<0x0161>", "š"),
            ("<0x0166>", "Ŧ"),
            ("<0x0167>", "ŧ"),
            ("<0x017D>", "Ž"),
            ("<0x017E>", "ž"),
            ("<0x2003>", " "),
            (
                "========================================================"
                "========================",
                "\n",
            ),
        ]
        content = util.replace_all(plaintext_oddities, content)
        remove_re = re.compile(f"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F{extra}]")
        content, _ = remove_re.subn("", content)

        return content

    @staticmethod
    def make_element(element_name, text):
        """Make an xml element.

        Args:
            element_name (str): Name of the xml element
            text (str): The text the xml should contain
            attributes (dict): The attributes the element should have

        :returns: lxml.etree.Element
        """
        element = etree.Element(element_name)

        hyph_parts = text.split("<hyph/>")
        if len(hyph_parts) > 1:
            element.text = hyph_parts[0]
            for hyph_part in hyph_parts[1:]:
                hyph = etree.Element("hyph")
                hyph.tail = hyph_part
                element.append(hyph)
        else:
            element.text = text

        return element

    def content2xml(self, content):
        """Transform plaintext to an intermediate xml document.

        Args:
            content (str): the content of the plaintext document.

        Returns:
            An etree element.
        """
        document = etree.Element("document")
        header = etree.Element("header")
        body = etree.Element("body")

        ptext = ""

        for line_no, line in enumerate(content, start=1):
            if line_no not in self.metadata.skip_lines:
                if line.strip() == "":
                    if ptext.strip() != "":
                        body.append(self.make_element("p", ptext))
                    ptext = ""
                else:
                    ptext = ptext + line

        if ptext != "":
            body.append(self.make_element("p", ptext))

        document.append(header)
        document.append(body)

        return document


def convert2intermediate(filename):
    """Transform plaintext to an intermediate xml document.

    Args:
        filename (str): name of the file that should be converted

    Returns:
        An etree element.
    """
    converter = PlaintextConverter(filename)

    return converter.content2xml(io.StringIO(converter.to_unicode()))
