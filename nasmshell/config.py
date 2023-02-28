#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os, errno, sys
from pathlib import Path

from shell_libs.transform import Transform
from shell_libs.color import Color
from shell_libs.logger import Logger
from shell_libs.__meta__ import __version__, __title__, __author__, __description__, __url__
import platform

ASSEMBLY = 0
DISASSEMBLY = 1

_formatToMode = {
    ASSEMBLY: 'ASSEMBLY',
    DISASSEMBLY: 'DISASSEMBLY',
}
_nameToMode = {
    'ASSEMBLY': ASSEMBLY,
    'DISASSEMBLY': DISASSEMBLY
}

class Configuration(object):
    ''' Stores configuration variables and functions for NASM Shell. '''
    version = '0.0.0'
    name = ""

    initialized = False # Flag indicating config has been initialized
    verbose = 0
    cmd_line = ''
    pwd = ''
    transform_format = 0
    quiet = False
    arch = 'x86'
    platform = ''
    mode = 0
    bad_chars = bytearray()

    @staticmethod
    def initialize():
        '''
            Sets up default initial configuration values.
            Also sets config values based on command-line arguments.
        '''

        Configuration.version = str(__version__)
        Configuration.name = str(__name__)

        # Only initialize this class once
        if Configuration.initialized:
            return

        Configuration.initialized = True

        Configuration.verbose = 0  # Verbosity level.
        Configuration.print_stack_traces = True
        Configuration.pwd = str(Path('.').resolve())

        # Overwrite config values with arguments (if defined)
        Configuration.load_from_arguments()


    @staticmethod
    def load_from_arguments():
        ''' Sets configuration values based on Argument.args object '''
        from .args import Arguments

        config_check = 0

        list_formats = any(['--list' in word for word in sys.argv])

        if list_formats:
            Color.pl('{+} {W}Transform Formats')
            for f in Transform.format_list():
                Logger.pl('     {C}%s{W}' % f)

            sys.exit(1)

        Configuration.platform = platform.system().lower()
        args = Arguments().args

        a1 = sys.argv
        a1[0] = 'nasm_shell'
        for a in a1:
            Configuration.cmd_line += "%s " % a

        Configuration.verbose = args.verbose
        Configuration.quiet = args.quiet

        try:
            # Parse bad chars
            if args.bad_chars is not None and args.bad_chars.strip() != '':
                txt = args.bad_chars.lower()
                txt = txt.replace('\\x', ',')
                txt = txt.replace('0x', ',')
                txt = txt.replace(';', ',')
                txt = txt.strip(' ,')
                Configuration.bad_chars = sorted(set([
                    int(x, 16) for x in txt.split(',')
                    if x.strip() != ''
                ]))

        except Exception as x:
            Logger.pl('{!} {R}error: could not parse --bad-chars %s: %s {W}\r\n' % (args.bad_chars, x))
            sys.exit(1)

        if not Configuration.quiet:
            Logger.pl('{+} {W}Startup parameters')
            Logger.pl('     {C}command line:{O} %s{W}' % Configuration.cmd_line)

        if Configuration.verbose > 0:
            Logger.setLevel(Configuration.verbose)

        if not Configuration.quiet:
            Logger.pl('     {C}log level:{O} %s{W}' % (Logger.getLevelName(Logger.level)))

        if config_check == 1:
            Configuration.mandatory()

        Configuration.transform_format = Transform.parse_format(args.transform_format)

        arch = args.arch.lower()
        if arch == 'x86' or arch == '32':
            Configuration.arch = 'x86'
        elif arch == 'x86_64' or arch == 'amd64' or arch == '64':
            Configuration.arch = 'x86_64'
        else:
            Logger.pl('{!} {R}error: unrecognized arch {O}%s{R}. {W}Permitted values: {G}x86{W} and {G}x86_64{W}\n' % (arch))
            sys.exit(1)

        mode = args.mode.lower()
        if mode == 'assembly' or mode == 'as':
            Configuration.mode = ASSEMBLY
        elif mode == 'disassembly' or mode == 'dis':
            Configuration.mode = DISASSEMBLY
        else:
            Logger.pl(('{!} {R}error: unrecognized operational mode {O}%s{R}.'
                       ' {W}Permitted values: {G}assembly{W} and {G}disassembly{W}\n' % (mode)))
            sys.exit(1)

        p = args.platform.lower() if args.platform is not None else Configuration.platform
        if p == 'linux':
            Configuration.platform = 'linux'
        elif p == 'windows':
            Configuration.platform = 'windows'
        elif p == 'darwin':
            Configuration.platform = 'darwin'
        else:
            Logger.pl(('{!} {R}error: unrecognized platform {O}%s{R}.'
                       ' {W}Permitted values: {G}linux{W} and {G}windows{W}\n' % (p)))
            sys.exit(1)

        if not Configuration.quiet:
            Logger.pl('     {C}operational mode:{O} %s{W}' % _formatToMode[Configuration.mode])
            Logger.pl('     {C}platform:{O} %s{W}' % Configuration.platform)
            Logger.pl('     {C}architecture:{O} %s{W}' % Configuration.arch)
            Logger.pl('     {C}transform format:{O} %s{W}' % (Transform.get_name(Configuration.transform_format)))

        if not Configuration.quiet:
            if len(Configuration.bad_chars) > 0:
                Logger.pl('     {C}bad chars:{O} %s{W}' % (', '.join([
                        f"0x{format(x, '02x')}" for x in Configuration.bad_chars
                    ])))
            else:
                Logger.pl('     {C}bad chars:{O} Empty{W}')

        if not Configuration.quiet:
            print('  ')

    @staticmethod
    def mandatory():
        Color.pl('{!} {R}error: missing a mandatory option ({O}-asm{R}){G}, use -h help{W}\r\n')
        sys.exit(1)

    @staticmethod
    def get_banner():
        Configuration.quiet = any(['-q' in word or '--quiet' for word in sys.argv])
        if not Configuration.quiet:
            Configuration.version = str(__version__)

            return '''\

{G}%s {D}v%s{W}{G} by %s{W}
{W}{D}%s{W}
{C}{D}%s{W}
    ''' % (str(__title__), Configuration.version, __author__, __description__, __url__)
        else:
            return ''


    @staticmethod
    def dump():
        ''' (Colorful) string representation of the configuration '''
        from shell_libs.color import Color

        max_len = 20
        for key in Configuration.__dict__.keys():
            max_len = max(max_len, len(key))

        result  = Color.s('{W}%s  Value{W}\n' % 'Configuration Key'.ljust(max_len))
        result += Color.s('{W}%s------------------{W}\n' % ('-' * max_len))

        for (key,val) in sorted(Configuration.__dict__.items()):
            if key.startswith('__') or type(val) == staticmethod or val is None:
                continue
            result += Color.s("{G}%s {W} {C}%s{W}\n" % (key.ljust(max_len),val))
        return result
