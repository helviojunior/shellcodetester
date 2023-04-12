#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import string, random, sys, re
import unicodedata
from tabulate import tabulate

from shell_libs.color import Color


class Tools:

    def __init__(self):
        pass

    @staticmethod
    def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    @staticmethod
    def clear_line():
        sys.stderr.write("\033[K")
        sys.stdout.write("\033[K")  # Clear to the end of line

        try:
            size = os.get_terminal_size(fd=os.STDOUT_FILENO)
        except:
            size = 50

        print((" " * size), end='\r', flush=True)
        print((" " * size), file=sys.stderr, end='\r', flush=True)

    @staticmethod     
    def permited_char(s):
        if s.isalpha():
            return True
        elif bool(re.match("^[A-Za-z0-9:]*$", s)):
            return True
        elif s == ".":
            return True
        elif s == ",":
            return True
        else:
            return False

    @staticmethod
    def mandatory():
        Color.pl('{!} {R}error: missing a mandatory option, use -h help{W}\r\n')
        Tools.exit_gracefully(1)

    @staticmethod
    def exit_gracefully(code=0):
        exit(code)

    @staticmethod
    def count_file_lines(filename: str):
        def _count_generator(reader):
            b = reader(1024 * 1024)
            while b:
                yield b
                b = reader(1024 * 1024)

        with open(filename, 'rb') as fp:
            c_generator = _count_generator(fp.raw.read)
            # count each \n
            count = sum(buffer.count(b'\n') for buffer in c_generator)
            return count + 1

    @staticmethod
    def clear_string(text):
        return ''.join(filter(Tools.permited_char, Tools.strip_accents(text))).strip().lower()

    @staticmethod
    def strip_accents(text):
        try:
            text = unicode(text, 'utf-8')
        except NameError:  # unicode is a default on python 3
            pass

        text = unicodedata.normalize('NFD', text) \
            .encode('ascii', 'ignore').decode("utf-8")

        return str(text).strip()

    @staticmethod
    def get_tabulated(data: list) -> str:

        if len(data) == 0:
            return ''

        headers = [(h if len(h) > 2 and h[0:2] != '__' else ' ') for h in data[0].keys()]
        data = [item.values() for item in data]

        return tabulate(data, headers, tablefmt='psql')

    @staticmethod
    def sizeof_fmt(num, suffix="B", start_unit=""):
        started = False
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if started or start_unit.upper() == unit:
                started = True
                if abs(num) < 1024.0:
                    return f"{num:3.1f} {unit}{suffix}"
                num /= 1024.0
        return f"{num:.1f} Y{suffix}"

    @staticmethod
    def is_platform_windows():
        import platform
        return platform.system().lower() == "windows"

    @staticmethod
    def is_platform_linux():
        import platform
        return platform.system().lower() == "linux"

    @staticmethod
    def find_index(data: [bytearray, bytes], pattern: [bytearray, bytes], start=0, end=-1):
        j = 0
        i = start
        if end == -1:
            l = len(data)
        else:
            l = end

        m = len(pattern)
        while (i < l) and (j < m):
            if int(data[i]) == int(pattern[j]):
                j += 1
            elif j == 1 and int(data[i]) == int(pattern[0]):
                j = 1
            else:
                j = 0
            i += 1

        if j == m:
            return i - m
        else:
            return -1

    @staticmethod
    def print_error(error: Exception):
        Color.pl('\n{!} {R}Error:{O} %s{W}' % str(error))

        Color.pl('\n{!} {O}Full stack trace below')
        from traceback import format_exc
        Color.p('\n{!}    ')
        err = format_exc().strip()
        err = err.replace('\n', '\n{W}{!} {W}   ')
        err = err.replace('  File', '{W}{D}File')
        err = err.replace('  Exception: ', '{R}Exception: {O}')
        Color.pl(err + '{W}')
