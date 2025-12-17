#include <iostream>
#include <string>

int main() {
    int x, y;
    
    x = 5;
    y = 3;
    if ((x > y)) {
        x = (x + 1);
        y = (y * 2);
        x = (x + y);
    }
    else {
        x = (x - 1);
        y = (y + 4);
    }
    
    return 0;
}