import _thread
import time
from datetime import datetime
import random
import sys
sys.path.append('../')
import os

from ECU_models.base_ECU import ECU_Sim
from bk_utils import ecu_constants as cons, flag


class ECU_Sim_Stage4(ECU_Sim):

    def __init__(self, ecu_nvm_path, ecu_memory_map_path):

        ECU_Sim.__init__(self, ecu_nvm_path, ecu_memory_map_path)

        # starting Coordinate Listener
        self.terminated = False
        self.x = _thread.start_new_thread(self.coordinateListener, ())

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
                        os.system('cls')
                        os.system('color 08')
                        break
                    elif command == "cls":
                        os.system('cls')
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
                        self.diagWrite(rx_data[1], int(rx_data[2]))
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

    ################ECU_FUNCTIONALITIES##########################
    # Here are the ECU functionalities defined.
    def coordinateListener(self):
        while self.terminated == False:
            if self.diagMatrix['destCoordLat'][cons.VAR_VALUE()] == 49.0 and \
                    self.diagMatrix['destCoordLong'][cons.VAR_VALUE()] == 61.0:
                print('\n!!!!!!!!!!!!!!COORDINATES UPDATED!!!!!!!!!!!!!!!!!\n')
                flag.flag(b'Coordinates Challenge')
                self.terminated = True
                time.sleep(1)

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


nvm_path = './__data__/ecu_NVM_factory_reset_atlas.json'
memory_map_path = './__data__/memory_map_factory_reset.json'
ecu = ECU_Sim_Stage4(nvm_path, memory_map_path)