from pathlib import Path
from random import shuffle

from shellcodetester.config import Configuration
from shell_libs.logger import Logger

_x86Instruction = [
    {'asm': 'inc %eax', 'byte': b'\x40'},
    {'asm': 'inc %ecx', 'byte': b'\x41'},
    {'asm': 'inc %edx', 'byte': b'\x42'},
    {'asm': 'inc %ebx', 'byte': b'\x43'},
    {'asm': 'inc %esp', 'byte': b'\x44'},
    {'asm': 'inc %ebp', 'byte': b'\x45'},
    {'asm': 'inc %esi', 'byte': b'\x46'},
    {'asm': 'inc %edi', 'byte': b'\x47'},
    {'asm': 'dec %eax', 'byte': b'\x48'},
    {'asm': 'dec %ecx', 'byte': b'\x49'},
    {'asm': 'dec %edx', 'byte': b'\x4a'},
    {'asm': 'dec %ebx', 'byte': b'\x4b'},
    {'asm': 'dec %esp', 'byte': b'\x4c'},
    {'asm': 'dec %ebp', 'byte': b'\x4d'},
    {'asm': 'dec %esi', 'byte': b'\x4e'},
    {'asm': 'dec %edi', 'byte': b'\x4f'},
]

_x86_64Instruction = [
    {'asm': 'inc %rax', 'byte': b'\x48\xff\xc0'},
    {'asm': 'inc %rcx', 'byte': b'\x48\xff\xc1'},
    {'asm': 'inc %rdx', 'byte': b'\x48\xff\xc2'},
    {'asm': 'inc %rbx', 'byte': b'\x48\xff\xc3'},
    {'asm': 'inc %rsp', 'byte': b'\x48\xff\xc4'},
    {'asm': 'inc %rbp', 'byte': b'\x48\xff\xc5'},
    {'asm': 'inc %rsi', 'byte': b'\x48\xff\xc6'},
    {'asm': 'inc %rdi', 'byte': b'\x48\xff\xc7'},
    {'asm': 'dec %rax', 'byte': b'\x48\xff\xc8'},
    {'asm': 'dec %rcx', 'byte': b'\x48\xff\xc9'},
    {'asm': 'dec %rdx', 'byte': b'\x48\xff\xca'},
    {'asm': 'dec %rbx', 'byte': b'\x48\xff\xcb'},
    {'asm': 'dec %rsp', 'byte': b'\x48\xff\xcc'},
    {'asm': 'dec %rbp', 'byte': b'\x48\xff\xcd'},
    {'asm': 'dec %rsi', 'byte': b'\x48\xff\xce'},
    {'asm': 'dec %rdi', 'byte': b'\x48\xff\xcf'},
]


class AsmFile(object):
    file_path = ''
    file_pattern = ''
    arch = 'unsupported'
    assembled_data = None
    sign_data = []

    def __init__(self, filename: str):
        self.file_path = Path(filename)
        self.file_pattern = str(Path.joinpath(
            Path(Configuration.pwd),
            f'st_{self.file_path.name.replace(self.file_path.suffix, "")}').resolve())

        Logger.debug("Reading file {G}%s" % self.file_path.name)

        if self.file_path.exists():
            with open(self.file_path.resolve(), 'r', errors="surrogateescape") as f:
                line = f.readline()
                while line:

                    check_txt = line.strip(' \t')
                    if len(check_txt) > 0:
                        if check_txt[0] != "#" and check_txt[0] != ";":
                            if '[bits 64]' in line.lower():
                                self.arch = 'x86_64'
                                break

                            elif '[bits 32]' in line.lower():
                                self.arch = 'x86'
                                break

                    try:
                        line = f.readline()
                    except:
                        pass

        if self.arch == 'unsupported':
            raise Exception('Unknown or unsupported ASM architecture')

        lst = _x86Instruction
        if self.arch == 'x86_64':
            lst = _x86_64Instruction
        lst_idx = list(range(len(lst)))
        shuffle(lst_idx)
        lst_idx = lst_idx[0:7]

        self.sign_data = [lst[i] for i in lst_idx]

        Logger.debug("ASM architecture: {G}%s" % self.arch)
