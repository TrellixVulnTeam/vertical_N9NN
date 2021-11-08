from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QMessageBox as mes
import docxtpl
import os
import datetime as dt
from my_helper.notebook.sourse.database import *


class Journal(QDialog):
    def __init__(self, parent):
        super(Journal, self).__init__()
        self.conf = Ini(self)
        self.ui_file = self.conf.get_path_ui("journal")
        if not self.check_start():
            return
        self.parent = parent
        self.path = parent.path + self.conf.get_path("docs") + "/Журнал.docx"
        self.b_print.clicked.connect(self.ev_print)
        self.data = dict()
        self.init_bosses()
        self.name.append("По ")

    def check_start(self):
        self.status_ = True
        self.path_ = self.conf.get_path_ui("journal")
        try:
            uic.loadUi(self.ui_file, self)
            return True
        except:
            mes.question(self, "Сообщение", "Не удалось открыть форму " + self.ui_file, mes.Cancel)
            self.status_ = False
            return False

    def init_bosses(self):
        self.parent.parent.db.init_list(self.boss_1, "*", "itrs", people=True)
        self.parent.parent.db.init_list(self.boss_2, "*", "itrs", people=True)
        self.parent.parent.db.init_list(self.boss_3, "*", "bosses", people=True)
        self.parent.parent.db.init_list(self.boss_4, "*", "bosses", people=True)
        pass

    def get_data(self):
        data = dict()
        data["name"] = self.name.toPlainText()
        data["numb"] = str(self.number.value())
        data["boss_1"] = "".join(self.boss_1.currentText().split(". ")[1:])
        data["boss_2"] = "".join(self.boss_2.currentText().split(". ")[1:])
        data["boss_3"] = "".join(self.boss_3.currentText().split(". ")[1:])
        data["boss_4"] = "".join(self.boss_4.currentText().split(". ")[1:])
        data["post_1"] = self.get_post(self.boss_1.currentText().split(".")[0], "itrs")
        data["post_2"] = self.get_post(self.boss_2.currentText().split(".")[0], "itrs")
        data["post_3"] = self.get_post(self.boss_3.currentText().split(".")[0], "bosses")
        data["post_4"] = self.get_post(self.boss_4.currentText().split(".")[0], "bosses")
        data["date"] = self.date.text()
        data["year"] = str(dt.datetime.now().year)
        data["company"] = self.parent.parent.company
        data["customer"] = self.parent.parent.customer
        return data

    def get_post(self, my_id, table):
        rows = self.parent.parent.db.get_data("*", table)
        for item in rows:
            if str(item[-1]) == my_id:
                print(item)
                return item[3]
        return "."

    def ev_print(self):
        self.data = self.get_data()
        if not self.check_input():
            return False
        try:
            path = self.conf.get_path("path") + self.conf.get_path("path_pat_patterns") + "/Журнал.docx"
            doc = docxtpl.DocxTemplate(path)
        except:
            mes.question(self, "Сообщение", "Файл " + path + " не найден", mes.Ok)
            return False
        doc.render(self.data)
        doc.save(self.parent.path + "/Журнал работ.docx")
        self.close()

    def check_input(self):
        if self.number.value() == 0:
            mes.question(self, "Сообщение", "Укажите номер журнала", mes.Ok)
            return False
        if self.date.text() == "01.01.2000":
            mes.question(self, "Сообщение", "Укажите дату начала работ", mes.Ok)
            return False
        if self.boss_1.currentText() == "(нет)":
            mes.question(self, "Сообщение", "Укажите первого босса", mes.Ok)
            return False
        if self.boss_2.currentText() == "(нет)":
            mes.question(self, "Сообщение", "Укажите второго босса", mes.Ok)
            return False
        if self.boss_3.currentText() == "(нет)":
            mes.question(self, "Сообщение", "Укажите третьего босса", mes.Ok)
            return False
        if self.boss_4.currentText() == "(нет)":
            mes.question(self, "Сообщение", "Укажите четвертого босса", mes.Ok)
            return False
        if self.name.toPlainText() == "" or len(self.name.toPlainText()) < 3:
            mes.question(self, "Сообщение", "Укажите название журнала", mes.Ok)
            return False
        return True