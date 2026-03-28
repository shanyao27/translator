#include <iostream>
#include <string>

struct point {
    float x;
    float y;
};
struct person {
    int age;
    float score;
};

int main() {
    point p;
    point q;
    person person;
    float dist;
    
    p.x = 3.0;
    p.y = 4.0;
    std::cout << p.x << " " << p.y << std::endl;
    q.x = (p.x * 2.0);
    q.y = (p.y * 2.0);
    std::cout << q.x << " " << q.y << std::endl;
    dist = ((p.x * p.x) + (p.y * p.y));
    std::cout << dist << std::endl;
    person.age = 25;
    person.score = 9.5;
    std::cout << person.age << " " << person.score << std::endl;
    if ((person.age > 18)) {
        std::cout << "adult" << std::endl;
    }
    else {
        std::cout << "minor" << std::endl;
    }
    p.x = 0.0;
    while ((p.x < 5.0)) {
        p.x = (p.x + 1.0);
    }
    std::cout << p.x << std::endl;
    return 0;
}