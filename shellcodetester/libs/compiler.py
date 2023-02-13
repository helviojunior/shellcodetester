import errno
import sys
from pathlib import Path

from shellcodetester.config import Configuration
from shellcodetester.libs.asmfile import AsmFile
from shellcodetester.libs.transform import Transform
from shellcodetester.util.logger import Logger
from shellcodetester.util.process import Process
from shellcodetester.util.tools import Tools

_extensions = {
    'windows': '.exe',
    'linux': '',
    'darwin': '',
}


class Compiler(AsmFile):
    c_file = ''
    bin_file = ''
    assembled_data = None

    def __init__(self, filename: str, assembled_data: bytearray):
        super().__init__(filename)
        self.assembled_data = assembled_data
        self.c_file = Path(f"{self.file_pattern}.c")
        self.bin_file = Path(f"{self.get_name()}")

    def get_name(self) -> str:
        import platform
        p = platform.system().lower()
        e = _extensions.get(p, "")
        return f"{self.file_pattern}-{self.arch}{e}"

    def compile(self) -> bool:

        if len(self.assembled_data) == 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}: Assembled data is empty{W}' % self.file_path.name)
            return False

        Logger.debug("Writing C source code to {G}%s" % self.c_file)
        try:

            if self.c_file.is_file() and self.c_file.exists():
                self.c_file.unlink(missing_ok=True)

            with open(self.c_file, 'w', encoding="utf-8") as f:
                f.write('#include<stdio.h>\n')
                f.write('#include<string.h>\n')
                f.write('\n')
                f.write('void main() {\n')
                f.write('\n')
                f.write(f'    int size = {len(self.assembled_data)};\n')
                f.write('    printf("Shellcode Length:  %d\\n", size);\n')
                f.write('\n')
                f.write('    shell();\n')
                f.write('}\n')
                f.write('\n')
                f.write('void shell() {\n')

                if Configuration.breakpoint:
                    f.write('    asm("INT3"); // INT3 -> Breakpoint\n')

                pattern = bytearray(b'\x40\x41\x42\x43\x44\x45\x46\x47')

                f.write('    asm("inc %eax");\n')
                f.write('    asm("inc %ecx");\n')
                f.write('    asm("inc %edx");\n')
                f.write('    asm("inc %ebx");\n')
                f.write('    asm("inc %esp");\n')
                f.write('    asm("inc %ebp");\n')
                f.write('    asm("inc %esi");\n')
                f.write('    asm("inc %edi");\n')

                for n in range(len(self.assembled_data)):
                    f.write('    asm("NOP");\n')
                    pattern.append(0x90)

                f.write('    asm("NOP");\n')
                f.write('    asm("inc %edi");\n')
                f.write('    asm("inc %esi");\n')
                f.write('    asm("inc %ebp");\n')
                f.write('    asm("inc %esp");\n')
                f.write('    asm("inc %ebx");\n')
                f.write('    asm("inc %edx");\n')
                f.write('    asm("inc %ecx");\n')
                f.write('    asm("inc %eax");\n')

                pattern += bytearray(b'\x90\x47\x46\x45\x44\x43\x42\x41\x40')

                if Configuration.fill:
                    for n in range(4096 - len(self.assembled_data)):
                        f.write('    asm("NOP");\n')

                f.write('}\n')
                pass

        except IOError as x:
            if x.errno == errno.EACCES:
                Logger.pl('{!} {R}error: could not open output file to write {O}permission denied{R}{W}\r\n')
                raise x
            elif x.errno == errno.EISDIR:
                Logger.pl('{!} {R}error: could not open output file to write {O}it is an directory{R}{W}\r\n')
                raise x
            else:
                Logger.pl('{!} {R}error: could not open output file to write{W}\r\n')
                raise x

        Logger.pl('{+} {W}Compiling {G}%s{W} binary to {O}%s{W}' % (
            self.arch, self.bin_file.resolve()))

        if self.bin_file.is_file() and self.bin_file.exists():
            self.bin_file.unlink(missing_ok=True)

        gcc_flags = '-fno-stack-protector'
        if not Tools.is_platform_windows():
            gcc_flags = ' -z execstack'
        if self.arch == 'x86':
            gcc_flags += ' -m32'

        # gcc source.c -o executable_file $gcc_flags -fno-stack-protector -z execstack
        (code, out, err) = Process.call(f"gcc \"{self.c_file.resolve()}\" -o \"{self.bin_file.resolve()}\" {gcc_flags}")
        if code != 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}:{O} \n{W}%s{W}' % (self.file_path.name, err))
            return False

        stat = self.bin_file.stat()
        if stat.st_size == 0:
            Logger.pl('{!} {R}Error compiling {G}%s{R}:{O} %s{W}' % (self.file_path.name, 'Output file is empty'))
            return False

        Logger.debug("File compiled with {G}%s bytes" % stat.st_size)

        if not self.replace_onfile(self.bin_file, pattern, self.assembled_data):
            Logger.pl('{!} {R}Error putting the shellcode inside of executable file {G}%s{W}' % self.bin_file.name)
            return False

        if Tools.is_platform_windows():
            if Configuration.breakpoint:
                Logger.pl(
                    '\n{+} {W}To debug your shellcode open the following application in your debugger: \n     {O}%s{W}\n' % self.bin_file.resolve())
                return True

            Logger.pl('\n{+} {W}To run your shellcode execute the application: \n     {O}%s{W}\n' % self.bin_file.resolve())
        else:
            if Configuration.breakpoint:
                Logger.pl(
                    '\n{+} {W}To debug your shellcode execute the command: \n     {O}gdb -q %s{W}\n' % self.bin_file.resolve())
                return True

            Logger.pl('\n{+} {W}To execute your shellcode execute the command: \n     {O}%s{W}\n' % self.bin_file.resolve())
        return True

    def replace_onfile(self, filename: [str, Path], pattern: [bytearray, bytes], replace_to: [bytearray, bytes]) -> bool:
        file = Path(filename)
        stat = self.bin_file.stat()
        if stat.st_size == 0:
            Logger.pl('{!} {R}Error putting the shellcode at {G}%s{R}:{O} %s{W}' % (file.name, 'Executable file is empty'))
            return False

        with open(file.resolve(), 'rb') as f:
            bin_data = f.read(stat.st_size)

        idx = Tools.find_index(bin_data, pattern)
        if idx == -1:
            Logger.pl('{!} {R}Error putting the shellcode at {G}%s{R}:{O} %s{W}' % (file.name, 'Find pattern1 not found'))
            return False

        if idx + len(replace_to) > len(bin_data):
            Logger.pl(
                '{!} {R}Error putting the shellcode at {G}%s{R}:{O} %s{W}' % (file.name, 'replace_to data is greater than binary file'))
            return False

        p2 = bytearray(b'\x90\x47\x46\x45\x44\x43\x42\x41\x40')
        idx2 = Tools.find_index(bin_data, p2, idx + 5)
        if idx2 == -1:
            Logger.pl('{!} {R}Error putting the shellcode at {G}%s{R}:{O} %s{W}' % (file.name, 'Find pattern2 not found'))
            return False

        idx2 += len(p2)
        if len(replace_to) > idx2 - idx:
            Logger.pl(
                '{!} {R}Error putting the shellcode at {G}%s{R}:{O} %s{W}' % (file.name, 'replace_to data is greater than expected'))
            return False

        fill_data = bytearray(replace_to)

        for n in range((idx2 - idx) - len(replace_to)):
            fill_data.append(0x90)

        new_data = bin_data[0:idx] + fill_data + bin_data[idx2:]

        with open(file.resolve(), 'wb') as f:
            f.write(new_data)

        return True

