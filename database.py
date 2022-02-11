from peewee import *
import datetime

# For debugging purposes - switch it ON
# import logging

# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

db = SqliteDatabase('database.db')

class BaseModel(Model):
  class Meta:
    database = db

class Table(BaseModel):
  id = AutoField()

class Waiter(BaseModel):
  name = TextField()
  surname = TextField()

class Product(BaseModel):
  name = TextField()
  category = TextField()
  description = TextField()
  price = DecimalField()

class Bill(BaseModel):
  tableID = ForeignKeyField(Table, backref='bills')
  waiterID = ForeignKeyField(Waiter, backref='bills')
  date = DateTimeField()
  closed = BooleanField()

class DishOrder(BaseModel): # list of ordered dishes at the bill
  billID = ForeignKeyField(Bill, backref='dishorders')
  productID = ForeignKeyField(Product, backref='dishorders')
  quantity = IntegerField()

# Database connection utilities

def dbConnect():
  db.connect()
  db.create_tables([Table, Waiter, Product, Bill, DishOrder])
  return {"success": True, "msg": ""}

def dbDisconnect():
  db.close()
  return {"success": True, "msg": ""}

def addTable():
  Table.create()
  return {"success": True, "msg": ""}

def getNumberOfFreeTables():
  return Table.select().count() - getNumberOfOpenBills()

# Staff management

def addWaiter(nameForm, surnameForm):
  if nameForm and surnameForm:
    person = Waiter(name=nameForm, surname=surnameForm)
    person.save()
    return {"success": True, "msg": "Waiter added successfully", "id": person.id}
  else:
    return {"success": False, "msg": "Provide name and surname of the waiter"}

def deleteWaiter(waiterID):
  # assuming that the ID is valid
  Waiter.get(Waiter.id == waiterID).delete_instance()
  return {"success": True, "msg": "Waiter deleted successfully"}

def editWaiter(waiterID, newName, newSurname):
  if newName and newSurname:
    Waiter.update(name=newName, surname=newSurname).where(Waiter.id == waiterID).execute()
    return {"success": True, "msg": "Waiter modified successfully"}
  else:
    return {"success": False, "msg": "Provide name and surname of the waiter"}

def getListOfWaiters():
  return Waiter.select()

def getNumberOfWaiters():
  return Waiter.select().count()

def getWaiter(waiterID):
  return Waiter.get(Waiter.id == waiterID)

# def getWaiterRevenueForPeriod():
#   to be done

# Menu management

def addProduct(nameForm, categoryForm, descriptionForm, priceForm):
  if nameForm and categoryForm and descriptionForm:
    Product(name=nameForm, category=categoryForm, description = descriptionForm, price = priceForm).save()
    return {"success": True, "msg": "Product added successfully"}
  else:
    return {"success": False, "msg": "Provide name, category and description of the product"}

def deleteProduct(productID):
  Product.get(Product.id == productID).delete_instance()
  return {"success": True, "msg": ""}

def getListOfProducts():
  return Product.select()

def getNumberOfProducts():
  return Product.select().count()

def getProduct(productID):
  return Product.get(Product.id == productID)

# Billing and table service

def addBill(tableID, waiterID): # executed when table is sat at
  if Bill.select().where(tableID == tableID).count() > 0:
    return {"success": False, "msg": "This table is already taken"}
  Bill(waiterID = waiterID, tableID = tableID, date = datetime.datetime.now(), closed = False).save()
  return {"success": True, "msg": ""} 

def addProductToBill(prodID, billID, quantity):
  DishOrder(billID = billID, productID = prodID, quantity = quantity).save()
  return {"success": True, "msg": ""}

def editPositionInBill(posID, newQuantity):
  if newQuantity == 0:
      DishOrder.get(id == posID).delete_instance()
  else:
    DishOrder.update(quantity = newQuantity).where(id == posID)
  return {"success": True, "msg": ""}

def deleteBill(billID):
  # first, delete all of the elements of the bill
  DishOrder.delete().where(billID == billID)
  # Then delete the bill itself
  Bill.get(billID == id).delete_instance()
  return {"success": True, "msg": ""}


def getBill(billID):
  return Bill.get(Bill.id == billID)

def getBillProducts(billID):
  return Product.select(Product.name, fn.SUM(DishOrder.quantity).alias("number"), fn.SUM(DishOrder.quantity * Product.price).alias("sum")).join(DishOrder).join(Bill).where(Bill.id == billID).group_by(Product)

def getNumberOfOpenBills():
  return Bill.select(Bill.closed == False).count()

def serveBill(billID):
  Product.update(closed = True).where(id == billID)
  return {"success": True, "msg": "Bill has been served"}

def calculateRevenueByWaiter(waiterID, howManyDaysBack):
  return Waiter.select(Waiter.name, Waiter.surname, fn.SUM(DishOrder.quantity * Product.price).alias("sum")).join(Bill, JOIN.LEFT_OUTER).join(DishOrder).join(Product).where(Waiter.id == waiterID and Bill.date >= datetime.datetime.now() - datetime.timedelta(days = howManyDaysBack)).group_by(Waiter.id).get()