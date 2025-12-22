from PySide6.QtWidgets import *

class RelationshipDialog(QDialog):
    def __init__(self, tables, rel_type=None, src=None, dst=None):
        super().__init__()# preparer qdialog
        self.setWindowTitle("Add Relationship")#title
        layout = QVBoxLayout()

        self.src = QComboBox()
        self.dst = QComboBox()
        self.type_combo = QComboBox()
        self.src.addItems(tables)
        self.dst.addItems(tables)
        self.type_combo.addItems(['1N', '11', 'NN'])

        if src:
            self.src.setCurrentText(src)
        if dst:
            self.dst.setCurrentText(dst)
        if rel_type:
            self.type_combo.setCurrentText(rel_type)

        self.btn_ok = QPushButton("Create")#button pour creer

        layout.addWidget(QLabel("Table 1"))
        layout.addWidget(self.src)
        layout.addWidget(QLabel("Table 2"))
        layout.addWidget(self.dst)
        layout.addWidget(QLabel("Relationship Type"))
        layout.addWidget(self.type_combo)
        layout.addWidget(self.btn_ok)

        self.setLayout(layout)
