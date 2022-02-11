import database as db
import gui
import sys

if __name__ == "__main__":
    """Main routine for the application, handles database connection and GUI start"""
    
    db.dbConnect()
    app = gui.qtw.QApplication(sys.argv)
    ui = gui.Window()
    db.dbDisconnect()
    sys.exit(app.exec_())