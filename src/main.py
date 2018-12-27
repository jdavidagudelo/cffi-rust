#!/usr/bin/env python3
# coding: utf-8

import sys
import ctypes
from ctypes import Structure
from ctypes import c_uint32, c_char_p, POINTER, c_int32


class Tuple(Structure):
    _fields_ = [("x", c_uint32),
                ("y", c_uint32)]

    def __str__(self):
        return "({},{})".format(self.x, self.y)


class ZipCodeDatabaseS(Structure):
    pass


def get_structure():
    lib = get_rust_library()
    lib.zip_code_database_new.restype = POINTER(ZipCodeDatabaseS)

    lib.zip_code_database_free.argtypes = (POINTER(ZipCodeDatabaseS),)

    lib.zip_code_database_populate.argtypes = (POINTER(ZipCodeDatabaseS),)

    lib.zip_code_database_population_of.argtypes = (POINTER(ZipCodeDatabaseS), c_char_p)
    lib.zip_code_database_population_of.restype = c_uint32

    class ZipCodeDatabase:
        def __init__(self):
            self.obj = lib.zip_code_database_new()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            lib.zip_code_database_free(self.obj)

        def populate(self):
            lib.zip_code_database_populate(self.obj)

        def population_of(self, zip_code):
            return lib.zip_code_database_population_of(self.obj, zip_code.encode('utf-8'))

    with ZipCodeDatabase() as database:
        database.populate()
        pop1 = database.population_of("90210")
        pop2 = database.population_of("20500")
        print(pop1 - pop2)


def get_rust_library(lib_name='integers'):
    prefix = {'win32': ''}.get(sys.platform, 'lib')
    extension = {'darwin': '.dylib', 'win32': '.dll'}.get(sys.platform, '.so')
    lib = ctypes.cdll.LoadLibrary(prefix + lib_name + extension)
    return lib


def return_string():
    lib = get_rust_library()
    lib.theme_song_generate.argtypes = (ctypes.c_uint8,)
    lib.theme_song_generate.restype = ctypes.c_void_p

    lib.theme_song_free.argtypes = (ctypes.c_void_p,)

    def theme_song_generate(count):
        ptr = lib.theme_song_generate(count)
        try:
            return ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf-8')
        finally:
            lib.theme_song_free(ptr)

    print(theme_song_generate(5))


def sum_of_even():
    lib = get_rust_library()
    lib.sum_of_even.argtypes = (POINTER(c_uint32), ctypes.c_size_t)
    lib.sum_of_even.restype = ctypes.c_uint32

    def sum_of_even_internal(numbers):
        buf_type = c_uint32 * len(numbers)
        buf = buf_type(*numbers)
        return lib.sum_of_even(buf, len(numbers))

    print(sum_of_even_internal([1, 2, 3, 4, 5, 6]))


def count_characters():
    lib = get_rust_library()
    lib.how_many_characters.argtypes = (c_char_p,)
    lib.how_many_characters.restype = c_uint32
    print(lib.how_many_characters("göes to élevên".encode('utf-8')))


def add_values():
    lib = get_rust_library()
    lib.addition.argtypes = (c_uint32, c_uint32)
    lib.addition.restype = c_uint32
    print(lib.addition(1, 2))


def get_tuple():
    lib = get_rust_library()
    lib.flip_things_around.argtypes = (Tuple,)
    lib.flip_things_around.restype = Tuple

    tup = Tuple(10, 20)

    print(lib.flip_things_around(tup))


def get_array():
    lib = get_rust_library()
    lib.test_array.restype = POINTER(c_int32 * 3)
    result = lib.test_array()
    print([i for i in result.contents])


def get_vector():
    lib = get_rust_library()

    class Slice(Structure):
        _fields_ = [("ptr", POINTER(c_int32)), ("len", ctypes.c_uint64)]

    lib.wrapper.restype = Slice
    v = lib.wrapper()
    data = [v.ptr[i] for i in range(v.len)]
    print(data)
    lib.free_vector.argtypes = (Slice,)
    lib.free_vector(v)


add_values()
count_characters()
return_string()
sum_of_even()
get_tuple()
get_structure()
get_array()
get_vector()
