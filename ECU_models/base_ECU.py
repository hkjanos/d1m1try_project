import random
import time
import os
import _thread

from bk_utils import json_parser, ecu_constants as cons, formatter


class ECU_Sim():
    # This is the environment related data used by simulation logic.
    # Tried to keep it as minimal as possible to push the usage of
    # the virtual memory (called here Memory Map).
    environment_dict = {
        'vehicleSpeed': 0,
        'maneuverOn': False
    }

    def __init__(self, ecu_nvm_path, ecu_memory_map_path):
        screen_handler = formatter.Format()
        # Clearing screen to improve user experience.
        screen_handler.clear_screen()
        # Coloring the screen to oscilloscope green, because that is funky. :)
        os.system('color 02')

        # This dictionary contains the most vital information about the ECU.
        # powerOn means that the ECU is on or off.
        # ECU state dict, kept as minimal as possible to push the usage of
        # the virtual memory (called Memory Map).
        # powerOn is used for determination of the operating status of the ECU.
        #           In other words: the availability of some services depends on it.
        #           PS: it is also used in stages where the ECU is considered
        #               as powered on, and only the tester connection needs
        #               to be initialized.
        # softwareInstalled is another factor that can influences availability
        #           of services. No software, no response. :)
        # initializedXCP determines the availability of xcp connection.
        #           You need to initialize that to start talking to the ECU in that way.
        self.ecu_state_dict = {
            'powerOn': False,
            'softwareInstalled': True,
            'initializedXCP': False
        }

        # The NVM content of the Body Control Module is imported from a json file.
        self.ecu_nvm_path = ecu_nvm_path
        self.memory_map_path = ecu_memory_map_path
        self.diagMatrix = self.factoryReset(ecu_nvm_path)
        self.memoryMap = self.factoryReset(ecu_memory_map_path)

        # Diagnostic related data:
        # permitAttempt is used for the determination of letting
        #           the user authenticating or not.
        # seedSpace is used for the display of seed value which is a deliberate
        #           vulnerability about exposing information on the mechanism
        #           about the seed&key space to the attacker.
        # seedSpace_bit is a numeric representation of the seed space.
        self.permitAttempt = False
        self.seedSpace = '{0:08b}'
        self.seedSpace_bit = 8
        # Here, a security Constant value is created that shall be used during
        # diagnostic authentication as a key.
        # NOTE: this key shall be moved to the ECU memory upon startup.
        self.securityConstant = random.randint(0, (2**self.seedSpace_bit-1))
        # # The following line is for testing purpose only. Comment this out for normal operation.
        # print('securityConstant: '+str(self.securityConstant))

        # Brute Force Protection related values
        self.bruteForceProtectionEnable = False
        self.bruteForceProtectionStatus = False
        self.memoryMap['consecFailedAttempts'] = [0, 0, 0, 0x327]

        # Setting up privilegeLevel for Default.
        self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] = cons.DEFAULT()
        # Moving diagnostic key into memory.
        self.memoryMap['diagnosticKey'][cons.VAR_VALUE()] = self.securityConstant

        # Printing out a welcome message
        print("Syndicate Automotive Diagnostic Tool v.43.2.11")
        print("The Future is One.")
        # Printing out tester help info
        # self.testerHelp()
        # Printing out ecu state
        self.getECUState()

    # --------------- Diag Tool Functionalities ------------------------
    def dict_to_string(self, inputDict):
        # This function creates a text from the content of a dictionary for
        # textual representation of non textual values like numerics and booleans.
        outputString = ""
        for key in inputDict:
            outputString += " " + key + " : " + str(inputDict[key]) + "\n"
        return outputString

    # external
    def getECUState(self):
        # This function provides information about the state of the ECU.
        print("ECU State:")
        print(self.dict_to_string(self.ecu_state_dict))

    # external
    def readMemoryMap(self):
        # This function provides the content of the Memory Map according to the a2l information.
        print('variable - address')
        for key in self.memoryMap:
            print(key + ' - ' + str(int(self.memoryMap[key][cons.VAR_ADDRESS()])))

    def checkManeuverStatus(self):
        # It is used to check whether the vehicle is currently inside a maneuver situation or not.
        # NOTE: currently it is not really used, but can be leveraged as simulation of
        # near accident situations.
        if self.ecu_state_dict['powerOn']:
            if random.randint(0, 10) > 6:
                self.startManeuver(random.choice([-1, 1]))
                print('Maneuver status is: ON')
            else:
                print('Maneuver status is: OFF')
        else:
            print('Timeout. No signal on vehicle bus.')

    # external
    def testerHelp(self):
        # Prints out the available commands as a help function.
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
              "exit - exit program\n"
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
        # This function enters into the user interface of the Tester and ECU simulation.
        # It listens to the commands provided by the user in the Tester Tool syntax
        # and executes the necessary functions respecting those commands.
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

    # ------------------ ECU_FUNCTIONALITIES -------------------------
    # Here are the ECU functionalities defined.
    # -------------- Diagnostic Functionalities ----------------------
    def factoryReset(self, filePath):
        # This function sets the NVM to a state in which the ECU is reached by an attacker.
        # The memory content of the ECU is imported from a json file.
        return json_parser.parse(filePath)

    # external
    def enumDiagValuesToRead(self):
        # This function returns the Diagnostic Parameter set available
        # to read at the current privilege level.
        print("Available Diagnostic Parameters To Read \nin Current Privilege Level:\n")
        if self.ecu_state_dict['powerOn']:
            for key in self.diagMatrix:
                if self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] >= \
                        self.diagMatrix[key][cons.ACCESS_RD()]:
                    print(key)
        else:
            print('Timeout. No response from ECU.')

    # external
    def enumDiagValuesToWrite(self):
        # This function returns the Diagnostic Parameter set available
        # to write at the current privilege level.
        print("Available Diagnostic Jobs To Write \nin Current Privilege Level:\n")
        if self.ecu_state_dict['powerOn']:
            for key in self.diagMatrix:
                if self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] >= \
                        self.diagMatrix[key][cons.ACCESS_WR()]:
                    print(key)
        else:
            print('Timeout. No response from ECU.')

    # external
    def ecuReset(self):
        # This function is for resetting the ECU.
        # Step 0) It is checked whether there is valid software installed.
        #           If not, then the ECU will not respond.
        # Step 1) It is checked whether the current privilege level is elevated.
        #           If not, this job is not available to prevent DoS.
        # Step 2) IgnitionOff - IgnitionOn, resetting memory map.
        # Step 2.1) Checking whether the vehicle travels fast AND a maneuver is on.
        #           If so, then it informs the user that the ECU reset caused
        #           near accident situation.
        # Step 3) A random delay is added to simulate startup time of an ECU.
        # Step 4) Printing out ECU state after startup.

        # Step 0)
        if self.ecu_state_dict['softwareInstalled']:
            # Step 1)
            if self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] == cons.ELEVATED():
                # Step 2)
                print('Resetting ECU...')
                self.ignitionOff()
                print(self.ecu_state_dict)
                # Step 2.1)
                if self.environment_dict['vehicleSpeed'] > 50 and self.environment_dict['maneuverOn']:
                    print('!!!!!!!!!!!!!!NEAR ACCIDENT SITUATION!!!!!!!!!!!!!!!!!')
                self.ignitionOn()
                self.factoryReset(self.memory_map_path)
                # Step 3
                time.sleep(random.uniform(0.2, 2))
                # Step 4)
                print(self.ecu_state_dict)
            else:
                result = cons.NEG_R_PERMISSION_DENIED()
                print(self.decodeResponse(result))
        else:
            time.sleep(2)
            print("Timeout. No response from ECU.")

    # external
    def getSeed(self):
        # This function makes the ECU to generate a seed value inside the
        # seed space specified in the __init__ method.
        # Step 0) It is checked whether the ECU is powered on and software is installed on ECU.
        #       If not, it notifies the user that the cabling should be checked.
        # Step 1) The authentication is permitted by the ECU.
        # Step 2) The seed value is generated using a random number generator method
        #       according to the seed space.
        # Step 3) The seed value is returned to the caller.

        # Step 0:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled']:
            # Step 1: generating new seed automatically makes authentication available.
            self.permitAttempt = True
            # Step 2:
            self.seedValue = random.randint(0, (2**self.seedSpace_bit-1))
            print('Authentication\nThe generated seed value is: ' + str(self.seedValue) + '\n'
                  + self.seedSpace.format(self.seedValue))
            # Step 3:
            return self.seedValue
        # Step 0 negative branch.
        else:
            print('Could not connect to ECU. Check cabling.')
            return '{0:04x}'.format(0xdead)

    def decodeResponse(self, response):
        # In our example implementation, diagnostic responses
        # shall be 2 digit numbers.
        # This function beautifies the response for
        # human user.
        if int(response / 10) == 1:
            outcome = 'Positive response: '
        elif int(response / 10) == 2:
            outcome = 'Negative response: '
        if response == cons.POS_R_PERM_GRANTED():
            cause = 'Permission granted.'
        elif response == cons.NEG_R_PERMISSION_DENIED():
            cause = 'Permission denied.'
        elif response == cons.NEG_R_MALFORMED_INPUT():
            cause = 'Malformed input.'
        elif response == cons.NEG_R_INCORRECT_KEYWORD():
            cause = 'Incorrect keyword.'
        elif response == cons.NEG_R_BRUTE_FORCE_PROTECTION():
            cause = 'Brute force protection is active.'
        return str(outcome) + str(cause)

    def bruteForceProtection(self):
        # This function provides a brute force mechanism for the ECU.
        # In case it is active, that means that the authentication is
        # prohibited for 10 seconds.
        # When the timer expires, it resets the number of consecutive failed attempts.
        self.bruteForceProtectionStatus = True
        time.sleep(10)
        self.bruteForceProtectionStatus = False
        self.memoryMap['consecFailedAttempts'][cons.VAR_VALUE()] = 0

    # external
    def authenticate(self, response):
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
        #               - if the brute force protection is active (that is inside the try block
        #               since it is handled with a separate error message to demonstrate this
        #               functionality to the players - it is an educational game after all. :)
        # Step 2) The expected response is calculated.
        # Step 3) If the expected response and the one sent by the user is equal,
        #         the permission is granted.
        # Step 4) If the expected response and the one sent by the user is not equal,
        #       it is handled with proper negative response.

        # Step 0:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled']:
            # Step 1:
            if self.permitAttempt:
                # The handling of the response is embedded in a try-chatch block to
                # prevent runtime errors because of malformed input.
                try:
                    if not self.bruteForceProtectionStatus:
                        # Step 2:
                        expected_response = self.seedValue ^ self.memoryMap['diagnosticKey'][cons.VAR_VALUE()]
                        if int(response) == expected_response:
                            # Step 3:
                            self.memoryMap['consecFailedAttempts'][cons.VAR_VALUE()] = 0
                            self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] = cons.ELEVATED()
                            result = cons.POS_R_PERM_GRANTED()
                            print('Elevated Privilege Granted')
                        else:
                            # Step 4
                            result = cons.NEG_R_PERMISSION_DENIED()
                            self.permitAttempt = False
                            if self.bruteForceProtectionEnable:
                                self.memoryMap['consecFailedAttempts'][cons.VAR_VALUE()] += 1
                                if self.memoryMap['consecFailedAttempts'][cons.VAR_VALUE()] >= 2:
                                    x = _thread.start_new_thread(self.bruteForceProtection, ())
                        print(self.decodeResponse(result))
                        return result
                    else:
                        result = cons.NEG_R_BRUTE_FORCE_PROTECTION()
                        print(self.decodeResponse(result))
                        return result
                except:
                    result = cons.NEG_R_MALFORMED_INPUT()
                    print(self.decodeResponse(result))
                    return result
            # Step 1 negative branch.
            else:
                result = cons.NEG_R_PERMISSION_DENIED()
                print(self.decodeResponse(result))
                return result
        # Step 0 negative branch.
        else:
            print('Could not connect to ECU. Check cabling.')
            return '{0:04x}'.format(0xdead)

    # external
    def diagRead(self, variableName):
        # A method for reading out variables from the ECU NVM.
        # Step 0) It is checked whether the ECU is powered on and a software is installed onto ECU.
        # Step 1) It is checked whether the variable is present
        #       in the ECU NVM.
        # Step 2) It is checked that the given variable is permitted
        #       to be extracted by someone with the current privilege level.
        #       If not, the proper negative response is sent.

        # Step 0:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled']:
            print('Reading out ' + variableName)
            # Step 1:
            if variableName in self.diagMatrix:
                # Step 2:
                if self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] >= \
                        self.diagMatrix[variableName][cons.ACCESS_RD()]:
                    response = cons.POS_R_PERM_GRANTED()
                    print(str(response) + '\n' + self.decodeResponse(response))
                    print(str(variableName) + ' : ' + str(self.diagMatrix[variableName][cons.VAR_VALUE()]))
                    return response
                # Step 2 negative branch.
                else:
                    response = cons.NEG_R_PERMISSION_DENIED()
                    print(str(response) + '\n' + self.decodeResponse(response))
                    return response
            # Step 1 negative branch.
            else:
                response = cons.NEG_R_INCORRECT_KEYWORD()
                print(str(response) + '\n' + self.decodeResponse(response))
                return response
        # Step 0 negative branch.
        else:
            print("Could not connect to ECU. Check cabling.")
            return 0

    # external
    def diagWrite(self, variableName, value):
        # This function provides means for modifying the ECU NVM data
        # according to the permissions defined in the Access Control Matrix.
        # Step 0) It is checked whether the ECU is powered on and a software is installed onto that.
        # Step 1) It is checked whether the variable is present
        #       in the ECU NVM.
        # Step 2) It is checked that the given variable is permitted
        #       to be modified by someone with the current privilege level.
        # Step 3) It is checked that the given variable value is compatible
        #       with the type of the new value.
        #       If not, the proper negative response is sent.

        # Step 0:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled']:
            # Step 1:
            if variableName in self.diagMatrix:
                # Step 2:
                if self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] >= \
                        self.diagMatrix[variableName][cons.ACCESS_WR()]:
                    # Step 3 :
                    if isinstance(value, (type(self.diagMatrix[variableName][cons.VAR_VALUE()]))):
                        self.diagMatrix[variableName][cons.VAR_VALUE()] = value
                        response = 10
                        print(str(response) + '\n' + self.decodeResponse(response))
                        print(str(variableName) + ' : ' + str(value))
                        return response
                    # Step 3 negative branch
                    else:
                        response = cons.NEG_R_MALFORMED_INPUT()
                        print(str(response) + '\n' + self.decodeResponse(response))
                        return response
                # Step 2 negative branch
                else:
                    response = cons.NEG_R_PERMISSION_DENIED()
                    print(str(response) + '\n' + self.decodeResponse(response))
                    return response
            # Step 1 negative branch
            else:
                response = cons.NEG_R_INCORRECT_KEYWORD()
                print(str(response) + '\n' + self.decodeResponse(response))
                return response
        # Step 0 negative branch
        else:
            print("Could not connect to ECU. Check cabling.")

    ################ XCP Functionalities ########################

    # external
    def xcpInit(self):
        # This method initializes the XCP connection.
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled']:
            self.ecu_state_dict['initializedXCP'] = True
            return 1
        else:
            print("Could not connect to ECU. Check cabling.")
            return 0

    # external
    def xcpDispose(self):
        # This method disposes the XCP connection.
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled']:
            self.ecu_state_dict['initializedXCP'] = False
        else:
            print("Could not connect to ECU. Check cabling.")

    def checkXCPReadAvail(self):
        # This method checks the availability of the XCP read functionality and returns its value.
        return self.diagMatrix['enableXCPRead'][cons.VAR_VALUE()]

    def checkXCPWriteAvail(self):
        # This method checks the availability of the XCP read functionality and returns its value.
        return self.diagMatrix['enableXCPWrite'][cons.VAR_VALUE()]

    # external
    def xcpRead(self, variableName):
        # This method provides read possibility into ECU real-time memory content.
        # Step 0) It is checked whether the ECU is powered on and the conditions are correct for this operation.
        # Step 1) It is checked whether the XCP channel is initialized and the XCP read is enabled.
        # Step 2) It is checked whether the variable reference used is valid and is permitted to read.
        # Step 3) If all of Steps0-2 are okay, the requested variable value is returned.

        # Step 0 and 1:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled'] \
                and self.ecu_state_dict['initializedXCP']:
            if self.checkXCPReadAvail():
                # Step 2:
                if variableName in self.memoryMap:
                    if self.memoryMap[variableName][cons.ACCESS_RD()] == 1:
                        # Step 3:
                        return self.memoryMap[variableName][cons.VAR_VALUE()]
                    else:
                        return '0xd34d'
                else:
                    return '0xd34d'
            else:
                return '0xd34d'
        # Signaling that the conditions are not okay for an XCP channel
        else:
            print("Not established connection!")
            return '0xd34d'

    #external
    def xcpReadByAddress(self, address):
        # This method provides read possibility by address into ECU real-time memory content.
        # Step 0) It is checked whether the ECU is powered on and the conditions are correct for this operation.
        # Step 1) It is checked whether the XCP channel is initialized and the XCP read is enabled.
        # Step 2) It is checked whether the variable reference used is valid and is permitted to read.
        #       If all of Steps0-2 are okay, the requested variable value is returned.
        #       If Steps0-2 are not okay, the error code is returned.

        # Step 0 and 1:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled'] \
                and self.ecu_state_dict['initializedXCP']:
            if self.checkXCPReadAvail():
                # Step 2:
                response = "0xd34d"
                for key in self.memoryMap:
                    if self.memoryMap[key][cons.VAR_ADDRESS()] == float(address) and \
                            self.memoryMap[key][cons.ACCESS_RD()]:
                        response = self.memoryMap[key][cons.VAR_VALUE()]
                        break
                return response
        # Signaling that the conditions are not okay for an XCP channel
        else:
            print("Not established connection!")
            return "0xd34d"

    # external
    def xcpWrite(self, variableName, inputValue):
        # This method provides read possibility into ECU real-time memory content.
        # Step 0) It is checked whether the ECU is powered on and the conditions are correct for this operation.
        # Step 1) It is checked whether the XCP channel is initialized and the XCP read is enabled.
        # Step 2) It is checked whether the variable reference used is valid and is permitted to read.
        # Step 3) It is checked whether the input value is an appropriate data type.
        # Step 4) If all of Steps0-2 are okay, the requested variable is updated.
        #       If Step 0-2 is not okay, it returns an error code.

        # Step 0 and 1:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled'] \
                and self.ecu_state_dict['initializedXCP']:
            if self.checkXCPWriteAvail():
                # Step 2:
                if variableName in self.memoryMap:
                    if self.memoryMap[variableName][cons.ACCESS_WR()] == 1:
                        # Step 3:
                        if isinstance(self.memoryMap[variableName][cons.VAR_VALUE()],
                                      type(inputValue)):
                            # Step 4:
                            self.memoryMap[variableName][cons.VAR_VALUE()] = inputValue
                            print(variableName + ' : ' + str(inputValue))
                            return inputValue
                        else:
                            return '0xd34d'
                    else:
                        return '0xd34d'
                else:
                    return '0xd34d'
            else:
                return '0xd34d'
        # Signaling that the conditions are not okay for an XCP channel
        else:
            print("Not established connection!")
            return '0xd34d'

    # external
    def xcpWriteByAddress(self, address, value):
        # This method provides write possibility by address into ECU real-time memory content.
        # Step 0) It is checked whether the ECU is powered on and the conditions are correct for this operation.
        # Step 1) It is checked whether the XCP channel is initialized and the XCP read is enabled.
        # Step 2) It is checked whether the variable reference used is valid and is permitted to read.
        #       If all of Steps0-2 are okay, the requested variable value is returned.
        #       If Steps0-2 are not okay, the error code is returned.

        # Step 0 and 1:
        if self.ecu_state_dict['powerOn'] and self.ecu_state_dict['softwareInstalled'] \
                and self.ecu_state_dict['initializedXCP']:
            if self.checkXCPReadAvail():
                # Step 2:
                response = "0xd34d"
                for key in self.memoryMap:
                    if self.memoryMap[key][cons.VAR_ADDRESS()] == float(address) and \
                            self.memoryMap[key][cons.ACCESS_WR()]:
                        self.memoryMap[key][cons.VAR_VALUE()] = float(value)
                        response = (str(key) + " : " + str(value))
                        break
                return response
        # Signaling that the conditions are not okay for an XCP channel
        else:
            print("Not established connection!")
            return "0xd34d"

    ################ENV_FUNCTIONALITIES##########################

    # external
    def ignitionOn(self):
        # Ignites the engine and provides power to the ECUs.
        self.ecu_state_dict['powerOn'] = True
        self.memoryMap['ecuState'][cons.VAR_VALUE()] = 1
        self.memoryMap['privilegeLevel'][cons.VAR_VALUE()] = cons.DEFAULT()
        self.diagMatrix['ignitionCycles'][cons.VAR_VALUE()] += 1

    # external
    def ignitionOff(self):
        # Turns off the engine and removes power from the ECUs.
        self.ecu_state_dict['powerOn'] = False
        self.ecu_state_dict['initializedXCP'] = False

    # external
    def getVehicleSpeed(self):
        # Returns the vehicle speed.
        return self.environment_dict['vehicleSpeed']

    # external
    def setVehicleSpeed(self, vehicleSpeed):
        # Adjusts the vehicle speed.
        self.environment_dict['vehicleSpeed'] = vehicleSpeed

    def maneuvering(self, direction, dummy):
        self.environment_dict['maneuverOn'] = True
        self.memoryMap['yawRateSensorData'] = random.random() * direction * 10
        time.sleep(4)
        self.environment_dict['maneuverOn'] = False
        self.memoryMap['yawRateSensorData'] = random.random() / 1000

    def startManeuver(self, direction):
        # This function triggers a thread that implements a maneuver.
        x = _thread.start_new_thread(self.maneuvering, (direction, 1))

    def stopManeuver(self):
        # This function forces the stop of a maneuver.
        # NOTE: not sure if it will be used, but if so, then might be handy.
        self.environment_dict['maneuverOn'] = False
        # setting back sensor signal to straight driving value with some noise
        self.memoryMap['yawRateSensorData'] = random.random() / 1000
