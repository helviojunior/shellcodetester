#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from shell_libs.process import Process

import sys
from shell_libs.color import Color


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

        for app in required_apps:
            name = app.get("name", None)
            if name is not None and name.strip() != '':
                if not Process.exists(name):
                    missing_required = True
                    Color.pl('{!} {R}error: required app {O}%s{R} was not found' % name)

                    p = platform.system().lower()
                    txt = app.get(p, "")
                    if txt is not None and txt.strip() != '':
                        Color.pl('{?} {O}Instructions to install dependency: ')
                        Color.pl('{W}%s{W}\n' % txt)

        if missing_required:
            Color.pl('{!} {R}required app(s) were not found, exiting.{W}')
            sys.exit(-1)

    def run(self):
        pass
