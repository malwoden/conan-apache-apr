#include <iostream>
#include <apr_general.h>

int main(int argc, char* argv[]) {
    const char* const* test = argv;
    apr_app_initialize(&argc, &test, 0);
    apr_terminate();
}
