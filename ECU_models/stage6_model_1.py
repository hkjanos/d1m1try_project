import os
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

        self.enterTesterMode()

    def authenticate(self):
        # This method is used for the verification of the
        # user's identity - or much more like the fact that
        # the user has the diagnostic authentication key.
        # Or the fact that the attacker accidentally hit
        # the proper answer.
        # The authenticate method takes the user's response as an argument.
        # Step 0) It is checked whether the ECU is powered on and a software is installed onto ECU.
        # Step 1) It is checked whether the authentication attempt is permitted by the ECU:
        #           It is forbidden to attempt authentication:
        #               - until a seed value is not requested explicitly.
        #               - after an unsuccessful attempt until a new seed value is requested.
        # Step 2) The expected response is calculated.
        # Step 3) If the expected response and the one sent by the user is equal,
        #         the permission is granted.
        # Step 4) If the expected response and the one sent by the user is not equal,
        #       it is handled with proper negative response.

        # Step 0:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled']:
            # Step 1:
            if self.permitAttempt:
                response = self.seedValue ^ self.memoryMap['diagnosticKey'][cons.VAR_VALUE()]
                print('sending response: ' + str(response))
                self.memoryMap['consecFailedAttempts'][cons.VAR_VALUE()] = 0
                self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] = cons.ELEVATED()
                result = cons.POS_R_PERM_GRANTED()
                print('Elevated Privilege Granted')

    # external
    def testerHelp(self):
        print("\n\nAvailable commands:\n\n"
              "BASIC COMMANDS:\n"
              "help - Returns a list of available commands\n"
              "ignition_on - Turns on the ignition (turning on the ECU)\n"
              "ignition_off - Turns off the ignition (turning off the ECU)\n"
              "ecustate - Returns the informations on the ECU\n"
              "getspeed - Returns the information on the vehicle speed\n"
              "setspeed *speed value* - Sets the vehicle speed\n"
              "checkmaneuver - Checks whether the vehicle currently is in a maneuver.\n"
              "readmemorymap - Returns the memory variables available via XCP\n\n"
              # "exit - exit program\n"
              "DIAGNOSTIC COMMANDS\n"
              "diagjobs2read - Returns a list of values permitted to read in current security level\n"
              "diagjobs2write - Returns a list of values permitted to write in current security level\n"
              "ecureset - Resets the ECU\n"
              "getseed - Requests seed for challenge&response authentication\n"
              "service_auth - Generate and send a response to the challenge for authentication\n"
              "diagread *variable name* - Read out variable according permissions\n"
              "diagwrite *variable name* *variable new value* - Writes variable according permissions\n\n"
              "XCP COMMANDS\n"
              "xcpcon - Initialized an XCP connection with ECU\n"
              "xcpdiscon - Disconnects XCP from ECU\n"
              "xcpread *variable name* - Reads out particular variable\n"
              "xcpwrite *variable name* *variable new value* - Updates particular variable\n"
              "xcp_rd_address *address* - Reads out particular memory address value\n"
              "xcp_wr_address *address* *value* - Writes data at particular memory area\n")

    def enterTesterMode(self):
        self.testerHelp()
        while True:
            command = input('TESTER> ')
            rx_data = command.split(' ')
            print(rx_data)
            if rx_data != ['']:
                try:
                    command = rx_data[0].lower()
                    if command == 'help':
                        self.testerHelp()
                    elif command == "ignition_on":
                        self.ignitionOn()
                        self.getECUState()
                    elif command == "ignition_off":
                        self.ignitionOff()
                        self.getECUState()
                    elif command == "ecustate":
                        self.getECUState()
                    elif command == "getspeed":
                        print(self.getVehicleSpeed())
                    elif command == "setspeed":
                        self.setVehicleSpeed(rx_data[1])
                    elif command == 'checkmaneuver':
                        self.checkManeuverStatus()
                    elif command == "exit":
                        os.system('cls')
                        os.system('color 08')
                        break
                    elif command == "cls":
                        os.system('cls')
                    elif command == "readmemorymap":
                        self.readMemoryMap()
                    elif command == "diagjobs2read":
                        self.enumDiagValuesToRead()
                    elif command == "diagjobs2write":
                        self.enumDiagValuesToWrite()
                    elif command == "ecureset":
                        self.ecuReset()
                    elif command == "getseed":
                        self.getSeed()
                    elif command == "service_auth":
                        self.authenticate()
                    elif command == "diagread":
                        self.diagRead(rx_data[1])
                    elif command == "diagwrite":
                        self.diagWrite(rx_data[1], float(rx_data[2]))
                    elif command == "xcpcon":
                        self.xcpInit()
                    elif command == "xcpdiscon":
                        self.xcpDispose()
                    elif command == "xcpread":
                        print(self.xcpRead(rx_data[1]))
                    elif command == "xcpwrite":
                        self.xcpWrite(rx_data[1], rx_data[2])
                    elif command == "xcp_rd_address":
                        print(self.xcpReadByAddress(rx_data[1]))
                    elif command == "xcp_wr_address":
                        print(self.xcpWriteByAddress(rx_data[1], rx_data[2]))
                    else:
                        print("Command does not exist.")
                except:
                    print("Malformed command.")


nvm_path = './__data__/ecu_NVM_factory_reset_diplomat.json'
memory_map_path = './__data__/memory_map_factory_reset.json'
ecu = ECU_Sim_Stage6(nvm_path, memory_map_path)