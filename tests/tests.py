#reference: https://medium.com/assertqualityassurance/tutorial-de-pytest-para-iniciantes-cbdd81c6d761
import codecs

import pytest, sys

from shell_libs.color import Color
from shellcodetester import shellcodetester


def test_step_001():
    Color.pl('\n\n{+} Compiling x86...{W}')

    sys.argv = ['shellcodetester', 'asm', 'test_x86.asm']
    if sys.stdout.encoding is None:
        # Output is redirected to a file
        sys.stdout = codecs.getwriter('latin-1')(sys.stdout)

    try:

        shellcodetester.run()

        assert True
    except Exception as e:
        Color.pl('\n{!} {R}Error:{O} %s{W}' % str(e))

        Color.pl('\n{!} {O}Full stack trace below')
        from traceback import format_exc
        Color.p('\n{!}    ')
        err = format_exc().strip()
        err = err.replace('\n', '\n{W}{!} {W}   ')
        err = err.replace('  File', '{W}{D}File')
        err = err.replace('  Exception: ', '{R}Exception: {O}')
        Color.pl(err)

        assert False


def test_step_002():
    Color.pl('\n\n{+} Compiling x86_64...{W}')

    sys.argv = ['shellcodetester', 'asm', 'test_x86_64.asm']
    if sys.stdout.encoding is None:
        # Output is redirected to a file
        sys.stdout = codecs.getwriter('latin-1')(sys.stdout)

    try:

        shellcodetester.run()

        assert True
    except Exception as e:
        Color.pl('\n{!} {R}Error:{O} %s{W}' % str(e))

        Color.pl('\n{!} {O}Full stack trace below')
        from traceback import format_exc
        Color.p('\n{!}    ')
        err = format_exc().strip()
        err = err.replace('\n', '\n{W}{!} {W}   ')
        err = err.replace('  File', '{W}{D}File')
        err = err.replace('  Exception: ', '{R}Exception: {O}')
        Color.pl(err)

        assert False
