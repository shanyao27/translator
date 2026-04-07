#include <iostream>
#include <string>

class tcounter {
public:
    int value;
    tcounter(int v);
    void increment();
    int getvalue();
};

tcounter::tcounter(int v) {
    value = v;
}

void tcounter::increment() {
    value = (value + 1);
}

int tcounter::getvalue() {
    return value;
}

int main() {
    tcounter* c;
    
    c = new tcounter(0);
    c->increment();
    c->increment();
    c->increment();
    std::cout << c->getvalue() << std::endl;
    return 0;
}