import database as db
import gui

# db.dbConnect()
# db.addWaiter("Mike", "Wazowski")
# db.addProduct("Wino", "alkohol", "dobry alkohol", 150.99)
# print(db.addProduct("Łosoś", "danie główne", "taka rybcia", 75)['msg'])
# db.addTable()
# print(db.addBill(1, 1)['msg'])
# db.addProductToBill(1, 1, 5)
# db.addProductToBill(2, 1, 3)
# db.addProductToBill(2, 1, 3)
# db.addProductToBill(1, 1, 2)
# res = db.getBillProducts(1)
# for elem in res:
#   print(str(elem.name) + ": " + str(elem.sum))
# query = db.calculateRevenueByWaiter(1, 2)
# print(db.getBill(1).date)
# for el in db.getListOfWaiters():
#   print(el.name + " " + el.surname)
# print(db.getWaiter(1).name)
# db.deleteWaiter(1)
# print(db.getListOfWaiters())
# db.addWaiter("Joanna", "Janik")
# print(db.getWaiter(1).name)
# db.dbDisconnect()

if __name__ == "__main__":
    import sys
    db.dbConnect()
    app = gui.qtw.QApplication(sys.argv)
    ui = gui.Window()
    db.dbDisconnect()
    sys.exit(app.exec_())