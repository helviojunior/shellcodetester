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

        #self.dependency_check()

        Configuration.initialize()

        self.run()

    def dependency_check(self):
        ''' Check that required programs are installed '''
        required_apps = ["gcc", "nasm"]
        optional_apps = ["objdump"]
        missing_required = False
        missing_optional = False

        for app in required_apps:
            if not Process.exists(app):
                missing_required = True
                Color.pl('{!} {R}error: required app {O}%s{R} was not found' % app)

        for app in optional_apps:
            if not Process.exists(app):
                missing_optional = True
                Color.pl('{!} {O}warning: recommended app {R}%s{O} was not found' % app)

        if missing_required:
            Color.pl('{!} {R}required app(s) were not found, exiting.{W}')
            sys.exit(-1)

        if missing_optional:
            Color.pl('{!} {O}recommended app(s) were not found')
            Color.pl('{!} {O}ShellcodeTester may not work as expected{W}')

    def run(self):

        try:

            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            Logger.pl('{+} {C}start time {O}%s{W}' % timestamp)

            # Assembly ASM File
            asm = Assembler(Configuration.asm_file)
            asm.assembly()

            if Configuration.verbose >= 1 or any(bc in asm.assembled_data for bc in Configuration.bad_chars):
                dis = Disassembler(Configuration.asm_file, asm.assembled_data)
                dis.dump(Configuration.bad_chars)

            asm.print_payload(Configuration.transform_format, Configuration.bad_chars)

            comp = Compiler(Configuration.asm_file, asm.assembled_data)
            comp.compile()


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
