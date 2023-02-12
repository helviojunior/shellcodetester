import errno
import sys
from pathlib import Path

from shellcodetester.config import Configuration
from shellcodetester.libs.asmfile import AsmFile
from shellcodetester.libs.transform import Transform
from shellcodetester.util.logger import Logger
from shellcodetester.util.process import Process
from shellcodetester.util.tools import Tools


class Compiler(AsmFile):
    c_file = ''
    bin_file = ''
    assembled_data = None

    def __init__(self, filename: str, assembled_data: bytearray):
        super().__init__(filename)
        self.assembled_data = assembled_data
        self.c_file = Path(f"{self.file_pattern}.c")
        if self.arch == 'x86_64':
            self.bin_file = Path(f"{self.file_pattern}.elf64")
        else:
            self.bin_file = Path(f"{self.file_pattern}.elf32")

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
                f.write('#include <sys/mman.h>\n')
                f.write('\n')
                f.write('unsigned char code[] = {\n')

                if Configuration.breakpoint:
                    f.write(Transform(
                        line_size=-1,
                        line_prefix='\t',
                        format='c'
                    ).format([0xCC]) + ', // INT3 -> Breakpoint\n')

                f.write(Transform(
                    line_size=16,
                    line_prefix='\t',
                    format='c'
                ).format(self.assembled_data) + '\n')

                if Configuration.fill:
                    f.write(', // Filled NOPs\n')
                    f.write(Transform(
                        line_size=16,
                        line_prefix='\t',
                        format='c'
                    ).format(bytes([0x90 for n in range((4096 - len(self.assembled_data)))])) + '\n')

                f.write('};\n')
                f.write('\n')
                f.write('void main()\n')
                f.write('{\n')
                f.write('\n')
                f.write('    char *shell;\n')
                f.write('    int size = sizeof(code);\n')
                f.write('    printf("Shellcode Length:  %d\\n", size);\n')
                f.write('\n')
                f.write(
                    '    shell = (char*)mmap(NULL, size, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_ANON|MAP_SHARED, -1, 0);\n')
                f.write('\n')
                f.write('    memcpy(shell,code,size);\n')
                f.write('\n')
                f.write('    int (*ret)() = (int(*)())shell;\n')
                f.write('\n')
                f.write('    ret();\n')
                f.write('\n')
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

        gcc_flags = '-fno-stack-protector -z execstack'
        if self.arch == 'x86':
            gcc_flags += ' -m32'

        # gcc $c_file -o $bin_file $gcc_flags -fno-stack-protector -z execstack
        (code, out, err) = Process.call(f"gcc \"{self.c_file.resolve()}\" -o \"{self.bin_file.resolve()}\" {gcc_flags}")
        if code != 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}: \n{W}%s{W}' % (self.file_path.name, err))
            return False

        stat = self.bin_file.stat()
        if stat.st_size == 0:
            Logger.pl('{!} {R}Error compiling {G}%s{R}: %s{W}' % (self.file_path.name, 'Output file is empty'))
            return False

        Logger.debug("File compiled with {G}%s bytes" % stat.st_size)

        if Configuration.breakpoint:
            Logger.pl(
                '\n{+} {W}To debug your shellcode execute the command: \n     {O}gdb -q %s{W}\n' % self.bin_file.resolve())
            return True

        Logger.pl('\n{+} {W}To execute your shellcode execute the command: \n     {O}%s{W}\n' % self.bin_file.resolve())
        return True




