from PySide6.QtWidgets import *

class AttributeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Attribute")
        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.type = QComboBox()
        self.type.addItems(["INTEGER", "TEXT", "REAL", "BOOLEAN"])
        self.pk = QCheckBox("Primary Key")
        self.nn = QCheckBox("Not Null")
        self.btn_ok = QPushButton("Add")

        layout.addWidget(QLabel("Attribute name"))
        layout.addWidget(self.name)
        layout.addWidget(QLabel("Type"))
        layout.addWidget(self.type)
        layout.addWidget(self.pk)
        layout.addWidget(self.nn)
        layout.addWidget(self.btn_ok)

        self.setLayout(layout)
