from pathlib import Path

from shell_libs.asmfile import AsmFile
from shell_libs.disassembler import Disassembler
from shell_libs.transform import Transform
from shell_libs.logger import Logger
from shell_libs.process import Process
import tempfile, os


class InlineAssembler(AsmFile):
    o_file = ''
    assembled_data = None

    def __init__(self, instructions, arch: str = 'x86'):

        filename = os.path.join(tempfile.mkdtemp(), 'nasmshell.asm')
        if os.path.isfile(filename):
            os.unlink(filename)

        with open(filename, 'w', encoding='utf-8') as f:
            if arch.lower() == 'x86_64':
                f.write("[BITS 64]\n")
            else:
                f.write("[BITS 32]\n")

            f.write("section .text\n")
            f.write("_start:\n")

            if isinstance(instructions, str) and ';' in instructions:
                instructions = instructions.split(';')

            if isinstance(instructions, list):
                f.write('\n'.join(instructions))
            else:
                f.write(f"{instructions}\n")
            f.flush()

        super().__init__(filename)
        self.o_file = Path(f"{self.file_pattern}.o")

    def assembly(self) -> bool:

        if self.o_file.is_file() and self.o_file.exists():
            self.o_file.unlink(missing_ok=True)

        (code, out, err) = Process.call(f"nasm \"{self.file_path.resolve()}\" -o \"{self.o_file.resolve()}\"",
                                        cwd=self.file_path.parent.resolve())
        if code != 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}:{O} %s{W}' % (self.file_path.name, err))
            return False

        stat = self.o_file.stat()
        if stat.st_size == 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}:{O} %s{W}' % (self.file_path.name, 'Output file is empty'))
            return False

        with open(self.o_file.resolve(), 'rb') as f:
            self.assembled_data = f.read(stat.st_size)

        return True

    def get_disassembler(self) -> Disassembler:
        return Disassembler(
            filename=self.file_path.resolve(),
            assembled_data=bytearray(self.assembled_data)
        )

    def print_payload(self, format: str = 'c', bad_chars: [bytearray, bytes] = bytearray()):
        Logger.pl('{+} {W}Payload size: {G}%s{W} bytes{W}' % len(self.assembled_data))
        txt = Transform(
                    format=format,
                    line_size=16,
                    line_prefix=''
                ).format(self.assembled_data, bad_chars=bad_chars)
        Logger.pl('{+} {W}Final size of %s data: {G}%s{W} bytes{W}' % (Transform.get_name(format), len(txt)))
        Logger.pl('{W}%s\n' % txt)
