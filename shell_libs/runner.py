#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
from pathlib import Path

from shell_libs.process import Process

import sys
from shell_libs.color import Color
from shell_libs.tools import Tools


class Runner(object):

    def dependency_check(self):
        ''' Check that required programs are installed '''
        import platform

        required_apps = [
            {
                "name": "nasm",
                "windows": "Install NASM. Check how-to @ {G}https://github.com/helviojunior/shellcodetester/blob/master/WINDOWS.md{W}",
                "linux": "Run the command: {G}apt install nasm{W}",
                "darwin": ("Homebrew install instructions @ {G}https://docs.brew.sh/Installation{W}\n"
                           "And after that run the command: {G}brew install nasm{W}")
            },
            {
                "name": "gcc",
                "windows": "Install GCC. Check how-to @ {G}https://github.com/helviojunior/shellcodetester/blob/master/WINDOWS.md{W}",
                "linux": "Run the command: {G}apt install gcc{W}",
                "darwin": ("Homebrew install instructions @ {G}https://docs.brew.sh/Installation{W}\n"
                           "And after that run the command: {G}brew install gcc{W}")
            },
            {
                "name": "objdump",
                "windows": "Install BinUtils. Check how-to @ {G}https://github.com/helviojunior/shellcodetester/blob/master/WINDOWS.md{W}",
                "linux": "Run the command: {G}apt install binutils{W}",
                "darwin": ("Homebrew install instructions @ {G}https://docs.brew.sh/Installation{W}\n"
                           "And after that run the command: {G}brew install binutils{W}")
            },
        ]
        missing_required = False
        p = platform.system().lower()

        for app in required_apps:
            name = app.get("name", None)
            if name is not None and name.strip() != '':

                if p == 'windows' and name == 'gcc' and not Process.exists(name):
                    Runner.get_gcc()

                if not Process.exists(name):

                    missing_required = True
                    Color.pl('{!} {R}error: required app {O}%s{R} was not found' % name)

                    txt = app.get(p, "")
                    if txt is not None and txt.strip() != '':
                        Color.pl('{?} {O}Instructions to install dependency: ')
                        Color.pl('{W}%s{W}\n' % txt)

        if missing_required:
            Color.pl('{!} {R}required app(s) were not found, exiting.{W}')
            sys.exit(-1)

    @staticmethod
    def get_gcc():
        import requests
        requests.packages.urllib3.disable_warnings()

        Color.pl('{+} {GR}GCC not found, trying to get mingw-w64 gcc.{W}')
        try:
            r = requests.get('https://github.com/helviojunior/shellcodetester/releases/latest/download/mingw-latest.zip',
                             allow_redirects=True, verify=False, timeout=30)

            bin_path = os.path.join(Path(os.path.dirname(__file__)).resolve().parent, 'shell_bins', 'windows')
            with open(os.path.join(bin_path, 'mingw64.zip'), 'wb') as f:
                f.write(r.content)

            from zipfile import ZipFile
            with ZipFile(os.path.join(bin_path, 'mingw64.zip'), 'r') as zObject:
                zObject.extractall(path=bin_path)

            try:
                os.unlink(os.path.join(bin_path, 'mingw64.zip'))
            except:
                pass

        except Exception as e:
            Tools.print_error(e)

    def run(self):
        pass
