#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from shell_libs.color import Color

DEFAULT = 0
INFO = 1
DEBUG = 2

_levelToName = {
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    DEFAULT: 'DEFAULT',
}
_nameToLevel = {
    'INFO': INFO,
    'DEBUG': DEBUG,
    'DEFAULT': DEFAULT,
}


class Logger(object):
    ''' Helper object for easily printing colored text to the terminal. '''
    out_file = ''
    level = DEFAULT

    @staticmethod
    def setLevel(level):
        """
        Set the logging level of this logger.  level must be an int or a str.
        """
        Logger.level = Logger._checkLevel(level)

    @staticmethod
    def info(text):
        if Logger.level >= INFO:
            Logger.pl("{+} {W}%s{W}" % text)

    @staticmethod
    def debug(text):
        if Logger.level >= DEBUG:
            Logger.pl("{*} {W}{D}%s{W}" % text)

    @staticmethod
    def _checkLevel(level):
        if isinstance(level, int):
            rv = level
            if rv > DEBUG:
                rv = DEBUG
            if rv < 0:
                rv = DEFAULT
        elif str(level) == level:
            if level not in _nameToLevel:
                raise ValueError("Unknown level: %r" % level)
            rv = _nameToLevel[level]
        else:
            raise TypeError("Level not an integer or a valid string: %r" % level)
        return rv

    @staticmethod
    def getLevelName(level):
        """
        Return the textual or numeric representation of logging level 'level'.
        """
        result = _levelToName.get(level)
        if result is not None:
            return result
        result = _nameToLevel.get(level)
        if result is not None:
            return result
        return f"{level}"

    @staticmethod
    def pl(text):
        '''Prints text using colored format with trailing new line.'''
        Color.pl(text)

        if Logger.out_file != '':
            try:
                with open(Logger.out_file, "a") as text_file:
                    text_file.write(Color.sc(text) + '\n')
            except:
                pass

    @staticmethod
    def p(text):
        '''Prints text using colored format.'''
        Color.p(text)

        if Logger.out_file != '':
            try:
                with open(Logger.out_file, "a") as text_file:
                    text_file.write(Color.sc(text) + '\n')
            except:
                pass

    @staticmethod
    def pl_file(text):
        '''Prints text using colored format with trailing new line.'''

        if Logger.out_file != '':
            try:
                with open(Logger.out_file, "a") as text_file:
                    text_file.write(Color.sc(text) + '\n')
            except:
                Color.pl(text)
        else:
            Color.pl(text)