INCLUDES=-I/usr/local/include -I/usr/include/python2.7

pytcpcapmodule.so: pytcpcapmodule.o
	g++ -o pytcpcapmodule.so -shared pytcpcapmodule.o -lpcap

.cpp.o:
	g++ -g -std=c++11 -fPIC $(INCLUDES) -c $<

clean:
	rm -f *.o pytcpcapmodule.so
