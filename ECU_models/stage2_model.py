import _thread
import time
import random
import sys
sys.path.append('../')
import os

from ECU_models.base_ECU import ECU_Sim
from bk_utils import ecu_constants as cons, flag


class ECU_Sim_Stage2(ECU_Sim):

    def __init__(self, ecu_nvm_path, ecu_memory_map_path):
        self.runtimeError = False
        ECU_Sim.__init__(self, ecu_nvm_path, ecu_memory_map_path)

        # Setting up connection and setting the ecu to powered on state.
        self.ecu_state_dict['powerOn'] = True

        # Setting vehicle speed 50, since the vehicle is on the move.
        self.setVehicleSpeed(50)

        # entering tester mode
        self.enterTesterMode()

    def testerHelp(self):
        # In this stage, ignition on and off shall not be used because the trucks are
        # already on their way at the moment of startup.
        # However, the powerOn variable inside ecu_state_dictionary is the key
        # for every ecu service to do. Hence, ignition_on and ignition_off are
        # replaced by tester_con and tester_discon in the user interface,
        # while staying the same at the backend.
        print("\n\nAvailable commands:\n\n"
              "BASIC COMMANDS:\n"
              "help - Returns a list of available commands\n"
              "tester_con - Connects tester to the vehicle.\n"
              "tester_discon - Disconnects tester to the vehicle.\n"
              "ecustate - Returns the informations on the ECU\n"
              "getspeed - Returns the information on the vehicle speed\n"
              "checkmaneuver - Checks whether the vehicle currently is in a maneuver.\n"
              "readmemorymap - Returns the memory variables available via XCP\n\n"
              # "exit - exit program\n"
              "DIAGNOSTIC COMMANDS\n"
              "params2read - Returns a list of values permitted to read in current security level\n"
              "params2write - Returns a list of values permitted to write in current security level\n"
              "ecureset - Resets the ECU\n"
              "getseed - Requests seed for challenge&response authentication\n"
              "authenticate *response value* - Responds the challenge for authentication\n"
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
                    elif command == "tester_con":
                        self.ignitionOn()
                        self.getECUState()
                    elif command == "tester_discon":
                        self.ignitionOff()
                        print('Disconnected.')
                    elif command == "ecustate":
                        self.getECUState()
                    elif command == "getspeed":
                        print(self.getVehicleSpeed())
                    elif command == 'checkmaneuver':
                        self.checkManeuverStatus()
                    elif command == "exit":
                        self.screen_handler.clear_screen()
                        os.system('color 08')
                        break
                    elif command == "cls":
                        self.screen_handler.clear_screen()
                    elif command == "readmemorymap":
                        self.readMemoryMap()
                    elif command == "params2read":
                        self.enumDiagValuesToRead()
                    elif command == "params2write":
                        self.enumDiagValuesToWrite()
                    elif command == "ecureset":
                        self.ecuReset()
                    elif command == "getseed":
                        self.getSeed()
                    elif command == "authenticate":
                        self.authenticate(rx_data[1])
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
                        self.xcpWrite(rx_data[1], int(rx_data[2]))
                    elif command == "xcp_rd_address":
                        print(self.xcpReadByAddress(rx_data[1]))
                    elif command == "xcp_wr_address":
                        print(self.xcpWriteByAddress(rx_data[1], int(rx_data[2])))
                    else:
                        print("Command does not exist.")
                except:
                    print("Malformed command.")


    ################ECU_FUNCTIONALITIES##########################
    # Here are the ECU functionalities defined.
    def ecuReset(self):
        # This function is for resetting the ECU.
        # Step 1) IgnitionOff - IgnitionOn, resetting memory map
        # Step 2) Checking whether the vehicle travels fast AND a maneuver is on.
        #           If so, then it informs the user that the ECU reset caused
        #           near accident situation.
        # Step 3) The ignition is set to On for the ECU to provide functionality.
        # Step 4) A random delay is added to simulate startup time of an ECU.
        # Step 5) Printing out ECU state after startup.
        if self.ecu_state_dict['softwareInstalled']:
            if self.memoryMap['privilegeLevel'] == cons.ELEVATED() or self.runtimeError:
                print('Resetting ECU...')
                self.ignitionOff()
                print(self.ecu_state_dict)
                if not self.runtimeError:
                    time.sleep(random.uniform(0.2, 2))
                    self.ignitionOn()
                    print(self.ecu_state_dict)
                self.factoryReset(self.memory_map_path)
                self.runtimeError = False
                if self.environment_dict['vehicleSpeed'] > 50 and self.environment_dict['maneuverOn']:
                    print('!!!!!!!!!!!!!!NEAR ACCIDENT SITUATION!!!!!!!!!!!!!!!!!')
            else:
                result = cons.NEG_R_PERMISSION_DENIED()
                print(self.decodeResponse(result))
        else:
            time.sleep(2)
            print("Timeout. No response from ECU.")
    ############ XCP FUNCTIONALITIES #################
    #external
    def xcpReadByAddress(self, address):
        # This method provides read possibility into ECU real-time memory content.
        # Step 0) It is checked whether the ECU is powered on and the conditions are correct for this operation.
        # Step 1) It is checked whether the XCP channel is initialized and the XCP read is enabled.
        # Step 2) It is checked whether the variable reference used is valid and is permitted to read.
        # Step 3) If all of Steps0-2 are okay, the requested variable value is returned.
        # Step 5) If Step 0-2 is not okay, it raise error Could not connect to ECU.

        # Step 0 and 1:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled'] \
                and self.ecu_state_dict['initializedXCP']:
            if self.checkXCPReadAvail():
                # Step 2:
                response = "0xd34d"
                if int(address) > 0xfff0:
                    self.runtimeError = True
                    self.ecuReset()
                    flag.flag(b'Debug DoS READ')
                    return ''
                for key in self.memoryMap:
                    if self.memoryMap[key][cons.VAR_ADDRESS()] == float(address) and \
                            self.memoryMap[key][cons.ACCESS_RD()]:
                        response = self.memoryMap[key][cons.VAR_VALUE()]
                        break
                return response
        # Step 5: Signaling that the conditions are not okay for an XCP channel
        else:
            print("Not established connection!")
            return "0xd34d"

    # external
    def xcpWriteByAddress(self, address, value):
        # This method provides read possibility into ECU real-time memory content.
        # Step 0) It is checked whether the ECU is powered on and the conditions are correct for this operation.
        # Step 1) It is checked whether the XCP channel is initialized and the XCP read is enabled.
        # Step 2) It is checked whether the variable reference used is valid and is permitted to write.
        # Step 3) If all of Steps0-2 are okay, the requested value is updated and a positive response is sent.
        # Step 4) If Step 0-2 is not okay, it returns error code.

        # Step 0 and 1:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled'] \
                and self.ecu_state_dict['initializedXCP']:
            if self.checkXCPReadAvail():
                # Step 2:
                response = "0xd34d"
                if int(address) > 0xfff0:
                    self.runtimeError = True
                    self.ecuReset()
                    flag.flag(b'Debug DoS WRITE')
                    return ''
                for key in self.memoryMap:
                    if self.memoryMap[key][cons.VAR_ADDRESS()] == float(address) and \
                            self.memoryMap[key][cons.ACCESS_WR()]:
                        self.memoryMap[key][cons.VAR_VALUE()] = float(value)
                        # Step 3:
                        response = (str(key) + " : " + str(value))
                        break
                return response
        else:
            print("Not established connection!")
            return "0xd34d"


nvm_path = './__data__/ecu_NVM_factory_reset.json'
memory_map_path = './__data__/memory_map_factory_reset.json'
ecu = ECU_Sim_Stage2(nvm_path, memory_map_path)