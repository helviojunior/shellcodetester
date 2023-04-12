#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from shell_libs.color import Color

import argparse, sys


class Arguments(object):
    ''' Holds arguments used by the NASM Shell '''

    def __init__(self, custom_args=''):
        self.verbose = any(['-v' in word for word in sys.argv])
        self.args = self.get_arguments(custom_args)

    def _verbose(self, msg):
        if self.verbose:
            return Color.s(msg)
        else:
            return argparse.SUPPRESS

    def get_arguments(self, custom_args=''):
        ''' Returns parser.args() containing all program arguments '''

        parser = argparse.ArgumentParser(
            usage=argparse.SUPPRESS,
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=80,
                width=130))

        glob = parser.add_argument_group('General Setting')
        self._add_global_args(glob)

        custom_group = parser.add_argument_group('Custom Settings')
        self._add_custom_args(custom_group)

        if not custom_args == "":
            targs = custom_args.split()
            targs.pop(0)  # remove o path do arquivo python, mantendo somente os parametros
            return parser.parse_args(targs)
        else:
            return parser.parse_args()

    def _add_global_args(self, glob):
        glob.add_argument('--mode',
                          action='store',
                          dest='mode',
                          metavar='[mode]',
                          default='assembly',
                          type=str,
                          help=Color.s('Operation mode. (default: {G}assembly{W}, permitted: {G}assembly{W} and {G}disassembly{W})'))

        glob.add_argument('--arch',
                          action='store',
                          dest='arch',
                          metavar='[architecture]',
                          default='x86',
                          type=str,
                          help=Color.s('Architecture to assembly/disassembly. (default: {G}x86{W}, permitted: {G}x86_64{W} and {G}x86{W})'))

        glob.add_argument('--platform',
                          action='store',
                          dest='platform',
                          metavar='[platform]',
                          type=str,
                          help=Color.s('Platform. (permitted: {G}linux{W}, {G}windows{W} and {G}darwin{W})'))

    def _add_custom_args(self, custom):
        custom.add_argument('--bad-chars',
                            action='store',
                            dest='bad_chars',
                            metavar='[bad char list]',
                            type=str,
                            help=Color.s('List of bad chars to highlight (ex: {G}\\x00\\x0a{W}, default: {G}\\0x00{W})'))

        custom.add_argument('--list',
                            action='store_true',
                            default=False,
                            dest='format_list',
                            help=Color.s('List all supported output format{W}'))

        custom.add_argument('-f',
                            '--format',
                            action='store',
                            dest='transform_format',
                            metavar='[format]',
                            default='raw',
                            type=str,
                            help=Color.s('Output format (use {G}--list{W} formats to list){W}'))

        custom.add_argument('-v',
                            '--verbose',
                            action='count',
                            default=0,
                            dest='verbose',
                            help=Color.s(
                                'Shows more options ({G}-h -v{W}). Prints commands and outputs. (default: {G}quiet{W})'))

        custom.add_argument('-q',
                            '--quiet',
                            action='store_true',
                            default=False,
                            dest='quiet',
                            help=Color.s(
                                'Quiet mode, not show banners. (default: {G}false{W})'))

