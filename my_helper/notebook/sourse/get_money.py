from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QDate as Date
import datetime as dt
from PyQt5.QtWidgets import QMessageBox as mes
import docxtpl
import os
import inserts as ins
main_file = "D:/my_helper/get_money.docx"
print_file = "D:/my_helper/to_print/get_money.docx"
designer_file = '../designer_ui/get_money_2.ui'


class GetMoney(QDialog):
    def __init__(self, parent):
        super(GetMoney, self).__init__()
        uic.loadUi(designer_file, self)
        # pass
        self.parent = parent
        self.table = "finance"
        self.b_ok.clicked.connect(self.ev_ok)
        self.b_cancel.clicked.connect(self.ev_cancel)
        self.b_kill.clicked.connect(self.ev_kill)
        self.b_change.clicked.connect(self.ev_change)

        self.cb_recipient.activated[str].connect(self.change_note)
        self.cb_select.activated[str].connect(self.ev_select)
        # self.cb_manual_set.stateChanged.connect(self.manual_set)
        self.cb_manual_set.setEnabled(False)
        self.cb_day.stateChanged.connect(self.day_money)

        self.note.textChanged.connect(self.change_note)
        self.sb_value.valueChanged[int].connect(self.change_note)
        self.sb_days.valueChanged[int].connect(self.change_note)
        self.sb_emploeeyrs.valueChanged[int].connect(self.change_note)
        self.sb_some_value.valueChanged[int].connect(self.change_note)
        self.sb_cost.valueChanged[int].connect(self.change_note)
        self.cb_some.stateChanged.connect(self.change_note)
        self.cb_day.stateChanged.connect(self.change_note)
        self.date.setDate(dt.datetime.now().date())

        # self.but_status("add")
        self.rows_from_db = self.parent.db.get_data("*", self.table)
        self.cb_select.addItems(["(нет)"])
        for row in self.parent.db.get_data("id, date", self.table):
            self.cb_select.addItems([", ".join((row[0], row[1]))])
        self.parent.db.init_list(self.cb_recipient, "family, name, surname", "itrs", people=True)
        self.parent.db.init_list(self.cb_customer, "family, name, surname", "itrs", people=True)
        self.next_id = self.parent.db.get_next_id(self.table)
        self.current_id = self.next_id
        self.my_id.setValue(self.next_id)
        self.data = {"date": "", "post": "", "family": "", "text": ""}

    def ev_ok(self):
        if not self.check_input():
            return False
        data = self.get_data()
        if not data:
            return

        self.parent.db.my_commit(ins.add_to_db(data, self.table))

        rows = self.parent.db.get_data("post, family, name, surname", "itrs")
        for row in rows:
            if self.cb_customer.currentText() == row[1] + " " + row[2][0] + "." + row[3][0] + ".":
                self.data["post"] = row[0]
                self.data["family"] = self.cb_customer.currentText()
                self.data["text"] = self.note_result.toPlainText()
                self.data["date"] = self.date.text()

        doc = docxtpl.DocxTemplate(main_file)
        doc.render(self.data)
        doc.save(print_file)
        self.close()
        os.startfile(print_file)
        mes.question(self, "Сообщение", "Запись добавлена", mes.Ok)
        self.close()

    def ev_cancel(self):
        self.close()

    def ev_select(self, text):
        if text == "(нет)":
            self.clean_data()
            self.but_status("add")
            return
        else:
            self.but_status("change")
        for row in self.rows_from_db:
            if text in row:
                self.set_data(row)

    def change_note(self, state=None):
        self.sb_some_value.setEnabled(True) if self.cb_some.isChecked() else self.sb_some_value.setEnabled(False)
        self.day_money(self.cb_day.isChecked())
        itr = ""
        people = self.parent.db.get_data("post, family, name", "itrs")
        for boss in people:
            if self.cb_recipient.currentText()[:-5] in boss:
                itr = boss
                break
        text = list()
        text.append("Прошу Вас выслать ")
        text.append(str(self.sb_value.value()))
        text.append(" на банковскую карту ")
        text.append(" ".join(itr[0:2]))
        text.append(" для:\n")
        if self.cb_day.isChecked():
            cost = self.sb_days.value() * self.sb_emploeeyrs.value() * self.sb_cost.value()
            text.append("- {0}р. суточные из расчета {1} дней/я {2} чел. {3}р. ставка\n".format(cost,
                                                                                           self.sb_days.value(),
                                                                                           self.sb_emploeeyrs.value(),
                                                                                           self.sb_cost.value()))
        if self.cb_some.isChecked():
            text.append("- {0}р. на производственные нужды\n".format(self.sb_some_value.value()))
        if self.note.toPlainText():
            text.append(" - " + self.note.toPlainText())
        self.note_result.setText(" ".join(text))

    def day_money(self, state):
        if state:
            self.sb_days.setEnabled(True)
            self.sb_emploeeyrs.setEnabled(True)
            self.sb_cost.setEnabled(True)
        else:
            self.sb_days.setEnabled(False)
            self.sb_emploeeyrs.setEnabled(False)
            self.sb_cost.setEnabled(False)

    def ev_change(self):
        answer = mes.question(self, "Изменение записи", "Вы действительно хотите изменить запись на " +
                              str(self.get_data()) + "?", mes.Ok | mes.Cancel)
        if answer == mes.Ok:
            data = self.get_data()
            data[-1] = str(self.current_id)
            self.parent.db.my_update(data, self.table)
            answer = mes.question(self, "Сообщение", "Запись изменена", mes.Ok)
            if answer == mes.Ok:
                self.close()

    def ev_kill(self):
        answer = mes.question(self, "Удаление записи", "Вы действительно хотите удалить запись " +
                              str(self.get_data()) + "?", mes.Ok | mes.Cancel)
        if answer == mes.Ok:
            self.parent.db.kill_value(self.current_id, self.table)
            answer = mes.question(self, "Сообщение", "Запись удалена", mes.Ok)
            if answer == mes.Ok:
                self.close()

    def set_data(self, data):
        self.sb_number.setValue(data[0])
        self.date.setDate(Date.fromString(data[1], "dd.mm.yyyy"))
        self.sb_value.Value(int(data[2]))
        i = range(len(self.rows_from_db))
        for row in self.rows_from_db:
            self.cb_recipient.setCurrentIndex(next(i)) if data[3] in row else next(i)
        self.note.clear()
        self.note.append(data[4])

    def get_data(self):
        cost = self.sb_days.value() * self.sb_emploeeyrs.value() * self.sb_cost.value()
        if cost + self.sb_some_value.value() > self.sb_value.value():
            QMessageBox.question(self, "Внимание",
                                 "Сумма в итоге меньше, чем сумма пунктов. Вы хотите за своих оплачивать?))",
                                 QMessageBox.Ok | QMessageBox.Cancel)
            return
        if not self.note.toPlainText():
            if cost + self.sb_some_value.value() != self.sb_value.value():
                QMessageBox.question(self, "Внимание", "Не сходится сумма, напишите куда именно вы потратите разницу",
                                     QMessageBox.Ok)
                return
        data = list()
        data.append(self.date.text())
        data.append(str(self.sb_value.value()))
        data.append(self.cb_customer.currentText())

        if self.cb_day.isChecked():
            data.append("суточные {0} чел {1} дней {2}р. ставка".format(self.sb_days.value(),
                                                                        self.sb_emploeeyrs.value(),
                                                                        self.sb_cost.value()))
        if self.cb_some.isChecked():
            if len(data) == 2:
                data.append("производственные нужды " + self.sb_some_value.value())
            else:
                data[3] = data[3] + "| производственные нужды " + str(self.sb_some_value.value())
        if self.note.toPlainText():
            if len(data) == 2:
                data.append(self.note.toPlainText())
            else:
                data[3] = data[3] + "| " + self.note.toPlainText()
        data.append(str(self.my_id.value()))
        return data

    def check_input(self):
        if self.sb_value.value() == 0:
            mes.question(self, "Сообщение", "Укажите общую сумму", mes.Cancel)
            return False
        if self.cb_recipient.currentText() == "(нет)":
            mes.question(self, "Сообщение", "Укажите получателя перевода", mes.Cancel)
            return False
        if self.cb_day.isChecked():
            cost = self.sb_days.value() * self.sb_emploeeyrs.value() * self.sb_cost.value()
            if cost == 0:
                mes.question(self, "Сообщение", "Укажите значения в суточных или уберите галочку", mes.Cancel)
                return False
        if self.cb_some.isChecked():
            if self.sb_some_value.value() == 0:
                mes.question(self, "Сообщение", "Укажите значения в производственных нуждах или уберите галочку",
                             mes.Cancel)
                return False
        return True

    def clean_data(self):
        self.sb_recipient.setCurrentIndex(0)
        self.sb_value.setValue(0)
        self.note.clear()
        self.cb_day.setCheacked(False)
        self.sb_day.setValue(0)
        self.sb_emploeers.setValue(0)

    def but_status(self, status):
        if status == "add":
            self.b_ok.setEnabled(True)
            self.b_change.setEnabled(False)
            self.b_kill.setEnabled(False)
        if status == "change":
            self.b_ok.setEnabled(False)
            self.b_change.setEnabled(True)
            self.b_kill.setEnabled(True)
