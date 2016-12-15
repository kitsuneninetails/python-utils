import unittest


def run_unit_test(test_case_name):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_case_name)
    try:
        unittest.TextTestRunner(verbosity=2).run(suite)
    except Exception as e:
        print('Exception: ' + e.message + ', ' + str(e.args))
