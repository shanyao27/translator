#include <iostream>
#include <string>

int add(int a, int b) {
    return (a + b);
}

void print_sum(int a, int b) {
    s = add(a, b);
    std::cout << "Sum = " << " " << s << std::endl;
}

int main() {
    int x, y, s;
    
    x = 10;
    y = add(x, 5);
    std::cout << "Result of function add: " << " " << y << std::endl;
    print_sum(3, 4);
    return 0;
}