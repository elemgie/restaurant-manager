# Rat picture: https://picsart.com/i/292143013006211

import database as db
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from autogui import Ui_MainMenu


class Window(qtw.QWidget, Ui_MainMenu):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.MainMenu = qtw.QMainWindow()
    self.setupUi(self.MainMenu)

    # prepare waiters' table
    self.waitersNumber.setNum(db.getNumberOfWaiters())
    self.showTableContents(self.waitersTable, db.Waiter)
    self.selectedWaitersRow = None
    self.waitersTable.horizontalHeader().sortIndicatorChanged.connect(self.waitersTable.clearSelection)
    self.waitersTable.horizontalHeader().sortIndicatorChanged.connect(self.waiterNameInput.clear)
    self.waitersTable.horizontalHeader().sortIndicatorChanged.connect(self.waiterSurnameInput.clear)


    self.productsNumber.setNum(db.getNumberOfProducts())
    self.freeTablesNumber.setNum(db.getNumberOfFreeTables())
    self.openBillsNumber.setNum(db.getNumberOfOpenBills())

    # connecting actions
    self.exitButton.clicked.connect(qtc.QCoreApplication.instance().quit)
    self.waiterAddButton.clicked.connect(self.addWaiter)
    self.waitersTable.itemClicked.connect(self.printWaiterOnSelection)
    self.waiterEditButton.clicked.connect(self.editWaiter)
    self.waiterDeleteButton.clicked.connect(self.deleteWaiter)
    self.revenueButton.clicked.connect(self.calculateRevenue)


    self.MainMenu.show()

  def showInformationWindow(self, input):
    if input['success']:
        qtw.QMessageBox.information(None, "Success", input['msg'])
    else:
        qtw.QMessageBox.critical(None, "Failure", input['msg'])

  def showTableContents(self, table, content):
    contList = content.select()
    if contList.count() == 0:
      return
    columnNumber = len(contList.get().__data__.keys())
    for elem in contList:
      table.insertRow(table.rowCount())
      for col in range(columnNumber):
        table.setItem(table.rowCount() - 1, col, qtw.QTableWidgetItem(str(elem.__data__[list(elem.__data__.keys())[col]])))

  # Waiter's utilities

  def addWaiter(self):
    name = self.waiterNameInput.text()
    surname = self.waiterSurnameInput.text()
    self.waiterNameInput.clear()
    self.waiterSurnameInput.clear()
    res = db.addWaiter(name, surname)
    if res['success']:
      self.waitersNumber.setNum(db.getNumberOfWaiters())
      self.waitersTable.insertRow(self.waitersTable.rowCount())
      self.waitersTable.setItem(self.waitersTable.rowCount() - 1, 0, qtw.QTableWidgetItem(str(res['id'])))
      self.waitersTable.setItem(self.waitersTable.rowCount() - 1, 1, qtw.QTableWidgetItem(name))
      self.waitersTable.setItem(self.waitersTable.rowCount() - 1, 2, qtw.QTableWidgetItem(surname))
    self.showInformationWindow(res)

  def printWaiterOnSelection(self):
    self.selectedWaitersRow = int(self.waitersTable.selectionModel().selectedRows()[0].row())
    self.waiterNameInput.setText(self.waitersTable.item(self.selectedWaitersRow, 1).text())
    self.waiterSurnameInput.setText(self.waitersTable.item(self.selectedWaitersRow, 2).text())

  def clearAfterWaitersTableAlternation(self):
    self.waiterNameInput.clear()
    self.waiterSurnameInput.clear()
    self.waitersTable.clearSelection()
    self.selectedWaitersRow = None

  def editWaiter(self):
    if self.selectedWaitersRow == None:
      qtw.QMessageBox.information(None, "Warning", "Choose entry to be modified first!")
      return
    id = int(self.waitersTable.item(self.selectedWaitersRow, 0).text())
    newName = self.waiterNameInput.text()
    newSurname = self.waiterSurnameInput.text()
    oldName = self.waitersTable.item(self.selectedWaitersRow, 1).text()
    oldSurname = self.waitersTable.item(self.selectedWaitersRow, 2).text()

    confirmationWindow = qtw.QMessageBox
    ret = confirmationWindow.question(None, "Modification confirmation", f"Do you wish to change the following entry?\n\nOld name: {oldName}\nOld surname: {oldSurname}\n\nNew name: {newName}\nNew surname: {newSurname}", qtw.QMessageBox.Yes | qtw.QMessageBox.No)
    if ret == confirmationWindow.Yes:
      res = db.editWaiter(id, newName, newSurname)
      self.showInformationWindow(res)
      if res['success']:
        self.waitersTable.setItem(self.selectedWaitersRow, 1, qtw.QTableWidgetItem(newName))
        self.waitersTable.setItem(self.selectedWaitersRow, 2, qtw.QTableWidgetItem(newSurname))
        self.clearAfterWaitersTableAlternation()
        
  
  def deleteWaiter(self):
    if self.selectedWaitersRow == None:
      qtw.QMessageBox.information(None, "Warning", "Choose entry to be deleted first!")
      return
    id = int(self.waitersTable.item(self.selectedWaitersRow, 0).text())
    oldName = self.waitersTable.item(self.selectedWaitersRow, 1).text()
    oldSurname = self.waitersTable.item(self.selectedWaitersRow, 2).text()
    confirmationWindow = qtw.QMessageBox
    ret = confirmationWindow.question(None, "Deletion confirmation", f"Do you wish to delete the following entry?\n\nName: {oldName}\nSurname: {oldSurname}", qtw.QMessageBox.Yes | qtw.QMessageBox.No)
    if ret == confirmationWindow.Yes:
      res = db.deleteWaiter(id)
      self.showInformationWindow(res)
      self.waitersTable.removeRow(self.selectedWaitersRow)
      self.waitersNumber.setNum(int(self.waitersNumber.text()) - 1)
      if res['success']:
        self.clearAfterWaitersTableAlternation()
  
  def calculateRevenue(self):
    if self.selectedWaitersRow == None:
      qtw.QMessageBox.information(None, "Warning", "Choose waiter whose revenue you want to calculate!")
      return
    