import sys
sys.path.append('../')
import zlib

from bk_utils import ecu_constants as cons
from ECU_models.base_ECU import ECU_Sim


class ECU_Sim_Stage6(ECU_Sim):

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
        # setting a static security constant for being able to use lookup table
        self.securityConstant = int(zlib.decompress(b'x\x9c31657\x01\x00\x03\x16\x01\x08'))

        # Turning on brute force protection.
        self.bruteForceProtectionEnable = True

        # Moving diagnostic key into memory.
        self.memoryMap['diagnosticKey'][cons.VAR_VALUE()] = self.securityConstant


nvm_path = './__data__/ecu_NVM_factory_reset_diplomat_target.json'
memory_map_path = './__data__/memory_map_factory_reset.json'
ecu = ECU_Sim_Stage6(nvm_path, memory_map_path)