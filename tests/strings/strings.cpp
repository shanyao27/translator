#include <iostream>
#include <string>

std::string concat_strings(std::string a, std::string b) {
    return (a + b);
}

std::string hello(std::string name) {
    return ("Hello, " + name);
}

int main() {
    std::string firstname;
    std::string lastname;
    std::string fullname;
    std::string greeting;

    firstname = "Nikita";
    lastname = " Vdovenkov";
    fullname = concat_strings(firstname, lastname);
    greeting = hello(fullname);
    std::cout << "Full name: " << " " << fullname << std::endl;
    std::cout << greeting << std::endl;
    return 0;
}