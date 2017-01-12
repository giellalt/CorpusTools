# -*- coding: utf-8 -*-

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
#   Copyright © 2012-2016 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""This file contains classes to handle corpus filenames."""


from __future__ import absolute_import, print_function

import os

from corpustools import util, xslsetter


class CorpusPath(object):
    """Map filenames in a corpus.

    Args:
        path: path to a corpus file
    """

    def __init__(self, path):
        """Initialise the CorpusPath class."""
        self.pathcomponents = self.split_path(path)
        self.metadata = xslsetter.MetadataHandler(self.xsl, create=True)

    @staticmethod
    def split_path(path):
        """Map path to the original file.

        Args:
            path: a path to a corpus file

        Returns:
            A PathComponents namedtuple containing the components of the
            original file
        """
        def split_on_module(path):
            """Split the path in three parts.

            Args:
                path: a path to a corpus file

            Returns:
                tuple of str: part one is the corpus directory, the second
                    part is the module, the third part is the path of the
                    corpus file inside the corpus

            Raises:
                ValueError: the path is not part of a corpus.
            """
            for module in [u'goldstandard/orig', u'prestable/converted',
                           u'prestable/toktmx', u'prestable/tmx', u'orig',
                           u'converted', u'stable', u'toktmx', u'tmx']:
                module_dir = u'/' + module + u'/'
                if module_dir in path:
                    root, rest = path.split(module_dir)
                    return root, module, rest

            raise ValueError('File is not part of a corpus: {}'.format(path))

        # Ensure we have at least one / before module, for safer splitting:
        abspath = os.path.normpath(os.path.abspath(path))
        root, module, lang_etc = split_on_module(abspath)

        lang_etc_parts = lang_etc.split('/')
        (lang, genre, subdirs, basename) = (lang_etc_parts[0],
                                            lang_etc_parts[1],
                                            lang_etc_parts[2:-1],
                                            lang_etc_parts[-1])

        if 'orig' in module:
            if basename.endswith('.xsl'):
                basename = util.basename_noext(basename, '.xsl')
            elif basename.endswith('.log'):
                basename = util.basename_noext(basename, '.log')
        elif 'converted' in module or 'analysed' in module:
            basename = util.basename_noext(basename, '.xml')
        elif 'toktmx' in module:
            basename = util.basename_noext(basename, '.toktmx')
        elif 'tmx' in module:
            basename = util.basename_noext(basename, '.tmx')

        if '2' in lang and 'tmx' in module:
            lang = lang[:lang.find('2')]

        return util.PathComponents(root, 'orig', lang, genre,
                                   '/'.join(subdirs), basename)

    @property
    def orig(self):
        """Return the path of the original file."""
        return os.path.join(*list(self.pathcomponents))

    @property
    def xsl(self):
        """Return the path of the metadata file."""
        return self.orig + '.xsl'

    @property
    def log(self):
        """Return the path of the log file."""
        return self.orig + '.log'

    def name(self, module='orig', lang=None, name=None, extension=''):
        """Return a path based on the module and extension.

        Arguments:
            module (str): string containing some corpus module
            lang (str): string containing the language of the wanted name
            name (str): name of the wanted file
            extension (str): string containing a file extension
        """
        this_lang = self.pathcomponents.lang if lang is None else lang
        this_name = self.pathcomponents.basename if name is None else name

        return os.path.join(self.pathcomponents.root,
                            module,
                            this_lang,
                            self.pathcomponents.genre,
                            self.pathcomponents.subdirs,
                            this_name + extension)

    @property
    def converted(self):
        """Return the path to the converted file."""
        module = 'converted'
        if self.metadata.get_variable('conversion_status') == 'correct':
            module = 'goldstandard/converted'

        return self.name(module=module, extension='.xml')

    @property
    def prestable_converted(self):
        """Return the path to the prestable/converted file."""
        module = 'prestable/converted'
        if self.metadata.get_variable('conversion_status') == 'correct':
            module = 'prestable/goldstandard/converted'

        return self.name(module=module, extension='.xml')

    @property
    def analysed(self):
        """Return the path to analysed file."""
        return self.name(module='analysed', extension='.xml')

    def parallel(self, language):
        """Check if there is a parallel for language.

        Arguments:
            language (str): language of the parallel file.

        Returns:
            str: path to the parallel file if it exist, otherwise empty string
        """
        try:
            return self.name(
                lang=language,
                name=self.metadata.get_parallel_texts().get(language))
        except TypeError:
            return ''

    @property
    def parallels(self):
        """Return paths to all parallel files.

        Yields:
            str: path to the orig path of a parallel file.
        """
        for language, name in self.metadata.get_parallel_texts():
            yield self.name(lang=language, name=name)

    def tmx(self, language):
        """Name of the tmx file.

        Arguments:
            language (str): language of the parallel

        Returns:
            str: path to the tmx file
        """
        self.name(module='tmx',
                  lang=self.pathcomponents.lang + '2' + language,
                  extension='.tmx')

    def prestable_tmx(self, language):
        """Name of the prestable tmx file.

        Arguments:
            language (str): language of the parallel

        Returns:
            str: path to the prestable tmx file
        """
        self.name(module='prestable/tmx',
                  lang=self.pathcomponents.lang + '2' + language,
                  extension='.tmx')
