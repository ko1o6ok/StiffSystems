#include "library.h"

#include <cmath>
#include <fstream>
#include <utility>
#include <iostream>


using namespace std;

// Проверка выхода на правую границу
bool inside(double x,double b,double eps_b){
    return x < b - eps_b;
}

// Евклидова норма
double euclid_norm(pair<double,double> v1, pair<double,double> v2){
    double d1 = v1.first-v2.first;
    double d2 = v1.second-v2.second;
    return sqrt(d1*d1 + d2*d2);
}

std::pair<double,double> anal_sol(double x){
    // Собств числа
    double lam1 = -0.01;
    double lam2 = -1000;
    double C1 = 10;
    double C2 = -3;

    return {C1 * exp(lam1 * x) + C2 * exp(lam2 * x),C1 * exp(lam1 * x) - C2 * exp(lam2 * x)};
}


void rigid_step(double& x, pair<double,double>& v, double step){
    // Неявный РК2
    // Заранее аналитически выражены коэффициенты
    double a,b;
    a = -500.005;
    b = 499.995;

    double k1_1 = a * v.first + b * v.second;
    double k1_2 = b * v.first + a * v.second;

    pair<double,double> s = {v.first+step/2 * k1_1,v.second + step/2 * k1_2};
    double tmp = s.first;
    s.first = a * s.first + b * s.second;
    s.second = b * tmp + a * s.second;

    double det = (1-step/2 * a) * (1-step/2 * a) - ((step/2 * b) * (step/2 * b));

    double s1 = (1-step/2 * a) * s.first + (step/2 * b) * s.second;
    double s2 = (step/2 * b) * s.first + (1-step/2 * a) * s.second;

    double k2_1 = s1/det;
    double k2_2 = s2/det;

    v.first = v.first + step/2 * (k1_1+k2_1);
    v.second = v.second + step/2 * (k1_2+k2_2);
    x = x + step;
}


// Метод для жёсткой системы
// Nmax - макс. число итераций
// b - правая граница
// eps_b - контроль выхода на правую границу
// eps - параметр контроля локальной погрешности
// step - начальный шаг
extern "C" __declspec(dllexport) void run_rigid(int Nmax,double b, double eps_b, double eps, double step){
    std::ofstream file_1("rigid_syst_data_w.txt"); // Файл с данными для графика
    std::ofstream file_2("rigid_syst.txt"); // Файл с выходными данными
    std::ofstream file_3("rigid_syst_data_s.txt");

    pair<double,double> v0 = {7,13}; // Начальные условия
    double x = 0.0; // Начальная координата
    double h = step; // Начальный шаг

    auto v = v0; // Текущее состояние

    double x_help; // Координаты вспомогательной точки численной траектории
    pair<double,double> v_help,v_current;
    double x_current; // Текущее положение
    double S = 10000; // Параметр оценки локальной погрешности

    int C1 = 0; // Счётчик деления шага
    int C2 = 0; // Счётчик удвоений шага

    double n=0; // Будет считать число итераций
    double max_OLP = -1; // Макс модуль ОЛП
    double OLP;
    double max_step = -1; // Максимальный шаг
    double x_max_step; // Соотв коорд
    double min_step = h; // Минимальный шаг
    double x_min_step=0; // Соотв коорд

    double diff = 0; // Евклидова норма разности численного и аналитич решения
    double max_anal_diff = -1; // Макс разность численного и анал реш = макс глобальная погрешность

    // Начальный шаг метода
    auto sol_ = anal_sol(x); // Аналитическое решение в этой точке
    diff  = euclid_norm(v,sol_);
    if(diff > max_anal_diff)
        max_anal_diff = diff;
    //file_1 << 0 << " " << x << " " << v.first<< " " <<v.second <<" "<<" - "<< " " <<h << " " <<C1<< " " <<C2<< " "<<sol_.first<<" "<<sol_.second<< " "<< diff <<"\n";

    file_1 << 0 << " " << x << " " << v.first << " " << 0 << " " <<0<< " " <<0<< " " <<h << " " <<C1<< " " <<C2 <<" "<<sol_.first<< " "<< diff <<"\n";
    file_3 << 0 << " " << x << " " << v.second << " " << 0 << " " <<0<< " " <<0<< " " <<h << " " <<C1<< " " <<C2 <<" "<<sol_.second<< " "<< diff <<"\n";


    for (int i = 0; i < Nmax && inside(x,b,eps_b); ++i) {
        if(h > max_step){
            max_step = h;
            x_max_step = x;
        }
        if(h < min_step){
            min_step = h;
            x_min_step = x;
        }
        // Контроль выхода на правую границу
        while(x+h >b){
            h = h/2;
            ++C1;
        }
        // Находимся в точке (x_n,v_n)
        // Текущие координаты численной траектории
        x_current = x;
        v_current = v;

        x_help = x_current;
        v_help = v_current;
        // Перейдём во вспомогательную точку половинным шагом
        rigid_step(x_help,v_help,h/2);
        // Получим новую точку ЧТ тем же половинным шагом
        rigid_step(x_help,v_help,h/2);

        // Теперь считаем эту же точку с шагом h
        rigid_step(x_current,v_current,h);

        // Вычисляем
        S = euclid_norm(v_help,v_current)/ 3.0;
        OLP = 4 * S; // Оценка локальной погрешности



        if(S <= eps){
            if(OLP > max_OLP)
                max_OLP = OLP;
            // Принимаем следующую точку
            x = x_current;
            //v = v_current;
            v = v_help;
            auto sol = anal_sol(x); // Аналитическое решение в этой точке
            diff  = euclid_norm(v,sol);
            if(diff > max_anal_diff)
                max_anal_diff = diff;
            //file_1 << (i + 1) << " " << x << " " << v.first<< " " <<v.second <<" "<<OLP<< " " <<h << " " <<C1<< " " <<C2<< " "<<sol.first<<" "<<sol.second<< " "<< diff <<"\n";

            file_1 << (i + 1) << " " << x << " " << v.first << " " << v_help.first<< " " <<v.first-v_help.first<< " " <<16*S<< " " <<h << " " <<C1<< " " <<C2 << " "<<sol.first<< " "<<diff<<"\n";
            file_3 << (i + 1) << " " << x << " " << v.second << " " << v_help.second<< " " <<v.second-v_help.second<< " " <<16*S<< " " <<h << " " <<C1<< " " <<C2 << " "<<sol.second<< " "<<diff<<"\n";
            if(S < eps/8){//8
                // Продолжаем счёт с удвоенным шагом
                h = 2 * h; // Удвоили шаг
                C2 ++;
            }
        }
        else {
            // Новая точка не принимается
            h = h / 2; // Шаг в 2 раза меньше
            C1++;
        }

        n = i + 1;
    }
    file_1.close();
    file_2 << n << " " << b-x << " " << max_OLP << " " << C2 << " " << C1 << " " << max_step << " " << x_max_step << " " << min_step << " " << x_min_step << " "<<max_anal_diff;
    file_2.close();
}

 //Метод для жёсткой системы
 //Nmax - макс. число итераций
 //b - правая граница
 //eps_b - контроль выхода на правую границу
 //eps - параметр контроля локальной погрешности
 //step - начальный шаг
extern "C" __declspec(dllexport) void run_rigid_const_step(int Nmax,double b, double eps_b, double eps, double step){
    std::ofstream file_1("rigid_syst_data_const_step_w.txt"); // Файл с данными для графика
    std::ofstream file_2("rigid_syst_const_step.txt"); // Файл с выходными данными
    std::ofstream file_3("rigid_syst_data_const_step_s.txt");

    pair<double,double> v0 = {7,13}; // Начальные условия
    double x = 0.0; // Начальная координата
    double h = step; // Начальный шаг

    auto v = v0; // Текущее состояние

    double x_help; // Координаты вспомогательной точки численной траектории
    pair<double,double> v_help,v_current;
    double x_current; // Текущее положение
    double S = 10000; // Параметр оценки локальной погрешности

    int C1 = 0; // Счётчик деления шага
    int C2 = 0; // Счётчик удвоений шага

    double n=0; // Будет считать число итераций
    double max_OLP = -1; // Макс модуль ОЛП
    double OLP;
    double max_step = -1; // Максимальный шаг
    double x_max_step; // Соотв коорд
    double min_step = h; // Минимальный шаг
    double x_min_step=0; // Соотв коорд
    double diff = 0; // Евклидова норма разности численного и аналитич решения
    double max_anal_diff = -1; // Макс разность численного и анал реш = макс глобальная погрешность

    auto sol_ = anal_sol(x); // Аналитическое решение в этой точке
    diff  = euclid_norm(v,sol_);
    if(diff > max_anal_diff)
        max_anal_diff = diff;

    file_1 << 0 << " " << x << " " << v.first << " " <<h << " " <<C1<< " " <<C2 << " "<<sol_.first<< " "<<diff<<"\n";
    file_3 << 0 << " " << x << " " << v.second << " " << h << " " <<C1<< " " <<C2 <<" "<<sol_.second<< " "<<diff<<"\n";

    for (int i = 0; i < Nmax && inside(x,b,eps_b); ++i) {
        if(h > max_step){
            max_step = h;
            x_max_step = x;
        }
        if(h < min_step){
            min_step = h;
            x_min_step = x;
        }
        while(x+h >b){
            h = h/2;
            ++C1;
        }
        // Находимся в точке (x_n,v_n)
        // Текущие координаты численной траектории
        x_current = x;
        v_current = v;

        auto sol = anal_sol(x); // Аналитическое решение в этой точке
        diff  = euclid_norm(v,sol);
        if(diff > max_anal_diff)
            max_anal_diff = diff;

        // Теперь считаем эту точку с шагом h
        rigid_step(x_current,v_current,h);


        // Принимаем следующую точку
        x = x_current;
        v = v_current;

        file_1 << (i + 1) << " " << x << " " << v.first << " " <<h << " " <<C1<< " " <<C2 <<" "<<sol.first<< " "<<diff<<"\n";
        file_3 << (i + 1) << " " << x << " " << v.second << " " << h << " " <<C1<< " " <<C2 <<" "<<sol.second<< " "<<diff<<"\n";
        n = i + 1;
    }
    file_1.close();
    file_2 << n << " " << b-x  << " " << C2 << " " << C1 << " " << max_step << " " << x_max_step << " " << min_step << " " << x_min_step << " "<<max_anal_diff ;
    file_2.close();
}
