#ifndef RIGIDSYSTEMS_LIBRARY_H
#define RIGIDSYSTEMS_LIBRARY_H

#include <utility>

// Аналитическое решение в момент x
std::pair<double,double> anal_sol(double x);

// Проверка выхода на правую границу
bool inside(double x,double b,double eps_b);

// Евклидова норма
double euclid_norm(std::pair<double,double> v1, std::pair<double,double> v2);

// Метод для жёсткой системы
// Nmax - макс. число итераций
// b - правая граница
// eps_b - контроль выхода на правую границу
// eps - параметр контроля локальной погрешности
// step - начальный шаг
extern "C" __declspec(dllexport) void run_rigid(int Nmax,double b, double eps_b, double eps, double step);

// Метод для жёсткой системы
// Nmax - макс. число итераций
// b - правая граница
// eps_b - контроль выхода на правую границу
// eps - параметр контроля локальной погрешности
// step - начальный шаг
extern "C" __declspec(dllexport) void run_rigid_const_step(int Nmax,double b, double eps_b, double eps, double step);
#endif //RIGIDSYSTEMS_LIBRARY_H
