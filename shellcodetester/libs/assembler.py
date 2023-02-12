from pathlib import Path

from shellcodetester.libs.asmfile import AsmFile
from shellcodetester.libs.transform import Transform
from shellcodetester.util.logger import Logger
from shellcodetester.util.process import Process
from shellcodetester.util.tools import Tools


class Assembler(AsmFile):
    o_file = ''
    assembled_data = None

    def __init__(self, filename):
        super().__init__(filename)
        self.o_file = Path(f"{self.file_pattern}.o")

    def assembly(self) -> bool:

        Logger.pl('{+} {W}Assembling {G}%s{W} file {O}%s{W} to {O}%s{W}' % (
            self.arch, self.file_path.name, self.o_file.resolve()))

        if self.o_file.is_file() and self.o_file.exists():
            self.o_file.unlink(missing_ok=True)

        (code, out, err) = Process.call(f"nasm \"{self.file_path.resolve()}\" -o \"{self.o_file.resolve()}\"")
        if code != 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}: %s{W}' % (self.file_path.name, err))
            return False

        stat = self.o_file.stat()
        if stat.st_size == 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}: %s{W}' % (self.file_path.name, 'Output file is empty'))
            return False

        with open(self.o_file.resolve(), 'rb') as f:
            self.assembled_data = f.read(stat.st_size)

        Logger.debug("File assembled with {G}%s bytes" % len(self.assembled_data))

        return True

    def print_payload(self, format: str = 'c', bad_chars: [bytearray, bytes] = bytearray()):
        Logger.pl('{+} {W}Payload size: {G}%s{W} bytes{W}' % len(self.assembled_data))
        txt = Transform(
                    format=format,
                    line_size=16,
                    line_prefix=''
                ).format(self.assembled_data, bad_chars=bad_chars)
        Logger.pl('{+} {W}Final size of %s data: {G}%s{W} bytes{W}' % (Transform.get_name(format), len(txt)))
        Logger.pl('{W}%s\n' % txt)
