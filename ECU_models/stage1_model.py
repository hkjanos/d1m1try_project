import _thread
import time
import random
import sys
sys.path.append('../')

from ECU_models.base_ECU import ECU_Sim
from bk_utils import ecu_constants as cons, flag


class ECU_Sim_Stage1(ECU_Sim):

    def __init__(self, ecu_nvm_path, ecu_memory_map_path):
        self.runtime_error = False

        ECU_Sim.__init__(self, ecu_nvm_path, ecu_memory_map_path)

        # entering tester mode
        self.enterTesterMode()

    ################ECU_FUNCTIONALITIES##########################
    # Here are the ECU functionalities defined.

    def ecuReset(self):
        if self.ecu_state_dict['softwareInstalled']:
            print('Resetting ECU...')
            self.ignitionOff()
            print(self.ecu_state_dict)
            if int(self.getVehicleSpeed()) > 50 and self.environment_dict['maneuverOn']:
                print('!!!!!!!!!!!!!!NEAR ACCIDENT SITUATION!!!!!!!!!!!!!!!!!')
            flag.flag(b'Diagnostic Denial of Service')
            self.ignitionOn()
            self.factoryReset(self.memory_map_path)
            time.sleep(random.uniform(0.2, 2))
            print(self.ecu_state_dict)
        else:
            time.sleep(2)
            print('Timeout.')


nvm_path = './__data__/ecu_NVM_factory_reset.json'
memory_map_path = './__data__/memory_map_factory_reset.json'
ecu = ECU_Sim_Stage1(nvm_path, memory_map_path)