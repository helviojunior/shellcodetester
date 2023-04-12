import re
from pathlib import Path

from shell_libs.asmfile import AsmFile
from shell_libs.logger import Logger
from shell_libs.process import Process
import tempfile, os


class Disassembler(AsmFile):
    assembled_data = None
    platform = None

    def __init__(self, filename: str = '',
                 assembled_data: [bytearray, bytes] = bytearray(),
                 platform: str = '',
                 arch: str = 'unsupported'):

        write_data = False
        if isinstance(filename, Path):
            filename = str(Path(filename).resolve())

        if filename is None or filename.strip() == '':
            write_data = True
            filename = os.path.join(tempfile.mkdtemp(), 'nasmshell.o')
            if os.path.isfile(filename):
                os.unlink(filename)

        self.arch = arch

        if platform is None or platform.strip() == '':
            import platform as p
            self.platform = p.system().lower()
        else:
            self.platform = platform

        super().__init__(filename)
        self.assembled_data = assembled_data
        self.o_file = Path(f"{self.file_pattern}.o")

        if write_data:
            with open(self.o_file, 'wb') as f:
                f.write(bytearray(assembled_data))

    def dump(self, bad_chars: [bytearray, bytes] = bytearray(), quiet: bool = False):
        if not quiet:
            Logger.pl('{+} {W}Disassembly{W}')

        if self.platform == "darwin":
            cmd = f"objdump -D -Mintel,i386 \"{self.o_file.resolve()}\""
            if self.arch == 'x86_64':
                cmd = f"objdump -D -Mintel,x86-64 \"{self.o_file.resolve()}\""
        else:
            cmd = f"objdump -D -Mintel,i386 -b binary -m i386 \"{self.o_file.resolve()}\""
            if self.arch == 'x86_64':
                cmd = f"objdump -D -Mintel,x86-64 -b binary -m i386 \"{self.o_file.resolve()}\""

        (code, out, err) = Process.call(cmd)
        if code != 0:
            if err is not None and out is not None and len(err) == 0 and len(out) > 0:
                err = out
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

        if not quiet:
            Logger.pl(' ')
        for l in lines:
            search = re.search('(^[a-fA-F0-9 ]{1,20}:)(.*)', l, re.IGNORECASE)
            if search is not None:
                l_data = search.group(2)
                for b in bc:
                    l_data = (l_data + '\n').replace(b, '{R}%s{W}' % b).replace('\n', '')

                Logger.pl('{O}{D}%s{W}%s{W}' % (search.group(1), l_data))

        Logger.pl(' ')

