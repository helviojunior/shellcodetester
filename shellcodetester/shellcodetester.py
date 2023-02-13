#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import codecs

from .libs.assembler import Assembler
from .libs.compiler import Compiler
from .libs.disassembler import Disassembler
from .util.process import Process

try:
    from .config import Configuration
except (ValueError, ImportError) as e:
    raise Exception('You may need to run ShellcodeTester from the root directory (which includes README.md)', e)


import sys, datetime, time, os
from .util.color import Color
from .util.logger import Logger
from .util.tools import Tools


class ShellcodeTester(object):

    def main(self):
        ''' Either performs action based on arguments, or starts attack scanning '''

        self.dependency_check()

        Configuration.initialize()

        self.run()

    def dependency_check(self):
        ''' Check that required programs are installed '''
        import platform

        required_apps = [
            {
                "name": "nasm",
                "windows": "Install NASM. Check how-to @ {G}https://github.com/helviojunior/shellcodetester/blob/master/WINDOWS.md{W}",
                "linux": "Run the command: {G}apt install nasm{W}",
                "darwin": ("Homebrew install instructions @ {G}https://docs.brew.sh/Installation{W}\n"
                           "And after that run the command: {G}brew install nasm{W}")
            },
            {
                "name": "gcc",
                "windows": "Install GCC. Check how-to @ {G}https://github.com/helviojunior/shellcodetester/blob/master/WINDOWS.md{W}",
                "linux": "Run the command: {G}apt install gcc{W}",
                "darwin": ("Homebrew install instructions @ {G}https://docs.brew.sh/Installation{W}\n"
                           "And after that run the command: {G}brew install gcc{W}")
            },
            {
                "name": "objdump",
                "windows": "Install BinUtils. Check how-to @ {G}https://github.com/helviojunior/shellcodetester/blob/master/WINDOWS.md{W}",
                "linux": "Run the command: {G}apt install binutils{W}",
                "darwin": ("Homebrew install instructions @ {G}https://docs.brew.sh/Installation{W}\n"
                           "And after that run the command: {G}brew install binutils{W}")
            },
        ]
        missing_required = False

        for app in required_apps:
            name = app.get("name", None)
            if name is not None and name.strip() != '':
                if not Process.exists(name):
                    missing_required = True
                    Color.pl('{!} {R}error: required app {O}%s{R} was not found' % name)

                    p = platform.system().lower()
                    txt = app.get(p, "")
                    if txt is not None and txt.strip() != '':
                        Color.pl('{?} {O}Instructions to install dependency: ')
                        Color.pl('{W}%s{W}\n' % txt)

        if missing_required:
            Color.pl('{!} {R}required app(s) were not found, exiting.{W}')
            sys.exit(-1)

    def run(self):

        try:

            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            Logger.pl('{+} {C}start time {O}%s{W}' % timestamp)

            # Assembly ASM File
            asm = Assembler(Configuration.asm_file)
            if not asm.assembly():
                sys.exit(2)

            if Configuration.verbose >= 1 or any(bc in asm.assembled_data for bc in Configuration.bad_chars):
                dis = Disassembler(Configuration.asm_file, asm.assembled_data)
                dis.dump(Configuration.bad_chars)

            asm.print_payload(Configuration.transform_format, Configuration.bad_chars)

            comp = Compiler(Configuration.asm_file, asm.assembled_data)
            if not comp.compile():
                sys.exit(2)

        except Exception as e:
            Color.pl("\n{!} {R}Error: {O}%s" % str(e))
            if Configuration.verbose > 0 or True:
                Color.pl('\n{!} {O}Full stack trace below')
                from traceback import format_exc
                Color.p('\n{!}    ')
                err = format_exc().strip()
                err = err.replace('\n', '\n{W}{!} {W}   ')
                err = err.replace('  File', '{W}{D}File')
                err = err.replace('  Exception: ', '{R}Exception: {O}')
                Color.pl(err)
        except KeyboardInterrupt as e:
            raise e

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        Logger.pl('{+} {C}End time {O}%s{W}' % timestamp)
        print(' ')

    def print_banner(self):
        """ Displays ASCII art of the highest caliber.  """
        Color.pl(Configuration.get_banner())

def run():
    # Explicitly changing the stdout encoding format
    if sys.stdout.encoding is None:
        # Output is redirected to a file
        sys.stdout = codecs.getwriter('latin-1')(sys.stdout)

    o = ShellcodeTester()
    o.print_banner()

    try:
        o.main()

    except Exception as e:
        Color.pl('\n{!} {R}Error:{O} %s{W}' % str(e))

        if Configuration.verbose > 0 or True:
            Color.pl('\n{!} {O}Full stack trace below')
            from traceback import format_exc
            Color.p('\n{!}    ')
            err = format_exc().strip()
            err = err.replace('\n', '\n{W}{!} {W}   ')
            err = err.replace('  File', '{W}{D}File')
            err = err.replace('  Exception: ', '{R}Exception: {O}')
            Color.pl(err)

        Color.pl('\n{!} {R}Exiting{W}\n')

    except KeyboardInterrupt:
        Color.pl('\n{!} {O}interrupted, shutting down...{W}')

    Tools.exit_gracefully(2)
