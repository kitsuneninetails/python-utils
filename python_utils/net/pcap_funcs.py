import pytcpcap
from python_utils.common import exceptions
from python_utils.common import mp_thread


class Pcap:
    def __init__(self, device, filter_str=""):
        self.handle = pytcpcap.init(device, filter_str)
        self._server_thread = mp_thread.MPThread(self._listen_server)

    def start_capture(self):
        self._server_thread.start()
        ret = self._server_thread.get_data()
        if ret is not None:
            raise ret

    def _listen_server(self):
        try:
            pytcpcap.start(self.handle)
            self._server_thread.put_data(None)
        except exceptions.SubprocessFailedException as e:
            self._server_thread.put_data(e)
        pytcpcap.loop(self.handle)

    def get_packets(self):
        ret = pytcpcap.get_packets(self.handle)
        print str(ret)

    def close(self):
        pytcpcap.stop(self.handle)
        self._server_thread.join()
