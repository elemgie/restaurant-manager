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
  """Represents an instance of a restaurant table"""

  id = AutoField()

class Waiter(BaseModel):
  """Represents an instance of an employed waiter"""

  name = TextField()
  surname = TextField()

class Product(BaseModel):
  """Represents an instance of a product/dish that is in the menu"""

  name = TextField()
  price = DecimalField()
  description = TextField()

class Bill(BaseModel):
  """Represents an instance of a bill
  
  Whenever clients sit at the table, bill is created. Furthermore, with orders for specific products being done, the bill is extended and in the end it is closed and clients pay sum specified by it
  """

  tableID = ForeignKeyField(Table, backref='bills')
  waiterID = ForeignKeyField(Waiter, backref='bills')
  date = DateTimeField()
  closed = BooleanField()

class DishOrder(BaseModel):
  """Joint table for many-to-many relationship between bill and product"""

  billID = ForeignKeyField(Bill, backref='dishorders')
  productID = ForeignKeyField(Product, backref='dishorders')
  quantity = IntegerField()

# Database connection utilities

def dbConnect():
  """Create database and its tables"""

  db.connect()
  db.create_tables([Table, Waiter, Product, Bill, DishOrder])
  return {"success": True, "msg": ""}

def dbDisconnect():
  """Safely disconnect from database engine"""

  db.close()
  return {"success": True, "msg": ""}

def addTable():
  """Create a new table instance and put it into the database"""

  table = Table()
  table.save()
  return {"success": True, "msg": "Table added successfully", "id": table.id}

def deleteTable(tableID):
  Table.get(Table.id == tableID).delete_instance()
  return {"success": True, "msg": "Table deleted successfully"}

def getNumberOfFreeTables():
  return Table.select().count() - getNumberOfOpenBills()

def getListOfFreeTables():
  return Table.select().join(Bill, JOIN.LEFT_OUTER).where(Bill.id.is_null())

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

def addProduct(nameForm, descriptionForm, priceForm):
  if nameForm and descriptionForm:
    prod = Product(name=nameForm, description = descriptionForm, price = priceForm)
    prod.save()
    return {"success": True, "msg": "Product added successfully", "id": prod.id}
  else:
    return {"success": False, "msg": "Provide name and description of the product"}

def deleteProduct(productID):
  Product.get(Product.id == productID).delete_instance()
  return {"success": True, "msg": "Product deleted successfully"}

def editProduct(productID, newName, newDescription, newPrice):
  if newName and newDescription:
    Product.update(name=newName, description=newDescription, price=newPrice).where(Product.id == productID).execute()
    return {"success": True, "msg": "Product modified successfully"}
  else:
    return {"success": False, "msg": "Provide name and description of the product"}

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
  return {"success": True, "msg": "Bill has been successfully created"} 

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
  res = Waiter.select(Waiter.name, Waiter.surname, fn.SUM(DishOrder.quantity * Product.price).alias("sum")).join(Bill, JOIN.LEFT_OUTER).join(DishOrder).join(Product).where(Waiter.id == waiterID and Bill.date >= datetime.datetime.now() - datetime.timedelta(days = howManyDaysBack)).group_by(Waiter.id)
  if res.exists():
    return {"success": True, "ret": res}
  else:
    return {"success": False, "ret": None}