from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from UI.infoWindow import UI_infoWindow

import ctypes
import os
import time

from table_columns import columns, extra_info_rows

ui_file = './UI/MainWindow.ui'


def create_plot(parent):
    parent.fig = Figure(figsize=(parent.width() / 100, parent.height() / 100))
    parent.canvas = FigureCanvas(parent.fig)
    parent.plot = parent.fig.add_subplot()
    return parent.plot


class UI_mainWindow(QMainWindow):
    def __init__(self):
        super(UI_mainWindow, self).__init__()
        uic.loadUi(ui_file, self)
        # определение значений по умолчанию

        # создание окон для графиков
        self.plt = create_plot(self.plot_widget_1)
        self.plt_PS = create_plot(self.plot_widget_2)

        # присвоение мест для окон
        self.plot_widget_1.canvas.setParent(self.plot_widget_1)
        self.plot_widget_2.canvas.setParent(self.plot_widget_2)

        self.tabWidget.currentChanged.connect(
            self.toolBar_changing)  # задание функционала. В данной строке: Меняет тулбар при переходе на другую вклвдку
        self.plot_toolBar = NavigationToolbar(self.plot_widget_1.canvas, self)

        self.addToolBar(self.plot_toolBar)  # создание тулбара

        self.plot_button.clicked.connect(
            self.plotting)  # задание функционала. В данной строке: построение графика при нажатии на кнопку "Построить"
        self.delete_plot.clicked.connect(
            self.clear_plots)  # задание функционала. В данной строке: очистка окон от ВСЕХ графиков (чистит все окна(графики и таблицу))

        # Названия осей
        self.plot_widget_1.plot.set_xlabel("x")
        self.plot_widget_1.plot.set_ylabel("Решения")

        self.plot_widget_2.plot.set_xlabel("V1")
        self.plot_widget_2.plot.set_ylabel("V2")

        # настройка включения второго окна
        self.info_button.triggered.connect(lambda: self.info_window("my_info.pdf"))

    def info_window(self,file_name):
        self.i_window = QMainWindow()
        self.i_window.ui = UI_infoWindow(file_name)
        self.i_window.ui.show()

    def clear_plots(self):
        self.plt.cla()
        self.plt_PS.cla()
        self.plot_widget_1.canvas.draw()  # обновление окна
        self.plot_widget_2.canvas.draw()

        self.clear_exrta_info_table()
        self.clear_table(self.info_table)
        self.clear_table(self.info_table_V_dot)

        # Названия осей
        self.plot_widget_1.plot.set_xlabel("x")
        self.plot_widget_1.plot.set_ylabel("Решения")

        self.plot_widget_2.plot.set_xlabel("V1")
        self.plot_widget_2.plot.set_ylabel("V2")

    def toolBar_changing(self, index):  # изменение привязки тулбара
        self.removeToolBar(self.plot_toolBar)
        if index == 0:  # тулбал для вкладки График
            self.plot_toolBar = NavigationToolbar(self.plot_widget_1.canvas, self)
        elif index == 2:  # тулбар для вкладки График ФП
            self.plot_toolBar = NavigationToolbar(self.plot_widget_2.canvas, self)
        self.addToolBar(self.plot_toolBar)

    def file_to_table(self, file_name):  # из str делает list(list(str))
        if len(file_name.split('.')) == 1:
            file_name += '.txt'
        table = []
        with open(file_name, 'r') as f:
            for line in f:
                table.append(line.split(' '))
        return table

    def clear_exrta_info_table(self):
        while self.extra_info_layout.count():
            item = self.extra_info_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def update_extra_info_table(self, task_index, table):
        self.clear_exrta_info_table()

        table = table[0]
        i = 0
        cur_table = extra_info_rows[task_index]
        for elem in table:
            cur_text = f"{cur_table[i]} {elem}"
            self.extra_info_layout.addWidget(QLabel(cur_text, self))
            i += 1

    def plotting(self):
        # lib_dir = os.path.join(os.curdir, "libNM1_lib.dll")
        lib_dir = os.path.join(os.curdir, "libRigidSystems.dll")
        lib = ctypes.windll.LoadLibrary(lib_dir)

        X_start = 0.0
        X_end = float(self.get_X_end())

        # Начальные значения
        # u0 = float(self.get_U0())  # Начальное значение функции
        # du0 = float(self.get_DU0())  # Начальное значение производной функции (для осн. задачи - 2)

        # Начальные значения системы (w,s)
        w_0 = 7.0
        s_0 = 13.0
        h0 = float(self.get_start_step())  # Начальный шаг
        eps = float(self.get_step_control())  # Параметр контроля шага
        eps_b = float(self.get_border_control()) # Параметр контроля выхода на правую границу

        Nmax = int(self.get_num_max_iter())  # Максимальное число итераций
        # a = float(self.get_param_a())  # параметр а для осн. задачи - 2

        # task = self.get_task()
        file_name = ""  # Имя основного файла, в котором хранятся шаги счёта
        file_name_extra_info = ""  # Имя файла с дополнительной информацией (в UI - колонка, расположенная в правом нижнем углу)
        file_name_for_V_dot = ""
        # task[0]- номер задачи. 0-тестовая; 1-основная №1; 2-основная №2
        # if task[0] == 0:
        #
        #     if self.step_mode.isChecked():
        #         my_func = lib.run_test_method  # выбор задачи
        #         file_name = "test_method_1"
        #         file_name_extra_info = 'test_method_2'
        #     else:
        #         my_func = lib.run_test_method_const_step
        #         file_name = "test_method_1_const_step"
        #         file_name_extra_info = 'test_method_2_const_step'
        #
        #     my_func.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double,
        #                         ctypes.c_double,
        #                         ctypes.c_double]  # задание типов для параметров функции
        #     my_func.restype = ctypes.c_void_p  # задание типа возвращаемого значения
        #     my_func(u0, Nmax, X_end, 0.01, eps, h0)
        #
        #
        # elif task[0] == 1:
        #     if self.step_mode.isChecked():
        #         my_func = lib.run_main_method_1
        #         file_name = "main_method_1_1"
        #         file_name_extra_info = 'main_method_1_2'
        #     else:
        #         my_func = lib.run_main_method_1_const_step
        #         file_name = "main_method_1_1_const_step"
        #         file_name_extra_info = 'main_method_1_2_const_step'
        #
        #     my_func.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double,
        #                         ctypes.c_double,
        #                         ctypes.c_double]
        #     my_func.restype = ctypes.c_void_p
        #     my_func(u0, Nmax, X_end, 0.01, eps, h0)



        if self.step_mode.isChecked():
            # my_func = lib.run_main_method_2
            # file_name = "main_method_2_1_v"
            # file_name_for_V_dot = "main_method_2_1_v_dot"
            # file_name_extra_info = 'main_method_2_2'

            my_func = lib.run_rigid
            file_name = "rigid_syst_data_w"
            file_name_for_V_dot = "rigid_syst_data_s"
            file_name_extra_info = 'rigid_syst'
        else:
            # my_func = lib.run_main_method_2_const_step
            # file_name = "main_method_2_1_const_step_v"
            # file_name_for_V_dot = "main_method_2_1_const_step_v_dot"
            # file_name_extra_info = 'main_method_2_2_const_step'

            my_func = lib.run_rigid_const_step
            file_name = "rigid_syst_data_const_step_w"
            file_name_for_V_dot = "rigid_syst_data_const_step_s"
            file_name_extra_info = 'rigid_syst_const_step'

        # my_func.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double,
        #                     ctypes.c_double,
        #                     ctypes.c_double, ctypes.c_double, ctypes.c_double]
        my_func.argtypes = [ctypes.c_int, ctypes.c_double,
                            ctypes.c_double,
                            ctypes.c_double, ctypes.c_double]
        my_func.restype = ctypes.c_void_p
        my_func(Nmax, X_end, eps_b, eps, h0)

        self.clear_table(self.info_table_V_dot)


        self.set_table(self.info_table_V_dot, self.file_to_table(file_name_for_V_dot), file_name_for_V_dot)

        self.clear_table(self.info_table)
        table = self.file_to_table(file_name)  # Парсинг файла в табличный вид (тип ячейки:str)

        self.set_table(self.info_table, table, file_name)  # заполнение таблицы(вкладка "Таблица")

        table_extra_info = self.file_to_table(file_name_extra_info)
        self.update_extra_info_table(file_name_extra_info,table_extra_info)  # заполнение вспомогательной информации(правый нижний угол)

        X_arr = [X_start] + [float(row[1]) for row in table]
        V_arr = [w_0] + [float(row[2]) for row in table]

        # if task[0] == 0:
        #     U_arr = [u0] + [float(row[9 if self.step_mode.isChecked() else 6]) for row in table]
        #     self.plt.plot(X_arr, U_arr, label="Аналит. решение")
        # if task[0] == 2:
        #     U_arr = [float(row[2]) for row in table]
        #     dotU_arr = [float(row[2]) for row in self.file_to_table(file_name_for_V_dot)]
        #     self.plt_PS.plot(U_arr, dotU_arr, label="Фазовая кривая")
        #     self.plt_PS.legend(loc="upper right")
        # else:
        #     self.clear_table(self.info_table_V_dot)
        #     self.plt_PS.cla()

        U_arr = [float(row[2]) for row in table]
        dotU_arr = [float(row[2]) for row in self.file_to_table(file_name_for_V_dot)]
        self.plt_PS.plot(U_arr, dotU_arr, label="Фазовая кривая")
        self.plt_PS.legend(loc="upper right")

        self.plt.plot(X_arr, V_arr, label="Числ. решение (V1)")
        self.plt.scatter(X_start, w_0,label="Старт. точка (V1)")  # scatter - построение точечного графика. В данном случае просто ставит точку (x0,u0)

        self.plt.plot(X_arr, [s_0]+dotU_arr, label="Числ. решение (V2)")
        self.plt.scatter(X_start, s_0,label="Старт. точка (V2)")

        self.plt.set_xlim(auto=True)
        self.plt.set_ylim(auto=True)
        self.plt.legend(loc="upper right")  # legend - задание окна легенд

        self.plot_widget_1.canvas.draw()
        self.plot_widget_2.canvas.draw()

    def get_X_start(self):
        return self.X_start.text()

    def get_X_end(self):
        return self.X_end.text()

    # def get_U0(self):
    #     return self.U_X0.text()
    #
    # def get_DU0(self):
    #     return self.DU_X0.text()

    def get_start_step(self):
        return self.step_start.text()

    def get_step_control(self):
        return self.step_control.text()

    def get_border_control(self):
        return self.border_control.text()

    # def get_task(self):
    #     return self.task_selection_box.currentIndex(), self.task_selection_box.currentText()

    def get_step_mode(self):
        return self.step_mode.isChecked()

    def set_row(self, table, row):
        max_row_index = table.rowCount()
        table.insertRow(max_row_index)  # создание строки
        for i in range(len(row)):
            table.setItem(max_row_index, i, QTableWidgetItem(str(row[i])))  # заполнение элементами

    def set_columns(self, table, task_index):
        cols = columns[task_index]
        table.setColumnCount(len(cols))  # создание пустых колонок, в количестве len(cols) штук
        table.setHorizontalHeaderLabels(cols)  # присвоение имен для колонок

    def set_table(self, table, data, task_index):
        self.set_columns(table, task_index)
        for row in data:
            self.set_row(table, row)

    def clear_table(self, table):
        while (table.rowCount() > 0):
            table.removeRow(0)

    def get_num_max_iter(self):
        return self.max_num_iter.text()



