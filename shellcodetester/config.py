#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os, errno, sys
from pathlib import Path

from shell_libs.transform import Transform
from shell_libs.color import Color
from shell_libs.logger import Logger
from shell_libs.__meta__ import __version__, __title__, __author__, __description__, __url__


class Configuration(object):
    ''' Stores configuration variables and functions for Shellcode Tester. '''
    version = '0.0.0'
    name = ""

    initialized = False # Flag indicating config has been initialized
    verbose = 0
    cmd_line = ''
    asm_file = ''
    out_file = ''
    pwd = ''
    platform = ''
    remove = False
    transform_format = 0
    breakpoint = False
    fill = False
    bad_chars = bytearray([0x00])
    cave_size = 200
    writable_text = False

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
        import platform
        p = platform.system().lower()
        if p == 'darwin':
            p = 'macos'
        Configuration.platform = p

        config_check = 0

        list_formats = any(['--list' in word for word in sys.argv])

        if list_formats:
            Color.pl('{+} {W}Transform Formats')
            for f in Transform.format_list():
                Logger.pl('     {C}%s{W}' % f)

            sys.exit(1)

        args = Arguments().args

        a1 = sys.argv
        a1[0] = 'shellcodetester'
        for a in a1:
            Configuration.cmd_line += "%s " % a

        Configuration.verbose = args.verbose

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

        Color.pl('{+} {W}Startup parameters')
        Logger.pl('     {C}command line:{O} %s{W}' % Configuration.cmd_line)
        Logger.pl('     {C}platform:{O} %s{W}' % Configuration.platform)

        if Configuration.verbose > 0:
            Logger.setLevel(Configuration.verbose)

        Logger.pl('     {C}log level:{O} %s{W}' % (Logger.getLevelName(Logger.level)))

        if args.asm_file is None or args.asm_file.strip() == '':
            config_check = 1

        if config_check == 1:
            Configuration.mandatory()

        Configuration.asm_file = args.asm_file

        if args.out_file:
            Configuration.out_file = args.out_file

        Configuration.cave_size = int(args.cave_size)
        Configuration.breakpoint = args.breakpoint
        Configuration.remove = args.remove
        Configuration.fill = args.fill
        Configuration.writable_text = args.writable_text
        Configuration.transform_format = Transform.parse_format(args.transform_format)

        Logger.pl('     {C}writable .text section:{O} %s{W}' % Configuration.writable_text)
        Logger.pl('     {C}code cave size:{O} %s{W}' % Configuration.cave_size)
        Logger.pl('     {C}transform format:{O} %s{W}' % (Transform.get_name(Configuration.transform_format)))

        if len(Configuration.bad_chars) > 0:
            Logger.pl('     {C}bad chars:{O} %s{W}' % (', '.join([
                f"0x{format(x, '02x')}" for x in Configuration.bad_chars
            ])))
        else:
            Logger.pl('     {C}bad chars:{O} Empty{W}')
            Configuration.remove = False

        Logger.pl('     {C}remove bad chars:{O} %s{W}' % Configuration.remove)

        if not os.path.isfile(Configuration.asm_file):
            Color.pl('{!} {R}error: ASM file not found {O}%s{R}{W}\r\n' % Configuration.asm_file)
            sys.exit(1)

        try:
            with open(Configuration.asm_file, 'r') as f:
                # file opened for reading.
                pass
        except IOError as x:
            if x.errno == errno.EACCES:
                Logger.pl('{!} {R}error: could not open ASM file {O}permission denied{R}{W}\r\n')
                sys.exit(1)
            elif x.errno == errno.EISDIR:
                Logger.pl('{!} {R}error: could not open ASM file {O}it is an directory{R}{W}\r\n')
                sys.exit(1)
            else:
                Logger.pl('{!} {R}error: could not open ASM file {W}\r\n')
                sys.exit(1)

        if Configuration.out_file != '':
            try:
                with open(Configuration.out_file, 'a', encoding="utf-8") as f:
                    # file opened for writing. write to it here
                    Logger.out_file = Configuration.out_file
                    f.write(Color.sc(Configuration.get_banner()) + '\n')
                    f.write(Color.sc('{+} {W}Startup parameters') + '\n')
                    pass
            except IOError as x:
                if x.errno == errno.EACCES:
                    Color.pl('{!} {R}error: could not open output file to write {O}permission denied{R}{W}\r\n')
                    sys.exit(1)
                elif x.errno == errno.EISDIR:
                    Color.pl('{!} {R}error: could not open output file to write {O}it is an directory{R}{W}\r\n')
                    sys.exit(1)
                else:
                    Color.pl('{!} {R}error: could not open output file to write{W}\r\n')
                    sys.exit(1)

        print('  ')

    @staticmethod
    def mandatory():
        Color.pl('{!} {R}error: missing a mandatory option ({O}-asm{R}){G}, use -h help{W}\r\n')
        sys.exit(1)

    @staticmethod
    def get_banner():
            Configuration.version = str(__version__)

            return '''\

{G}%s {D}v%s{W}{G} by %s{W}
{W}{D}%s{W}
{C}{D}%s{W}
    ''' % (str(__title__), Configuration.version, __author__, __description__, __url__)


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
