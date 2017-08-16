import os
import signal
from subprocess import Popen, PIPE, TimeoutExpired

FNULL = open(os.devnull, 'w')

class VM(object):
    """Utility to execute geth `evm` """

    def __init__(self,executable="evmbin", docker = False):
        self.executable = executable
        self.docker = docker

    def execute(self, code = None, codeFile = None, genesis = None, 
        gas = 4700000, price = None, json = False, statdump=True, 
        sender= None, receiver = None, memory=False,  input = None):

        if self.docker: 
            cmd = ['docker', 'run']
            # If any files are referenced, they need to be mounted
            if genesis is not None:
                cmd.append('-v')
                cmd.append('%s:%s' % (genesis,"/mounted_genesis"))
                genesis = "mounted_genesis"

            cmd.append( self.executable ) 
        else:
            cmd = [self.executable]

        if codeFile is not None :
            with open(codeFile,"r") as f: 
                code = f.read()

        if code is not None : 
            cmd.append("--code")
            cmd.append(code)


        if genesis is not None : 
            cmd.append("--chain")
            cmd.append(genesis)

        if gas is not None: 
            cmd.append("--gas")
            cmd.append("%s" % hex(gas)[2:])

        if price is not None:
            cmd.append("--gas-price")
            cmd.append("%d" % price)
        

        if sender is not None: 
            cmd.append("--from")
            cmd.append(sender)

        if receiver is not None:
            cmd.append("--to")
            cmd.append(receiver)

        if input is not None:
            cmd.append("--input")
            cmd.append(input)

        if json: 
            cmd.append("--json")

        print(" ".join(cmd))
        with Popen(cmd, stdout=PIPE, preexec_fn=os.setsid) as process:
            try:
                output = process.communicate(timeout=15)[0]
            except TimeoutExpired:
                os.killpg(process.pid, signal.SIGINT) # send signal to the process group
                output = process.communicate()[0]

        return output.decode().strip().split("\n")