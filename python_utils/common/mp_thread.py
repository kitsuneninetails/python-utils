import inspect
import multiprocessing
from python_utils.common import exceptions


class MPThread(multiprocessing.Process):
    THREAD_NOT_STARTED = 0
    THREAD_RUNNING = 1
    THREAD_FINISHED = 2
    THREAD_TERMINATED = 3
    THREAD_ERROR = 4

    DEFAULT_TIMEOUT = 10.0

    def __init__(self, run_func, **kwargs):
        super(MPThread, self).__init__(
            target=run_func, kwargs=kwargs)

        self.ready_signal = multiprocessing.Event()
        self.stop_signal = multiprocessing.Event()
        self.started_flag = multiprocessing.Event()
        self.complete_flag = multiprocessing.Event()
        self.terminated_flag = multiprocessing.Event()

        self.return_data = multiprocessing.Queue(1)
        self.error_data = multiprocessing.Queue(1)
        self.data_queues = {'default': multiprocessing.Queue()}
        """ :type: function """

    def run(self):
        self.ready_signal.set()
        if not self.terminated_flag.is_set():
            try:
                # If the runnable function has a 'thread' parameter defined,
                # pass in the thread object to it.  Otherwise, do not pass in
                # the thread object (and hence the data queues and flags will
                # not be accessible)
                if ('thread' in inspect.getargspec(self._target)[0] and
                        'thread' not in self._kwargs):
                    self._kwargs['thread'] = self
                self.return_data.put(
                    self._target(**self._kwargs))
            except BaseException as e:
                self.error_data.put(e)
            self.complete_flag.set()

    def start(self, timeout=DEFAULT_TIMEOUT):
        super(MPThread, self).start()
        self.ready_signal.wait(timeout=timeout)
        self.started_flag.set()

    def join(self, timeout=DEFAULT_TIMEOUT):
        super(MPThread, self).join()
        self.complete_flag.wait(timeout=float(timeout))
        if not self.error_data.empty():
            raise exceptions.SubprocessFailedException(
                info="Subprocess failed with exception",
                passed_exception=self.error_data.get())
        if not self.return_data.empty():
            return self.return_data.get()

    def terminate(self):
        if not self.terminated_flag.is_set():
            super(MPThread, self).terminate()
        self.terminated_flag.set()

    def data_present(self, key='default'):
        if key not in self.data_queues:
            return False
        return not self.data_queues[key].empty()

    def get_data(self, key='default', timeout=DEFAULT_TIMEOUT):
        if key not in self.data_queues:
            return None
        return self.data_queues[key].get(timeout=float(timeout))

    def put_data(self, item, key='default'):
        if key not in self.data_queues:
            self.data_queues[key] = multiprocessing.Queue()
        self.data_queues[key].put(item)

    def status(self):
        if not self.started_flag.is_set():
            return MPThread.THREAD_NOT_STARTED
        if self.complete_flag.is_set():
            return MPThread.THREAD_FINISHED
        if self.terminated_flag.is_set():
            return MPThread.THREAD_TERMINATED
        if not self.error_data.empty():
            return MPThread.THREAD_ERROR
        return MPThread.THREAD_RUNNING
