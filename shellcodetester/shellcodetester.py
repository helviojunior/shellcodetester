#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import codecs

from shell_libs.assembler import Assembler
from shell_libs.compiler import Compiler
from shell_libs.disassembler import Disassembler
from shell_libs.process import Process
from shell_libs.runner import Runner

try:
    from .config import Configuration
except (ValueError, ImportError) as e:
    raise Exception('You may need to run ShellcodeTester from the root directory (which includes README.md)', e)


import sys, datetime
from shell_libs.color import Color
from shell_libs.logger import Logger
from shell_libs.tools import Tools


class ShellcodeTester(Runner):

    def main(self):
        ''' Either performs action based on arguments, or starts attack scanning '''

        self.dependency_check()

        Configuration.initialize()

        self.run()

    def run(self):

        try:

            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            Logger.pl('{+} {C}Start time {O}%s{W}' % timestamp)

            # Assembly ASM File
            asm = Assembler(Configuration.asm_file)
            if not asm.assembly():
                sys.exit(2)

            if Configuration.verbose >= 1 or any(bc in asm.assembled_data for bc in Configuration.bad_chars):
                dis = Disassembler(Configuration.asm_file, asm.assembled_data)
                dis.dump(Configuration.bad_chars)

                fill_data = bytearray([
                    b for b in asm.assembled_data
                    if b not in Configuration.bad_chars
                ])

                if len(asm.assembled_data) != len(fill_data):
                    Logger.pl('{!} {R}Bad chars found. {GR}Disassembly without bad chars{W}')
                    dis = Disassembler(filename='', assembled_data=fill_data, platform=Configuration.platform, arch=asm.arch)
                    dis.dump(Configuration.bad_chars, quiet=True)

            asm.print_payload(Configuration.transform_format, Configuration.bad_chars)

            comp = Compiler(Configuration.asm_file,
                            asm.assembled_data,
                            Configuration.bad_chars,
                            Configuration.remove,
                            Configuration.writable_text)
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
