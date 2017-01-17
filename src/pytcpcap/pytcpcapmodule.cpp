#include <Python.h>
#include <pcap.h>
#include <string>
#include <vector>
#include <map>

typedef std::vector<std::pair<int, std::string> > PacketVectorType;
typedef std::map<std::string, PacketVectorType> PacketsByCapHandleMap;
PacketsByCapHandleMap packets;

void
setError(std::string baseStr) {
  PyErr_SetString(PyExc_RuntimeError, baseStr.c_str());
}

static PyObject *
pytcpcap_init(PyObject *self, PyObject *args) {
  const char* device;
  const char* filterStr = "";
  char errorBuf[PCAP_ERRBUF_SIZE];
  pcap_t* pcapObj;
  struct bpf_program filterPtr;

  if (!PyArg_ParseTuple(args, "s|s", &device, &filterStr)) {
    return NULL;
  }

  pcapObj = pcap_create(device, errorBuf);

  if (pcapObj == 0) {
    setError(std::string("Could not open pcap device: ") + errorBuf);
    return NULL;
  }

  if (strncmp(filterStr, "", 1)) {
    if (!pcap_compile(pcapObj, &filterPtr, filterStr,
                      0, PCAP_NETMASK_UNKNOWN)) {
      setError(std::string("Could not parse PCAP filter") + filterStr);
      pcap_close(pcapObj);
      return NULL;
    }
    if (!pcap_setfilter(pcapObj, &filterPtr)) {
      setError(std::string("Could not install PCAP filter") + filterStr);
      pcap_close(pcapObj);
      return NULL;
    }
  }

  // Capure the whole packet where we can
  if (int ret = pcap_set_snaplen(pcapObj, (int)0xFFFF) != 0) {
    setError(std::string("Could not set snaplen on PCAP: ") +
             std::to_string(ret));
    pcap_close(pcapObj);
    return NULL;
  }

  FILE* f = fopen("/tmp/pytcpcap.log", "a");
  fprintf(f, "Init capture on device: %s with filter [%s]\n",
          device, filterStr);
  fclose(f);

  return Py_BuildValue("k", pcapObj);
}

void
packetHandler(unsigned char* user,
              const struct pcap_pkthdr* header,
              const unsigned char* bytes) {
  std::string handleStr((char*)user);

  FILE* f = fopen("/tmp/pytcpcap.log", "a");
  fprintf(f, "Got packet on handle: %s\n", handleStr.c_str());
  fclose(f);

  std::string data((const char*)bytes, header->caplen);
  packets[handleStr].push_back(std::make_pair(header->caplen, data));
}

PyObject* makeList(PacketVectorType& packetsForCapHandle) {
  PyObject *l = PyList_New(packetsForCapHandle.size());
  FILE* f = fopen("/tmp/pytcpcap.log", "a");

  for (PacketVectorType::const_iterator it = packetsForCapHandle.begin();
       it != packetsForCapHandle.end();
       ++it) {
    PyList_Append(l, Py_BuildValue("s#", it->second.c_str(), it->first));
    fprintf(f, "Appending packet to list (len: %u)\n", it->first);
  }

  fclose(f);

  packetsForCapHandle.clear();
  return l;
}

static PyObject *
pytcpcap_start(PyObject* self, PyObject *args) {
  unsigned long pcapHandle;
  if (!PyArg_ParseTuple(args, "k", &pcapHandle)) {
    return NULL;
  }

  std::string handleStr = std::to_string((long)pcapHandle);

  FILE* f = fopen("/tmp/pytcpcap.log", "a");
  fprintf(f, "Activating for handle: %s\n", handleStr.c_str());

  if (int ret = pcap_activate((pcap_t*)pcapHandle) != 0) {
    std::string errorStr;
    switch (ret) {
      case PCAP_WARNING_PROMISC_NOTSUP:
        errorStr = "Promiscuous mode not supported";
        break;
      case PCAP_ERROR_NO_SUCH_DEVICE:
        errorStr = "No such device";
        break;
      case PCAP_ERROR_ACTIVATED:
        errorStr = "Interface has already been activated";
        break;
      case PCAP_ERROR_PERM_DENIED:
        errorStr = "No persmission to access interface";
        break;
      case PCAP_ERROR_PROMISC_PERM_DENIED:
        errorStr = "Cannot set promiscuous permission";
        break;
      case PCAP_ERROR_IFACE_NOT_UP:
        errorStr = "Interface not up";
        break;
      case PCAP_ERROR:
      case PCAP_WARNING:
        errorStr = pcap_geterr((pcap_t*)pcapHandle);
        break;
    }

    setError(std::string("Could not start capture for handle: ") +
             handleStr + " with error: " + errorStr);
    fclose(f);
    return NULL;
  }

  fprintf(f, "Activated capture for handle: %s\n", handleStr.c_str());
  fclose(f);
  Py_RETURN_NONE;
}

static PyObject *
pytcpcap_loop(PyObject* self, PyObject *args) {
  unsigned long pcapHandle;
  if (!PyArg_ParseTuple(args, "k", &pcapHandle)) {
    return NULL;
  }

  std::string handleStr = std::to_string((long)pcapHandle);

  FILE* f = fopen("/tmp/pytcpcap.log", "a");
  fprintf(f, "Starting loop for handle: %s\n", handleStr.c_str());
  fclose(f);

  int ret =
    pcap_loop((pcap_t*)pcapHandle, -1, &packetHandler,
              (unsigned char*)handleStr.c_str());

  if (ret == -1) {
    setError(std::string("Could not start packets handling loop for handle: ") +
             handleStr);
    return NULL;
  }

  Py_RETURN_NONE;
}

static PyObject *
pytcpcap_get_packets(PyObject* self, PyObject *args) {
  unsigned long pcapHandle;
  if (!PyArg_ParseTuple(args, "k", &pcapHandle)) {
    return NULL;
  }

  std::string handleStr = std::to_string((long)pcapHandle);

  FILE* f = fopen("/tmp/pytcpcap.log", "a");
  fprintf(f, "Pulling %lu packets from handle: %lu\n",
          packets[handleStr].size(), pcapHandle);
  fclose(f);

  return makeList(packets[handleStr]);
}

static PyObject *
pytcpcap_stop(PyObject* self, PyObject *args) {
  unsigned long pcapHandle;
  if (!PyArg_ParseTuple(args, "k", &pcapHandle)) {
    return NULL;
  }

  std::string handleStr = std::to_string((long)pcapHandle);

  pcap_breakloop((pcap_t*)pcapHandle);
  pcap_close((pcap_t*)pcapHandle);

  FILE* f = fopen("/tmp/pytcpcap.log", "a");
  fprintf(f, "Read %lu packets on handle: %s\n",
          packets[handleStr].size(), handleStr.c_str());
  fprintf(f, "Stopped capture\n");
  fclose(f);

  Py_RETURN_NONE;
}

static PyMethodDef PytcpcapMethods[] = {
  {"init",  pytcpcap_init, METH_VARARGS, "Init a capture session"},
  {"start",  pytcpcap_start, METH_VARARGS, "Activate packet capture"},
  {"loop",  pytcpcap_loop, METH_VARARGS, "Start processing packets"},
  {"get_packets",  pytcpcap_get_packets, METH_VARARGS, "Get packets"},
  {"stop",  pytcpcap_stop, METH_VARARGS, "Stop capturing packets"},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initpytcpcap(void) {
  (void) Py_InitModule("pytcpcap", PytcpcapMethods);
}
