#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from shell_libs.color import Color

import argparse, sys


class Arguments(object):
    ''' Holds arguments used by the Shellcode Tester '''

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
        glob.add_argument('-asm',
                          action='store',
                          dest='asm_file',
                          metavar='[ASM file name]',
                          type=str,
                          help=Color.s('Assembly file to be assembled'))

        glob.add_argument('-o',
                          action='store',
                          dest='out_file',
                          metavar='[output file]',
                          type=str,
                          help=Color.s('Save output to disk (default: {G}none{W})'))

    def _add_custom_args(self, custom):
        custom.add_argument('--break-point',
                            action='store_true',
                            default=False,
                            dest='breakpoint',
                            help=Color.s('Set software breakpoint ({G}INT3{W}) before shellcode (default: {G}false{W})'))

        custom.add_argument('--bad-chars',
                            action='store',
                            dest='bad_chars',
                            metavar='[bad char list]',
                            type=str,
                            help=Color.s('List of bad chars to highlight (ex: {G}\\x00\\x0a{W}, default: {G}\\0x00{W})'))

        custom.add_argument('--remove',
                            action='store_true',
                            default=False,
                            dest='remove',
                            help=Color.s('Remove bad chars from final binary executable (EXE, ELF and Mach-O). (default: {G}false{W})'))

        custom.add_argument('--cave-size',
                            action='store',
                            dest='cave_size',
                            metavar='[size]',
                            type=int,
                            default=1024,
                            help=Color.s('Code cave size (default: {G}1024{W})'))

        custom.add_argument('--fill-with-nop',
                            action='store_true',
                            default=False,
                            dest='fill',
                            help=Color.s('Fill entire page with NOP (default: {G}false{W})'))

        custom.add_argument('--writable-text',
                            action='store_true',
                            default=False,
                            dest='writable_text',
                            help=Color.s('Mark the output .text section as writable{W}'))

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


