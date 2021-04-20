import _thread
import time
import random
import sys
sys.path.append('../')

from ECU_models.base_ECU import ECU_Sim
from bk_utils import ecu_constants as cons, flag


class ECU_Sim_Stage3(ECU_Sim):

    def __init__(self, ecu_nvm_path, ecu_memory_map_path):
        ECU_Sim.__init__(self, ecu_nvm_path, ecu_memory_map_path)

        # starting Tempomat Status Listener
        self.terminated = False
        self.x = _thread.start_new_thread(self.hotStuffListener, ())

        # Diagnostic related data:
        # permitAttempt is used for the determination of letting
        # the user authenticating or not.
        # seedSpace is used for the display of seed value
        # which is a deliberate vulnerability about exposing information
        # about the seed&key space to the attacker.
        self.permitAttempt = False
        self.seedSpace = '{0:03b}'
        self.seedSpace_bit = 3
        # Here, a security Constant value is created that shall be used during
        # diagnostic authentication as a key.
        # NOTE: this key shall be moved to the ECU memory upon startup.
        self.securityConstant = random.randint(0, 7)

        # Moving diagnostic key into memory.
        self.memoryMap['diagnosticKey'][cons.VAR_VALUE()] = self.securityConstant

        # entering tester mode
        self.enterTesterMode()

    ################ECU_FUNCTIONALITIES##########################
    # Here are the ECU functionalities defined.
    def hotStuffListener(self):
        while self.terminated == False:
            if self.diagMatrix['enableHotStuff'][cons.VAR_VALUE()] == True:
                print('\n!!!!!!!!!!!!!!HOT STUFF IS UNLOCKED!!!!!!!!!!!!!!!!!\n')
                flag.flag(b'Hot Stuff Challenge')
                self.terminated = True
                time.sleep(1)


nvm_path = './__data__/ecu_NVM_factory_reset_sportscar.json'
memory_map_path = './__data__/memory_map_factory_reset.json'
ecu = ECU_Sim_Stage3(nvm_path, memory_map_path)