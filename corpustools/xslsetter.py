# -*- coding:utf-8 -*-

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
#   Copyright © 2013-2015 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function
from __future__ import unicode_literals

import lxml.etree as etree
import os
import sys


import util

here = os.path.dirname(__file__)


class XsltException(Exception):
    pass


class MetadataHandler(object):

    '''Class to handle metadata in .xsl files

    To convert the intermediate xml to a fullfledged  giellatekno document
    a combination of three xsl files + the intermediate files is needed
    This class makes the xsl file
    '''
    lang_key = "{http://www.w3.org/XML/1998/namespace}lang"

    def __init__(self, filename, create=False):
        self.filename = filename

        if not os.path.exists(filename):
            if not create:
                raise util.ArgumentError("{} does not exist!".format(filename))
            self.tree = etree.parse(os.path.join(here,
                                                 'xslt/XSL-template.xsl'))
        else:
            try:
                self.tree = etree.parse(filename)
            except etree.XMLSyntaxError as e:
                raise XsltException('Syntax error in {}:\n{}'.format(
                    self.filename, e))

    def _get_variable_elt(self, key):
        return self.tree.getroot().find(
            "{{http://www.w3.org/1999/XSL/Transform}}"
            "variable[@name='{}']".format(key))

    def set_variable(self, key, value):
        try:
            variable = self._get_variable_elt(key)
            variable.attrib['select'] = "'{}'".format(value)
        except AttributeError as e:
            print('Tried to update {} with value {}\n'
                  'Error was {}'.format(key, value, str(e)).encode('utf-8'),
                  file=sys.stderr)
            raise UserWarning

    def get_variable(self, key):
        variable = self._get_variable_elt(key)
        if variable is not None:
            value = variable.attrib['select']
            if value is not None:
                return value.replace("'", "")
        return None

    def get_parallel_texts(self):
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            return {}
        else:
            elts = parallels.findall("parallel_text")
            return {p.attrib[self.lang_key]: p.attrib["location"].strip("'")
                    for p in elts
                    if p.attrib["location"].strip("'") != ""}

    def set_parallel_text(self, language, location):
        attrib = {self.lang_key: language,
                  "location": location}
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            parallels = etree.Element(
                "{http://www.w3.org/1999/XSL/Transform}variable",
                name="parallels")
            parallels.text, parallels.tail = "\n", "\n\n"
            self.tree.getroot().append(parallels)
        elt = parallels.find("parallel_text[@{}='{}']".format(self.lang_key,
                                                              language))
        if elt is not None:
            elt.attrib.update(attrib)
        else:
            elt = etree.Element("parallel_text", attrib=attrib)
            elt.tail = "\n"
            parallels.append(elt)

    @property
    def skip_pages(self):
        '''Turn a skip_pages entry into a list of pages.'''
        pages = []
        skip_pages = self.get_variable('skip_pages')
        if skip_pages is not None:
            if 'odd' in skip_pages and 'even' in skip_pages:
                raise XsltException(
                    'Invalid format: Cannot have both "even" and "odd" in this line\n'
                    '{}'.format(skip_pages))

            if 'odd' in skip_pages:
                pages.append('odd')
                skip_pages = skip_pages.replace('odd', u'')
            if 'even' in skip_pages:
                pages.append('even')
                skip_pages = skip_pages.replace('even', '')

            # Turn single pages into single-page ranges, e.g. 7 → 7-7
            skip_ranges_norm = ((r if '-' in r else r + "-" + r)
                                for r in skip_pages.strip().split(",")
                                if r != "")

            skip_ranges = (tuple(map(int, r.split('-')))
                           for r in skip_ranges_norm)

            try:
                pages.extend([page
                              for start, end in sorted(skip_ranges)
                              for page in range(start, end + 1)])

            except ValueError:
                raise XsltException(
                    "Invalid format: {}".format(skip_pages))

        return pages

    def get_margin_lines(self):
        '''Get the margin lines from the metadata file.'''
        margin_lines = {
            key: self.get_variable(key).strip()
            for key in ['right_margin', 'top_margin', 'left_margin',
                        'bottom_margin']
            if (self.get_variable(key) is not None and
                self.get_variable(key).strip() != '')}

        return margin_lines

    @property
    def margins(self):
        '''Parse margin lines fetched from the .xsl file.'''
        margin_lines = self.get_margin_lines()
        _margins = {}
        for key, value in margin_lines.items():
            if ('all' in value and ('odd' in value or 'even' in value) or
                    '=' not in value):
                raise XsltException(
                    'Invalid format in the variable {} in the file:\n{}\n{}\n'
                    'Format must be [all|odd|even|pagenumber]=integer'.format(
                        key, self.filename, value))
            try:
                _margins[key] = self.parse_margin_line(value)
            except ValueError:
                raise XsltException(
                    'Invalid format in the variable {} in the file:\n{}\n{}\n'
                    'Format must be [all|odd|even|pagenumber]=integer'.format(
                        key, self.filename, value))

        return _margins

    @staticmethod
    def parse_margin_line(value):
        '''Parse a margin line read from the .xsl file.

        :param value: a string containing the margin settings for a particular
        margin (right_margin, left_margin, top_margin, bottom_margin)

        :returns: a dict containing the margins for pages in percent
        '''
        m = {}
        for part in value.split(','):
            (pages, margin) = tuple(part.split('='))
            for page in pages.split(';'):
                m[page.strip()] = int(margin)

        return m

    def write_file(self):
        try:
            with open(self.filename, 'w') as f:
                f.write(etree.tostring(self.tree,
                                       encoding="utf-8",
                                       xml_declaration=True))
        except IOError as e:
            print('cannot write', self.filename)
            print(e)
            sys.exit(254)
