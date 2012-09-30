import subprocess
import threading


class Command(object):
    def __init__(self, cmd, inputfile=None):
        self.cmd = " ".join(cmd)
        self.inputfile = inputfile
        self.result = None
        self.process = None

    def run(self, timeout):
        def target():
            print('starting proc')
            input = None
            if not self.inputfile is None:
                input = open(self.inputfile)

            self.process = subprocess.Popen(
                args=self.cmd,
                stdout=subprocess.PIPE,
                stdin=input,
                stderr=subprocess.STDOUT,
                shell=True
            )
            print('trying comms')
            out, err = self.process.communicate()
            self.result = out

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
            raise subprocess.CalledProcessError(
                cmd=self.cmd,
                returncode=-1,
                output='Timeout of %s seconds exceeded.' % timeout
            )
        if self.process.returncode != 0:
            raise subprocess.CalledProcessError(
                cmd=self.cmd,
                returncode=self.process.returncode,
                output=self.result
            )
        return self.result
