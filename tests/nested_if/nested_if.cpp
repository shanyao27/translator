#include <iostream>
#include <string>

int main() {
    int x;

    x = 10;
    if ((x > 0)) {
        if ((x < 20)) {
            x = (x + 5);
        }
        else {
            x = (x - 5);
        }
    }

    return 0;
}