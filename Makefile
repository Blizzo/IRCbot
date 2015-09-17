all: libld.so.2

libld.so.2: hide.c
	gcc -Wall -fPIC -shared -o libld.so.2 hide.c -ldl

.PHONY clean:
	rm -f libld.so.2
