import errno
from pathlib import Path

from shellcodetester.config import Configuration
from shell_libs.asmfile import AsmFile
from shell_libs.logger import Logger
from shell_libs.process import Process
from shell_libs.tools import Tools

_extensions = {
    'windows': '.exe',
    'linux': '',
    'darwin': '',
}


class Compiler(AsmFile):
    c_file = ''
    bin_file = ''
    assembled_data = None
    bad_chars = None
    remove_bad_chars = False
    writable_text = False

    def __init__(self, filename: str,
                 assembled_data: bytearray,
                 bad_chars: [bytearray, bytes] = bytearray(),
                 remove_bad_chars: bool = False,
                 writable_text: bool = False):
        super().__init__(filename)
        self.assembled_data = assembled_data
        self.c_file = Path(f"{self.file_pattern}.c")
        self.bin_file = Path(f"{self.get_name()}")
        self.bad_chars = bytearray([b for b in bad_chars])
        self.remove_bad_chars = remove_bad_chars
        self.writable_text = writable_text

    def get_name(self) -> str:
        import platform
        p = platform.system().lower()
        e = _extensions.get(p, "")
        return f"{self.file_pattern}-{self.arch}{e}"

    def compile(self) -> bool:

        if len(self.assembled_data) == 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}: Assembled data is empty{W}' % self.file_path.name)
            return False

        start_sign = self.sign_data
        end_sign = reversed(start_sign)

        Logger.debug("Writing C source code to {G}%s" % self.c_file)
        try:

            if self.c_file.is_file() and self.c_file.exists():
                self.c_file.unlink(missing_ok=True)

            with open(self.c_file, 'w', encoding="utf-8") as f:
                f.write('#include<stdio.h>\n')
                f.write('#include<stdlib.h>\n')
                f.write('#include<unistd.h>\n')
                f.write('#include<errno.h>\n')
                f.write('#include<string.h>\n')
                f.write('#include<time.h>\n')
                f.write('\n')
                f.write(
                    '#if defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__) || defined(WIN64) || defined(_WIN64) || defined(__WIN64__)\n')
                f.write('    #include <windows.h>\n')
                f.write('#elif __APPLE__\n')
                f.write('    #include <TargetConditionals.h>\n')
                f.write('    #if TARGET_IPHONE_SIMULATOR\n')
                f.write('         // iOS, tvOS, or watchOS Simulator\n')
                f.write('    #elif TARGET_OS_MACCATALYST\n')
                f.write('         // Macs Catalyst (ports iOS API into Mac, like UIKit).\n')
                f.write('    #elif TARGET_OS_IPHONE\n')
                f.write('        // iOS, tvOS, or watchOS device\n')
                f.write('    #elif TARGET_OS_MAC\n')
                f.write('        // Other kinds of Apple platforms\n')
                f.write('    #else\n')
                f.write('    #   error "Unknown Apple platform"\n')
                f.write('    #endif\n')
                f.write('#elif __linux__\n')
                f.write('    // linux\n')
                f.write('    #include <sys/mman.h>\n')
                f.write('#elif __unix__ // all unices not caught above\n')
                f.write('    // Unix\n')
                f.write('#elif defined(_POSIX_VERSION)\n')
                f.write('    // POSIX\n')
                f.write('#else\n')
                f.write('#   error "Unknown compiler"\n')
                f.write('#endif\n')
                f.write('\n')
                f.write('char ZEROARRAY[1024] = {0};\n')
                f.write('\n')
                f.write('void shell(int*, int*);\n')
                f.write('void code_cave();\n')
                f.write('int wtext();\n')
                f.write('int end_of_code();\n')
                f.write('\n')
                f.write('int main() {\n')
                f.write('\n')
                f.write(f'    int size = {len(self.assembled_data)};\n')
                f.write('    size_t size2 = sizeof(ZEROARRAY);\n')
                f.write('    printf("Shellcode Length: %d\\n", size);\n')

                if self.arch == 'x86':
                    f.write('    printf("edi = %p => code cave\\n", &code_cave);\n')
                    f.write('    printf("esi = %p => writable memory (%zd bytes)\\n", &ZEROARRAY, size2);\n')
                elif self.arch == 'x86_64':
                    f.write('    printf("rdi = %p => code cave\\n", &code_cave);\n')
                    f.write('    printf("rsi = %p => writable memory (%zd bytes)\\n", &ZEROARRAY, size2);\n')

                f.write('\n')
                f.write('    if (wtext()) {\n')
                f.write('       printf("Error setting .text permission");\n')
                f.write('       return 1;\n')
                f.write('    }\n')
                f.write('    shell(&code_cave, &ZEROARRAY);\n')
                f.write('    return 0;\n')
                f.write('}\n')
                f.write('\n')

                f.write('int wtext(){\n')
                if self.writable_text:
                    f.write('''
    long        page = 4096;
    intptr_t    start_addr = (intptr_t)0x00;
    intptr_t    end_addr = (intptr_t)0x00;

    #if defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__) || defined(WIN64) || defined(_WIN64) || defined(__WIN64__)
        SYSTEM_INFO si;
        GetSystemInfo(&si);
        page = (long)si.dwPageSize;
    #elif __linux__
        page = (long)sysconf(_SC_PAGESIZE);
    #else
        return errno;
    #endif

    // calculate max address    
    // main
    if ((intptr_t)main >= end_addr)
        end_addr = (intptr_t)main;
    // shell
    if ((intptr_t)shell >= end_addr)
        end_addr = (intptr_t)shell;
    // code_cave
    if ((intptr_t)code_cave >= end_addr)
        end_addr = (intptr_t)code_cave;
    // wtext
    if ((intptr_t)wtext >= end_addr)
        end_addr = (intptr_t)wtext;
    // end_of_code
    if ((intptr_t)end_of_code >= end_addr)
        end_addr = (intptr_t)end_of_code;


    // calculate min address
    start_addr = end_addr;
    // main
    if ((intptr_t)main <= start_addr)
        start_addr = (intptr_t)main;
    // shell
    if ((intptr_t)shell <= start_addr)
        start_addr = (intptr_t)shell;
    // code_cave
    if ((intptr_t)code_cave <= start_addr)
        start_addr = (intptr_t)code_cave;
    // wtext
    if ((intptr_t)wtext <= start_addr)
        start_addr = (intptr_t)wtext;
    // end_of_code
    if ((intptr_t)end_of_code <= start_addr)
        start_addr = (intptr_t)end_of_code;

    // calculate lenght
    size_t      length = (size_t)(end_addr - start_addr);
    if (length <= 10)
        length = page;
    length += (page - (length % page));

    // Calculate page boundary
    void *start = (char *)start_addr - ((long)start_addr % page);

    //printf("start = %x\\n", start);
    //printf("end_addr = %x\\n", end_addr);
    //printf("len = %d\\n", length);

    #if defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__) || defined(WIN64) || defined(_WIN64) || defined(__WIN64__)
        DWORD l=0;
        VirtualProtect(start, length, PAGE_EXECUTE_READWRITE, &l);
    #elif __linux__
        if (mprotect(start, length, PROT_READ | PROT_WRITE | PROT_EXEC) == -1)
            return errno;
    #else
        return errno;
    #endif

    return 0;
                    ''')
                else:
                    f.write('        return 0;\n')
                f.write('}\n')
                f.write('\n')

                f.write('void shell(int *code_cave, int *data) {\n')

                if self.arch == 'x86':
                    f.write('    asm("mov 0x8(%esp),%edi");\n')
                    f.write('    asm("mov 0xc(%esp),%esi");\n')

                if Configuration.breakpoint:
                    f.write('    asm("INT3"); // INT3 -> Breakpoint\n')

                f.write('    asm("NOP");\n')

                pattern = bytearray()
                for s in start_sign:
                    pattern += bytearray(s['byte'])
                    f.write('    asm("%s");\n' % s['asm'])

                for n in range(len(self.assembled_data)):
                    f.write('    asm("NOP");\n')
                    pattern.append(0x90)

                for s in end_sign:
                    pattern += bytearray(s['byte'])
                    f.write('    asm("%s");\n' % s['asm'])

                if Configuration.fill:
                    for n in range(4096 - len(self.assembled_data)):
                        f.write('    asm("NOP");\n')

                f.write('}\n')
                f.write('\n')

                f.write('void code_cave() {\n')

                for n in range(Configuration.cave_size):
                    f.write('    asm("NOP");\n')

                f.write('}\n')

                f.write('int end_of_code(){\n')
                f.write('   int i = 0;\n')
                f.write('   ++i + time(0); // time(0) is to prevent optimizer from just doing: return 1;\n')
                f.write('   return i;\n')
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
        # if not Tools.is_platform_windows():
        #    gcc_flags = ' -z execstack'
        if self.arch == 'x86':
            gcc_flags += ' -m32'

        # gcc source.c -o executable_file $gcc_flags -fno-stack-protector -z execstack
        (code, out, err) = Process.call(f"gcc \"{self.c_file.resolve()}\" -o \"{self.bin_file.resolve()}\" {gcc_flags}")
        if code != 0:
            Logger.pl('{!} {R}Error assembling {G}%s{R}:{O} \n{W}%s{W}' % (self.file_path.name, err))
            if 'stdio.h' in err and 'file not found' in err and Configuration.platform == 'macos':
                Logger.pl(('{R}NOTE: {GR}Try to run the following command before execute the shellcode tester: '
                           '{G}export SDKROOT=$(xcrun --sdk macosx --show-sdk-path){W}\n'))
            return False

        stat = self.bin_file.stat()
        if stat.st_size == 0:
            Logger.pl('{!} {R}Error compiling {G}%s{R}:{O} %s{W}' % (self.file_path.name, 'Output file is empty'))
            return False

        Logger.debug("File compiled with {G}%s bytes" % stat.st_size)

        if not self.replace_on_file(self.bin_file, pattern, self.assembled_data, self.bad_chars, self.remove_bad_chars):
            Logger.pl('{!} {R}Error putting the shellcode inside of executable file {G}%s{W}' % self.bin_file.name)
            return False

        if Tools.is_platform_windows():
            if Configuration.breakpoint:
                Logger.pl(
                    '\n{+} {W}To debug your shellcode open the following application in your debugger: \n    {O}%s{W}\n' % self.bin_file.resolve())
                return True
        else:
            if Configuration.breakpoint:
                Logger.pl(
                    '\n{+} {W}To debug your shellcode execute the command: \n    {O}gdb -q %s{W}\n' % self.bin_file.resolve())
                return True

        Logger.pl('\n{+} {W}To run your shellcode execute the command: \n    {O}%s{W}\n' % self.bin_file.resolve())
        return True

    def replace_on_file(self, filename: [str, Path],
                        pattern: [bytearray, bytes],
                        replace_to: [bytearray, bytes],
                        bad_chars: [bytearray, bytes] = bytearray(),
                        remove_bad_chars: bool = False) -> bool:
        file = Path(filename)
        stat = self.bin_file.stat()
        if stat.st_size == 0:
            Logger.pl(
                '{!} {R}Error putting the shellcode at {G}%s{R}:{O} %s{W}' % (file.name, 'Executable file is empty'))
            return False

        with open(file.resolve(), 'rb') as f:
            bin_data = f.read(stat.st_size)

        idx = Tools.find_index(bin_data, pattern)
        if idx == -1:
            Logger.pl(
                '{!} {R}Error putting the shellcode at {G}%s{R}:{O} %s{W}' % (file.name, 'Find pattern not found'))
            return False

        if idx + len(replace_to) > len(bin_data):
            Logger.pl(
                '{!} {R}Error putting the shellcode at {G}%s{R}:{O} %s{W}' % (
                file.name, 'replace_to data is greater than binary file'))
            return False

        fill_data = bytearray([
            b for b in replace_to
            if not remove_bad_chars or b not in bad_chars
        ])

        for n in range(len(pattern) - len(fill_data)):
            fill_data.append(0x90)

        new_data = bin_data[0:idx] + fill_data + bin_data[idx + len(pattern):]

        with open(file.resolve(), 'wb') as f:
            f.write(new_data)

        return True

