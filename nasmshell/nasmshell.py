import codecs
import sys

from shell_libs.color import Color
from shell_libs.disassembler import Disassembler
from shell_libs.logger import Logger
from shell_libs.runner import Runner
from .config import Configuration
from .libs import cmd
from shell_libs.inlineassembler import InlineAssembler


class NasmShell(cmd.Cmd):
    intro = '{+} Type {G}help{W} or {G}?{W} to list commands.\n'
    arch = 'x86'
    platform = ''
    method = 0
    prompt = '{R}┌─[{C}NASM Shell{R}]─[{G}ASM {O}→{G} Hex{R}]\n└──╼{O}➤{W} '

    file = None

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        if Configuration.quiet:
            self.intro = None

        self.arch = Configuration.arch
        self.platform = Configuration.platform
        self.method = int(Configuration.mode)

        self._setup()
        super().__init__(
            completekey=completekey,
            stdin=stdin,
            stdout=stdout
        )

    # ----- commands -----
    def do_method(self, arg):
        'Change method of work: (assembly or disassembly)'
        if len(arg) == 0 or arg is None:
            self.write_line("{!} {R}Invalid argument{W}")

        a = arg.lower()

        if a == 'assembly':
            self.method = 0
            self.write_line("{+} Method changed to {G}ASM {O}→{G} Hex{W}")
        elif a == 'disassembly':
            self.method = 1
            self.write_line("{+} Architecture changed to {G}Hex {O}→{G} ASM")
        else:
            self.write_line("{!} Invalid argument: {O}%s{W}" % arg)
        pass

    def do_arch(self, arg):
        'Set architecture: (x86 or x86_64)'
        if len(arg) == 0 or arg is None:
            self.write_line("{!} {R}Invalid argument{W}")

        a = arg.lower()

        if a == 'x86':
            self.arch = 'x86'
            self.write_line("{+} Architecture changed to {O}x86{W}")
        elif a == 'x86_64' or a == 'x64' or a == 'amd64':
            self.arch = 'x86_64'
            self.write_line("{+} Architecture changed to {O}x86_64{W}")
        else:
            self.write_line("{!} Invalid argument: {O}%s{W}" % arg)

    def do_exit(self, arg):
        'Exit Nasm Shell'
        self.write_line('')
        self.close()
        return True

    def default(self, inp):
        try:

            if inp == 'x' or inp == 'q':
                return self.do_exit(inp)

            if self.method == 0:
                asm = InlineAssembler(inp, arch=self.arch)
                asm.assembly()
                asm.print_payload(
                    bad_chars=Configuration.bad_chars,
                    format=Configuration.transform_format
                )
                Color.pl('{+} {W}Disassembly{W}')
                dis = asm.get_disassembler()
                dis.dump(
                    bad_chars=Configuration.bad_chars,
                    quiet=True
                )
            elif self.method == 1:
                txt = inp.lower()
                txt = txt.replace('\\x', ',')
                txt = txt.replace('0x', ',')
                txt = txt.replace(';', ',')
                txt = txt.replace(' ', ',')
                while ',,' in txt:
                    txt = txt.replace(',,', ',')
                txt = txt.strip(' ,')
                txt = '0' * (len(txt) % 2) + txt
                try:
                    if ',' not in txt:
                        txt = ','.join([txt[i:i + 2] for i in range(0, len(txt), 2)])

                    asm_data = list([
                        int(x, 16) for x in txt.split(',')
                        if x.strip() != ''
                    ])

                    if len(asm_data) == 0:
                        raise Exception('Data is empty')

                except Exception as e:
                    Logger.pl(
                        '{!} {R}error parsing Hex data: invalid hex data: {O}%s{W}\n' % (
                            str(e)))
                    sys.exit(1)

                asm = InlineAssembler(
                    instructions=[],
                    arch=Configuration.arch
                )
                asm.assembled_data = asm_data
                asm.print_payload(
                    bad_chars=Configuration.bad_chars,
                    format=Configuration.transform_format
                )

                Color.pl('{+} {W}Disassembly{W}')
                dis = Disassembler(
                    assembled_data=asm_data,
                    platform=Configuration.platform,
                    arch=Configuration.arch
                )
                dis.dump(
                    bad_chars=Configuration.bad_chars,
                    quiet=True
                )
            else:
                self.write_line("{!} Invalid command: {O}%s{W}" % inp)

        except Exception as e:
            self.write_line('\n{!} {R}Error:{O} %s{W}' % str(e))

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

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def _setup(self):
        if self.method == 1:
            self.prompt = (
                    '{R}┌─[{C}NASM Shell{R}]─[{G}%s %s{R}]─[{G}Hex {O}→{G} ASM{R}]\n└──╼{O}➤{W} ' % (
                self.arch,
                self.platform
            )
            )
        else:
            self.prompt = (
                    '{R}┌─[{C}NASM Shell{R}]─[{G}%s %s{R}]─[{G}ASM {O}→{G} Hex{R}]\n└──╼{O}➤{W} ' % (
                self.arch,
                self.platform
            )
            )

    do_EOF = do_exit
    help_EOF = do_exit

    def print_banner(self):
        """ Displays ASCII art of the highest caliber.  """
        Color.pl(Configuration.get_banner())


def run():  # Explicitly changing the stdout encoding format
    if sys.stdout.encoding is None:
        # Output is redirected to a file
        sys.stdout = codecs.getwriter('latin-1')(sys.stdout)

    Configuration.initialize()

    shell = NasmShell()
    shell.print_banner()

    try:

        r = Runner()
        r.dependency_check()

        shell.cmdloop()

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
