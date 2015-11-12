# -*- coding:utf-8 -*-

#
#   Move a corpus file from oldpath to newpath
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
#   Copyright © 2015 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function

import argparse
import os
import sys

from corpustools import argparse_version
from corpustools import namechanger


def mover(oldpath, newpath):
    if os.path.isfile(oldpath):
        if oldpath.endswith('.xsl'):
            oldpath = oldpath[:-4]
    else:
        raise UserWarning('{} is not a file'.format(oldpath))

    if newpath.endswith('.xsl'):
        newpath = newpath[:-4]
    elif os.path.isdir(newpath):
        newpath = os.path.join(newpath,
                               os.path.basename(oldpath))

    cfmu = namechanger.CorpusFilesetMoverAndUpdater(
        oldpath.decode('utf8'),
        newpath.decode('utf8'))
    filepair = cfmu.mc.filepairs[0]
    print('\tmoving {} -> {}'.format(
        filepair.oldpath, filepair.newpath))
    cfmu.move_files()
    cfmu.update_own_metadata()
    cfmu.update_parallel_files_metadata()


def mover_parse_args():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Program to move or rename files inside the corpus.')

    parser.add_argument('oldpath',
                        help='The path of the old file.')
    parser.add_argument('newpath',
                        help='The place to move the file to. newpath can '
                        'be either a filename or a directory')

    return parser.parse_args()


def main():
    args = mover_parse_args()
    if args.oldpath == args.newpath:
        print('{} and {} are the same file'.format(args.oldpath, args.newpath), file=sys.stderr)
    else:
        try:
            mover(args.oldpath, args.newpath)
        except UserWarning as e:
            print('Can not move file:', str(e), file=sys.stderr)
