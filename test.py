import database as db

db.dbConnect()
lista = db.Waiter.select()

db.addWaiter("Jan", "Bach")
db.dbDisconnect()
#db.Waiter.get(db.Waiter.id == 2)