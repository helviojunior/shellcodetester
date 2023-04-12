# -*- coding: utf-8 -*-
import platform
import tempfile
import time
import signal
import os
from pathlib import Path

from subprocess import Popen, PIPE

from shell_libs.logger import Logger
from shell_libs.color import Color
from shellcodetester.config import Configuration


class Process(object):
    ''' Represents a running/ran process '''

    @staticmethod
    def devnull():
        ''' Helper method for opening devnull '''
        return open('/dev/null', 'w')

    @staticmethod
    def call(command, cwd=None, shell=False):
        '''
            Calls a command (either string or list of args).
            Returns tuple:
                (stdout, stderr)
        '''
        if type(command) is not str or ' ' in command or shell:
            shell = True
            if Configuration.verbose > 1:
                Logger.debug("Executing (Shell): {G}%s" % command)
        else:
            shell = False
            if Configuration.verbose > 1:
                Logger.debug("Executing (Shell): {G}%s" % command)

        # it cause hang on windows
        #pid = Popen(command, cwd=cwd, stdout=PIPE, stderr=PIPE, shell=shell)
        #retcode = pid.wait()
        #(stdout, stderr) = pid.communicate()

        my_env = os.environ.copy()
        my_env["PATH"] = Process.get_path()

        with tempfile.NamedTemporaryFile(mode="w+") as tmp_out, tempfile.NamedTemporaryFile(mode="w+") as tmp_err:

            pid = Popen(command, env=my_env, cwd=cwd, stdout=tmp_out, stderr=tmp_err, shell=shell)
            retcode = pid.wait()

            # Cursor is after the last write call, reset to read output
            tmp_out.seek(0)
            tmp_err.seek(0)
            stdout = tmp_out.read()
            stderr = tmp_err.read()

        if type(stdout) is bytes: stdout = stdout.decode('utf-8')
        if type(stderr) is bytes: stderr = stderr.decode('utf-8')

        if Configuration.verbose > 1 and stdout is not None and stdout.strip() != '':
            Color.pe("{P} [stdout] %s{W}" % '\n [stdout] '.join(stdout.strip().split('\n')))
        if Configuration.verbose > 1 and stderr is not None and stderr.strip() != '':
            Color.pe("{P} [stderr] %s{W}" % '\n [stderr] '.join(stderr.strip().split('\n')))

        return (retcode, stdout, stderr)

    @staticmethod
    def get_path():
        p = platform.system().lower()
        if p == 'darwin':
            p = 'macosx'

        bin_path = os.path.join(Path(os.path.dirname(__file__)).resolve().parent, 'shell_bins', p)
        my_env = os.environ.copy()
        if p == 'windows':
            mingw64_path = os.path.join(Path(os.path.dirname(__file__)).resolve().parent, 'shell_bins', p, 'mingw64', 'bin')
            return f"{bin_path};{mingw64_path};" + my_env["PATH"]
        else:
            return my_env["PATH"] + f":{bin_path}"

    @staticmethod
    def exists(program):
        ''' Checks if program is installed on this system '''
        #p = Process(['which', program])
        #stdout = p.stdout().strip()
        #stderr = p.stderr().strip()

        #if stdout == '' and stderr == '':
        #    return False

        #return True

        from shutil import which
        return which(program, path=Process.get_path()) is not None


    def __init__(self, command, devnull=False, stdout=PIPE, stderr=PIPE, cwd=None, bufsize=0):
        ''' Starts executing command '''

        if type(command) is str:
            # Commands have to be a list
            command = command.split(' ')

        self.command = command

        if Configuration.verbose > 1:
            Color.pe("\n {C}[?] {W} Executing: {B}%s{W}" % ' '.join(command))

        self.out = None
        self.err = None
        if devnull:
            sout = Process.devnull()
            serr = Process.devnull()
        else:
            sout = stdout
            serr = stderr

        self.start_time = time.time()

        self.pid = Popen(command, stdout=sout, stderr=serr, cwd=cwd, bufsize=bufsize)

    def __del__(self):
        '''
            Ran when object is GC'd.
            If process is still running at this point, it should die.
        '''
        if self.pid and self.pid.poll() is None:
            self.interrupt()

    def stdout(self):
        ''' Waits for process to finish, returns stdout output '''
        self.get_output()
        if Configuration.verbose > 1 and self.out is not None and self.out.strip() != '':
            Color.pe("{P} [stdout] %s{W}" % '\n [stdout] '.join(self.out.strip().split('\n')))
        return self.out

    def stderr(self):
        ''' Waits for process to finish, returns stderr output '''
        self.get_output()
        if Configuration.verbose > 1 and self.err is not None and self.err.strip() != '':
            Color.pe("{P} [stderr] %s{W}" % '\n [stderr] '.join(self.err.strip().split('\n')))
        return self.err

    def stdoutln(self):
        return self.pid.stdout.readline()

    def stderrln(self):
        return self.pid.stderr.readline()

    def get_output(self):
        ''' Waits for process to finish, sets stdout & stderr '''
        if self.pid.poll() is None:
            self.pid.wait()
        if self.out is None:
            (self.out, self.err) = self.pid.communicate()

        if type(self.out) is bytes:
            self.out = self.out.decode('utf-8')

        if type(self.err) is bytes:
            self.err = self.err.decode('utf-8')

        return (self.out, self.err)

    def poll(self):
        ''' Returns exit code if process is dead, otherwise "None" '''
        return self.pid.poll()

    def wait(self):
        self.pid.wait()

    def running_time(self):
        ''' Returns number of seconds since process was started '''
        return int(time.time() - self.start_time)

    def interrupt(self, wait_time=2.0):
        '''
            Send interrupt to current process.
            If process fails to exit within `wait_time` seconds, terminates it.
        '''
        try:
            pid = self.pid.pid
            cmd = self.command
            if type(cmd) is list:
                cmd = ' '.join(cmd)

            if Configuration.verbose > 1:
                Color.pe('\n {C}[?] {W} sending interrupt to PID %d (%s)' % (pid, cmd))

            os.kill(pid, signal.SIGINT)

            start_time = time.time()  # Time since Interrupt was sent
            while self.pid.poll() is None:
                # Process is still running
                time.sleep(0.1)
                if time.time() - start_time > wait_time:
                    # We waited too long for process to die, terminate it.
                    if Configuration.verbose > 1:
                        Color.pe('\n {C}[?] {W} Waited > %0.2f seconds for process to die, killing it' % wait_time)
                    os.kill(pid, signal.SIGTERM)
                    self.pid.terminate()
                    break

        except OSError as e:
            if 'No such process' in e.__str__():
                return
            raise e  # process cannot be killed

    @staticmethod
    def kill(code=0):
        ''' Deletes temp and exist with the given code '''

        os.kill(os.getpid(),signal.SIGTERM)

if __name__ == '__main__':
    p = Process('ls')
    print(p.stdout(), p.stderr())
    p.interrupt()

    # Calling as list of arguments
    (out, err) = Process.call(['ls', '-lah'])
    print(out, err)

    print('\n---------------------\n')

    # Calling as string
    (out, err) = Process.call('ls -l | head -2')
    print(out, err)

    print('"reaver" exists:', Process.exists('reaver'))

    # Test on never-ending process
    p = Process('yes')
    # After program loses reference to instance in 'p', process dies.