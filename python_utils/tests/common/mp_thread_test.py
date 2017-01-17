import unittest
from python_utils.common import mp_thread
from python_utils.tests.utils.test_utils import run_unit_test


def func_global(thread, bar=None):
    return bar + 'out'


def func_global_set(thread, bar=None):
    thread.put_data('foo')
    return bar + 'out'


def func_global_no_thread(bar=None):
    return bar + 'out'


class MPThreadTestFuncs(object):
    def func_class(self, thread, bar=None):
        return bar + 'out'

    def func_class_set(self, thread, bar=None):
        thread.put_data('foo')
        return bar + 'out'

    def func_class_no_thread(self, bar=None):
        return bar + 'out'

    @staticmethod
    def func_class_static(thread, bar=None):
        return bar + 'out'

    @staticmethod
    def func_class_static_set(thread, bar=None):
        thread.put_data('foo')
        return bar + 'out'

    @staticmethod
    def func_class_static_no_thread(bar=None):
        return bar + 'out'


class MPThreadTest(unittest.TestCase):
    def test_thread_create(self):
        thr = mp_thread.MPThread(func_global, bar='foo')
        thr.start()
        final_result = thr.join()
        self.assertEqual('fooout', final_result)

        cl = MPThreadTestFuncs()
        thr2 = mp_thread.MPThread(cl.func_class, bar='foo')
        thr2.start()
        final_result = thr2.join()
        self.assertEqual('fooout', final_result)

        thr3 = mp_thread.MPThread(cl.func_class_static, bar='foo')
        thr3.start()
        final_result = thr3.join()
        self.assertEqual('fooout', final_result)

    def test_thread_no_thread_object(self):
        thr = mp_thread.MPThread(func_global_no_thread, bar='foo')
        thr.start()
        final_result = thr.join()
        self.assertEqual('fooout', final_result)

        cl = MPThreadTestFuncs()
        thr2 = mp_thread.MPThread(cl.func_class_no_thread, bar='foo')
        thr2.start()
        final_result = thr2.join()
        self.assertEqual('fooout', final_result)

        thr2 = mp_thread.MPThread(cl.func_class_static_no_thread, bar='foo')
        thr2.start()
        final_result = thr2.join()
        self.assertEqual('fooout', final_result)

    def test_thread_get_put_data(self):
        thr = mp_thread.MPThread(func_global_set, bar='foo')
        thr.start()
        midthread_result = thr.get_data()
        self.assertEqual('foo', midthread_result)
        final_result = thr.join()
        self.assertEqual('fooout', final_result)

        cl = MPThreadTestFuncs()
        thr2 = mp_thread.MPThread(cl.func_class_set, bar='foo')
        thr2.start()
        midthread_result = thr2.get_data()
        self.assertEqual('foo', midthread_result)
        final_result = thr2.join()
        self.assertEqual('fooout', final_result)

        thr3 = mp_thread.MPThread(cl.func_class_static_set, bar='foo')
        thr3.start()
        midthread_result = thr3.get_data()
        self.assertEqual('foo', midthread_result)
        final_result = thr3.join()
        self.assertEqual('fooout', final_result)

        self._thread = mp_thread.MPThread(self.selfThread, bar='foo')
        self._thread.start()
        midthread_result = self._thread.get_data()
        self.assertEqual('foo', midthread_result)
        final_result = self._thread.join()
        self.assertEqual('fooout', final_result)

    def selfThread(self, bar=None):
        self._thread.put_data('foo')
        return bar + 'out'

run_unit_test(MPThreadTest)
