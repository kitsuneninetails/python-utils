from distutils.core import setup, Extension

module1 = Extension('pytcpcap',
                    sources=['src/pytcpcap/pytcpcapmodule.cpp'],
                    libraries=['pcap'],
                    extra_compile_args=['-std=c++11'])

setup(name='Python Utils',
      version='1.0',
      description='Python utilities',
      ext_modules=[module1])
