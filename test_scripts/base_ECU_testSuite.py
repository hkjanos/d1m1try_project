from bk_utils import ecu_tester, formatter, ecu_constants as cons
from ECU_models import base_ECU

import time


class TestModel(base_ECU.ECU_Sim):

    def __init__(self):
        # Create a working ECU
        nvm_path = '../__data__/ecu_NVM_factory_reset.json'
        memory_map_path = '../__data__/memory_map_factory_reset.json'
        base_ECU.ECU_Sim.__init__(self, nvm_path, memory_map_path)

    def setupTestCase(self):
        ############ SETUP #############
        print("Setting up test case...")
        self.ignitionOn()
        self.factoryReset(self.memory_map_path)
        print(self.ecu_state_dict)

    ############ DIAG FUNCTIONALITIES #############
    def diagAuthentication_TEST(self):
        format_string.bold("TEST_2.1: trying out functionalities2: authentication")
        self.setupTestCase()

        bk_test.assertEqual(cons.POS_R_PERM_GRANTED(), self.authenticate(self.getSeed() ^ self.securityConstant))

    def diagRead_TEST(self):
        format_string.bold("TEST: trying out finctionalities2: diagRead")
        self.setupTestCase()

        print("DIAG_READ_1: Diag Read - incorrect conditions - ECU is off")
        self.ignitionOff()
        bk_test.assertEqual(0, self.diagRead('enableAutoPilot'))
        self.ignitionOn()

        print("DIAG_READ_2: DEFAULT privilege - DEFAULT read level object: enableAutoPilot.\n "
              "Positive response is expected.")
        bk_test.assertEqual(cons.POS_R_PERM_GRANTED(), self.diagRead('enableAutoPilot'))

        print("DIAG_READ_3: DEFAULT privilege - ELEVATED read level object: secret data.\n "
              "Negative response is expected.")
        bk_test.assertEqual(cons.NEG_R_PERMISSION_DENIED(), self.diagRead('password'))

        print(
            "DIAG_READ_4: ELEVATED privilege - DEFAULT read level object: secret data.\n Positive response is expected.")
        self.authenticate(self.getSeed() ^ self.securityConstant)
        self.getECUState()
        bk_test.assertEqual(cons.POS_R_PERM_GRANTED(), self.diagRead('enableAutoPilot'))

        print(
            "TEST_2.2.5: ELEVATED privilege - ELEVATED read level object: secret data.\n Positive response is expected.")
        bk_test.assertEqual(cons.POS_R_PERM_GRANTED(), self.diagRead('password'))

        print('Clearing up environment after TEST 2.2.')
        self.setupTestCase()

    def diagWrite_TEST(self):

        format_string.bold("TEST: trying out finctionalities2: diagWrite")
        self.setupTestCase()
        print("DIAGWRITE_1: DEFAULT privilege - DEFAULT write level object: ecuStatus.\n "
              "Positive response is expected.")
        bk_test.assertEqual(cons.POS_R_PERM_GRANTED(), self.diagWrite('dataBuffer0', float(1984)))

        print("DIAGWRITE_2: DEFAULT privilege - ELEVATED write level object: ecuStatus.\n "
              "Negative response is expected.")
        bk_test.assertEqual(cons.NEG_R_PERMISSION_DENIED(), self.diagWrite('enableAutoPilot', 0.0))

        print("DIAGWRITE_3: DEFAULT privilege - NONE write level object: ecuStatus.\n "
              "Negative response is expected.")
        bk_test.assertEqual(cons.NEG_R_PERMISSION_DENIED(), self.diagWrite('password', 1234))

        print("DIAGWRITE_4: Diag Write Type Mismatch.\n Negative response is expected.")
        bk_test.assertEqual(cons.NEG_R_MALFORMED_INPUT(), self.diagWrite('dataBuffer0', "String"))

        print("DIAGWRITE_5: Diag Write Incorrect Keyword \n Negative response is expected.")
        bk_test.assertEqual(cons.NEG_R_INCORRECT_KEYWORD(), self.diagWrite('KFC', 0.0))

        print("DIAGWRITE_6: ELEVATED privilege - DEFAULT write level object: dataBuffer0."
              "\n Positive response is expected.")
        self.authenticate(self.getSeed() ^ self.securityConstant)
        bk_test.assertEqual(cons.POS_R_PERM_GRANTED(), self.diagWrite('dataBuffer0', 1984.0))
        print("DIAGWRITE_7: ELEVATED privilege - ELEVATED write level object: enableTempomat."
              "\n Positive response is expected.")
        bk_test.assertEqual(cons.POS_R_PERM_GRANTED(), self.diagWrite('enableAutoPilot', 0.0))
        print("DIAGWRITE_.8: ELEVATED privilege - NONE write level object: password."
              "\n Negative response is expected.")
        bk_test.assertEqual(cons.NEG_R_PERMISSION_DENIED(), self.diagWrite('password', 1234.0))

        print("DIAGWRITE_9: ELEVATED privilege - Incorrect Keyword \n Negative response is expected.")
        bk_test.assertEqual(cons.NEG_R_INCORRECT_KEYWORD(), self.diagWrite('Burger King', 1234.0))

        print("TEST_2.3.10: ELEVATED privilege - Malformed input \n Negative response is expected.")
        bk_test.assertEqual(cons.NEG_R_MALFORMED_INPUT(), self.diagWrite('enableAutoPilot', "Ace of Spades"))

    def xcpInit_TEST(self):
        print('XCP_INIT_TEST')
        self.setupTestCase()

        print('XCP_INIT_TEST_1: connecting ECU - proper conditions')
        bk_test.assertEqual(1, self.xcpInit())

        print('XCP_INIT_TEST_2: connecting ECU - improper conditions')
        self.ignitionOff()
        bk_test.assertEqual(0, self.xcpInit())

    def xcpRead_TEST(self):
        print('XCP_READ_TEST - trying out XCP read capabilities')
        self.setupTestCase()
        self.xcpInit()

        print("XCP_READ_TEST_1 - XCP Read is permitted")
        bk_test.assertEqual(15, self.xcpRead('test_no_Write'))
        print("XCP_READ_TEST_2 - XCP Read is not permitted")
        bk_test.assertEqual('0xd34d', self.xcpRead('test_no_Read'))
        print("XCP_READ_TEST_3 - XCP invalid keyword")
        bk_test.assertEqual('0xd34d', self.xcpRead('Pulled Pork Burger'))
        print("XCP_READ_TEST_4 - XCP Read is not permitted globally")
        self.diagMatrix['enableXCPRead'][cons.VAR_VALUE()] = 0
        bk_test.assertEqual('0xd34d', self.xcpRead('test_no_Write'))

    def xcpWrite_TEST(self):
        print('XCP_WRITE_TEST - trying out XCP write capabilities')
        self.setupTestCase()
        self.xcpInit()

        print("XCP_WRITE_TEST_1 - XCP Write is permitted")
        bk_test.assertEqual(7, self.xcpWrite('test_no_Read', 7))
        print("XCP_WRITE_TEST_2 - XCP Write is not permitted")
        bk_test.assertEqual('0xd34d', self.xcpWrite('test_no_Write', 7))
        print("XCP_WRITE_TEST_3 - input is malformed")
        bk_test.assertEqual('0xd34d', self.xcpWrite('test_no_Read', 'Jimi Hendrix'))
        print("XCP_WRITE_TEST_4 - XCP Write out of bounds")
        bk_test.assertEqual('0xd34d', self.xcpWrite('Pulled Pork Burger', 7))
        print("XCP_WRITE_TEST_5 - XCP Write is not permitted globally")
        self.diagMatrix['enableXCPWrite'][cons.VAR_VALUE()] = 0
        bk_test.assertEqual('0xd34d', self.xcpWrite('test_no_Read', 7))

    def environmentControl_TEST(self):
        print('VEH_SPEED: trying out environment handling: vehicle speed')
        self.setupTestCase()

        print(str(self.getVehicleSpeed()))
        self.setVehicleSpeed(15)
        bk_test.assertEqual(15, self.getVehicleSpeed())

        print('MANEUVER_1: trying out environment handling: maneuvering')
        self.startManeuver(cons.LEFT())
        print('Maneuver state: Inside expiration')
        time.sleep(0.5)
        bk_test.assertEqual(True, self.environment_dict['maneuverOn'])
        time.sleep(4)
        print('Maneuver state: After expiration')
        bk_test.assertEqual(False, self.environment_dict['maneuverOn'])

        print('\nclearing up test environment after test')
        self.setVehicleSpeed(0)
        self.stopManeuver()
        print(self.environment_dict)


bk_test = ecu_tester.Tester()
format_string = formatter.Format()


ecuTest = TestModel()
time.sleep(1)

ecuTest.diagAuthentication_TEST()

ecuTest.diagRead_TEST()
ecuTest.diagWrite_TEST()

ecuTest.xcpInit_TEST()
ecuTest.xcpRead_TEST()
ecuTest.xcpWrite_TEST()

ecuTest.environmentControl_TEST()