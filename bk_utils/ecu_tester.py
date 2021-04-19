from bk_utils import formatter


class Tester:
    # This class is for the test framework of this project.
    # Currently it is pretty lightweight but maybe can be extended later.
    format_string = formatter.Format()

    def assertEqual(self, expectedValue, measuredValue):
        # Do an assertion between two value, the expectation is that those should be equal.
        # Possible development: Create a generic assert function with a third parameter,
        # which sets the expectations (equal, more than, less than, etc.)
        if measuredValue == expectedValue:
            self.format_string.passed('PASSED. ' + str(expectedValue) + ' = ' + str(measuredValue) + '\n')
        else:
            self.format_string.failed('FAILED. ' + str(expectedValue) + ' = ' + str(measuredValue) + '\n')
