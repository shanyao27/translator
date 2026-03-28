#include <iostream>
#include <string>

int main() {
    const int max = 100;
    const int min = -5;
    const float pi = 3.14;
    const std::string greeting = "Hello, World!";
    const bool flag = true;
    
    int i;
    float r;
    
    i = 0;
    while ((i < max)) {
        i = (i + 1);
    }
    std::cout << i << std::endl;
    r = (pi * 2.0);
    std::cout << r << std::endl;
    std::cout << greeting << std::endl;
    i = (min + 10);
    std::cout << i << std::endl;
    if (flag) {
        std::cout << "flag is true" << std::endl;
    }
    else {
        std::cout << "flag is false" << std::endl;
    }
    return 0;
}