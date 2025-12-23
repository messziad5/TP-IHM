from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

class AttributeDialog(QDialog):
    def __init__(self, attribute=None):
        super().__init__()
        self.attribute = attribute
        self.setWindowTitle("Add Attribute" if not attribute else "Modify Attribute")
        self.setModal(True)
        self.resize(300, 200)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter attribute name")
        if attribute:
            self.name.setText(attribute.name)

        self.type = QComboBox()
        self.type.addItems(["INTEGER", "TEXT", "REAL", "BOOLEAN", "DATE"])
        if attribute:
            self.type.setCurrentText(attribute.dtype)

        self.pk = QCheckBox("Primary Key")
        if attribute:
            self.pk.setChecked(attribute.primary_key)

        self.nn = QCheckBox("Not Null")
        if attribute:
            self.nn.setChecked(not attribute.nullable)

        form_layout.addRow("Attribute name:", self.name)
        form_layout.addRow("Type:", self.type)
        form_layout.addRow(self.pk)
        form_layout.addRow(self.nn)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Add" if not attribute else "Modify")
        self.btn_ok.setDefault(True)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_ok)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.btn_ok.clicked.connect(self.accept)
