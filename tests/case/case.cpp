#include <iostream>
#include <string>

int main() {
    int day;
    int score;
    
    day = 3;
    switch (day) {
        case 1:
            std::cout << "Monday" << std::endl;
            break;
        case 2:
            std::cout << "Tuesday" << std::endl;
            break;
        case 3:
            std::cout << "Wednesday" << std::endl;
            break;
        case 4:
            std::cout << "Thursday" << std::endl;
            break;
        case 5:
            std::cout << "Friday" << std::endl;
            break;
        case 6:
            std::cout << "Saturday" << std::endl;
            break;
        case 7:
            std::cout << "Sunday" << std::endl;
            break;
        default:
            std::cout << "Invalid day" << std::endl;
            break;
    }
    score = 85;
    switch (score) {
        case 90:
        case 91:
        case 92:
        case 93:
        case 94:
        case 95:
        case 96:
        case 97:
        case 98:
        case 99:
            std::cout << 'A' << std::endl;
            break;
        case 80:
        case 81:
        case 82:
        case 83:
        case 84:
        case 85:
        case 86:
        case 87:
        case 88:
        case 89:
            std::cout << 'B' << std::endl;
            break;
        case 70:
        case 71:
        case 72:
        case 73:
        case 74:
        case 75:
        case 76:
        case 77:
        case 78:
        case 79:
            std::cout << 'C' << std::endl;
            break;
        default:
            std::cout << 'F' << std::endl;
            break;
    }
    day = 6;
    switch (day) {
        case 1:
            std::cout << "Weekday" << std::endl;
            break;
        case 2:
            std::cout << "Weekday" << std::endl;
            break;
        case 3:
            std::cout << "Weekday" << std::endl;
            break;
        case 4:
            std::cout << "Weekday" << std::endl;
            break;
        case 5:
            std::cout << "Weekday" << std::endl;
            break;
    }
    day = 1;
    while ((day <= 3)) {
        switch (day) {
            case 1:
                std::cout << "first" << std::endl;
                break;
            case 2:
                std::cout << "second" << std::endl;
                break;
            case 3:
                std::cout << "third" << std::endl;
                break;
        }
        day = (day + 1);
    }
    return 0;
}