
from PySide6.QtWidgets import QApplication
from model.schema import Schema
from view.main_view import MainView
from controller.main_controller import MainController
import sys

def main():
    app=QApplication(sys.argv)
    model=Schema()
    view=MainView()
    controller=MainController(model,view)
    view.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
