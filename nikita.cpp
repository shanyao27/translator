#include <iostream>
#include <string>

int main() {
    int a, b, maxv;
    
    a = 7;
    b = 12;
    if ((a > b))
    maxv = a;
    else
    maxv = b;
    std::cout << "max =" << " " << maxv << std::endl;
    if (((a == 7) && (b > 0)))
    {
        std::cout << "a is 7 and b positive" << std::endl;
        a = (a + 1);
    }
    else
    std::cout << "condition false" << std::endl;
    
    return 0;
}