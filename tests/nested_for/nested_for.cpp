#include <iostream>
#include <string>

int main() {
    int i, j, s;

    s = 0;
    for (i = 1; i <= 3; ++i) {
        for (j = 1; j <= 2; ++j) {
            s = (s + (i * j));
        }
    }

    return 0;
}