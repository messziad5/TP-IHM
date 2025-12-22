
from PySide6.QtWidgets import *

class TableDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Table")
        layout=QVBoxLayout()
        layout.addWidget(QLabel("Table name"))
        self.input=QLineEdit()
        layout.addWidget(self.input)
        self.btn_ok=QPushButton("Create")
        layout.addWidget(self.btn_ok)
        self.setLayout(layout)
