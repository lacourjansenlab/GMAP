#include <math.h>
#include <stdio.h>

/*
This file will contain all functions (and their helpers) required for
calculating the electric potential, field and gradient on any given list
of points.
*/

extern "C" {
    __declspec(dllexport) int testadd(int a, int b);
}


extern "C" {
    int testadd(int a, int b) {
        return (a + b);
    }
}
