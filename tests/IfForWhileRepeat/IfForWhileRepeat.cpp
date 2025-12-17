#include <iostream>
#include <string>

int main() {
    int x, y, s, i, i1;
    
    x = 5;
    y = 3;
    s = 0;
    i = 0;
    i1 = 0;
    for (i = 1; i <= 5; ++i) {
        s = (s + i);
    }
    if ((x > y)) {
        x = (x + 1);
        y = (y * 2);
        x = (x + y);
    }
    else {
        x = (x - 1);
        y = (y + 4);
    }
    while ((i < 5)) {
        i = (i + 1);
    }
    do {
        i1 = (i1 + 1);
    } while (!((i1 == 5)));
    
    return 0;
}