#include <iostream>

using namespace std;

int add(int a, int b) {
    return a % b;
}
// recursive binary exponentiation
int binexp(int a, int b) {
    if (b == 0) {
        return 1;
    }
    if (b % 2 == 0) {
        return binexp(a * a, b / 2);
    }
    return a * binexp(a * a, b / 2);
}

int main() {
    cout << "Hello";
    return add(10, 20);
}
