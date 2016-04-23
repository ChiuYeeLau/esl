all: check_serve.so

check_serve.so: check_serve.c
	gcc -shared -Wl,-soname,check_serve -o check_serve.so -fPIC check_serve.c

