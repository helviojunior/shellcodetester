import re
from pathlib import Path

from shellcodetester.libs.asmfile import AsmFile
from shellcodetester.util.logger import Logger
from shellcodetester.util.process import Process


class Disassembler(AsmFile):
    assembled_data = None

    def __init__(self, filename: str, assembled_data: bytearray):
        super().__init__(filename)
        self.assembled_data = assembled_data
        self.o_file = Path(f"{self.file_pattern}.o")
        if self.arch == 'x86_64':
            self.bin_file = Path(f"{self.file_pattern}.elf64")
        else:
            self.bin_file = Path(f"{self.file_pattern}.elf32")

    def dump(self, bad_chars: [bytearray, bytes] = bytearray()):
        Logger.pl('{+} {W}Disassembly of {G}%s{W}' % self.o_file.name)
        cmd = f"objdump -D -Mintel,i386 -b binary -m i386 \"{self.o_file.resolve()}\""
        if self.arch == 'x86_64':
            cmd = f"objdump -D -Mintel,x86-64 -b binary -m i386 \"{self.o_file.resolve()}\""

        (code, out, err) = Process.call(cmd)
        if code != 0:
            Logger.pl('{!} {R}Error disassembling {G}%s{R}: %s{W}' % (self.file_path.name, err))
            return False

        out.replace('\r', '')

        idx = out.find('00000000 <.data>:')
        if idx > 0:
            out = out[idx:]

        lines = out.split('\n')
        if '<.data>:' in lines[0]:
            lines = lines[1:]

        bc = [format(x, '02x') for x in bad_chars] + [format(x, '02x').upper() for x in bad_chars]
        if 0x00 in bad_chars:
            bc += ['0x0 ', '0x0\n']

        Logger.pl(' ')
        for l in lines:
            search = re.search('(^[a-fA-F0-9 ]{1,20}:)(.*)', l, re.IGNORECASE)
            if search is not None:
                l_data = search.group(2)
                for b in bc:
                    l_data = (l_data + '\n').replace(b, '{R}%s{W}' % b).replace('\n', '')

                Logger.pl('{O}{D}%s{W}%s{W}' % (search.group(1), l_data))

        Logger.pl(' ')

