from pathlib import Path

from shellcodetester.config import Configuration
from shellcodetester.util.logger import Logger


class AsmFile(object):
    file_path = ''
    file_pattern = ''
    arch = 'x86'
    assembled_data = None

    def __init__(self, filename: str):
        self.file_path = Path(filename)
        self.file_pattern = str(Path.joinpath(
            Path(Configuration.pwd),
            f'st_{self.file_path.name.replace(self.file_path.suffix, "")}').resolve())

        Logger.debug("Reading file {G}%s" % self.file_path.name)

        with open(self.file_path.resolve(), 'r', errors="surrogateescape") as f:
            line = f.readline()
            while line:

                check_txt = line.strip(' \t')
                if len(check_txt) > 0:
                    if check_txt[0] != "#" and check_txt[0] != ";":
                        if '[bits 64]' in line.lower():
                            self.arch = 'x86_64'
                            break

                try:
                    line = f.readline()
                except:
                    pass

        Logger.debug("ASM architecture: {G}%s" % self.arch)
