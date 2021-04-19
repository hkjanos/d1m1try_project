import _thread
import time
from datetime import datetime
import random
import sys
sys.path.append('../')
import os

from ECU_models.base_ECU import ECU_Sim
from bk_utils import ecu_constants as cons, flag


class ECU_Sim_Stage5(ECU_Sim):

    def __init__(self, ecu_nvm_path, ecu_memory_map_path):

        ECU_Sim.__init__(self, ecu_nvm_path, ecu_memory_map_path)

        # Diagnostic related data:
        # permitAttempt is used for the determination of letting
        # the user authenticating or not.
        # seedSpace is used for the display of seed value
        # which is a deliberate vulnerability about exposing information
        # about the seed&key space to the attacker.
        self.permitAttempt = False
        self.seedSpace = '{0:16b}'
        self.seedSpace_bit = 16
        # Here, a security Constant value is created that shall be used during
        # diagnostic authentication as a key.
        # NOTE: this key shall be moved to the ECU memory upon startup.
        self.securityConstant = random.randint(0, 65535)
        # # The following line is for testing purpose only. Comment this out for normal operation.
        # print('securityConstant: '+str(self.securityConstant))

        # Turning on brute force protection.
        self.bruteForceProtectionEnable = True

        # entering tester mode
        self.enterTesterMode()

    ################ECU_FUNCTIONALITIES##########################

    def getTime(self):
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def bruteForceScripted(self, seedSpace):
        response = random.randint(0, (2**seedSpace-1))
        attempt = 0
        start_time = self.getTime()
        while self.authenticate(response) != cons.POS_R_PERM_GRANTED():
            # time.sleep(0.1)
            self.getSeed()
            print('Attempt: ' + str(attempt) + ' with response: ' + str(response))
            attempt += 1
        print('Brute force started: ' + str(start_time))
        print('Brute force succeeded: ' + str(self.getTime()))
        input('Brute force is finished, ECU pwned. Hit enter to return to tester mode.')
        self.enterTesterMode()


nvm_path = './__data__/ecu_NVM_factory_reset_looted.json'
memory_map_path = './__data__/memory_map_factory_reset_looted.json'
ecu = ECU_Sim_Stage5(nvm_path, memory_map_path)