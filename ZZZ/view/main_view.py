from PySide6.QtWidgets import *

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DB Schema Designer")

        central = QWidget()
        layout = QHBoxLayout()

        # LEFT
        left = QVBoxLayout()
        left.addWidget(QLabel("Tables"))
        self.table_list = QListWidget()
        self.btn_new_table = QPushButton("New Table")
        self.btn_add_rel = QPushButton("Add Relationship")
        self.btn_mod_rel = QPushButton("Modify Relationship")
        self.btn_del_rel = QPushButton("Delete Relationship")
        self.btn_delete = QPushButton("Delete Table")

        left.addWidget(self.table_list)
        left.addWidget(self.btn_new_table)
        left.addWidget(self.btn_add_rel)
        left.addWidget(self.btn_mod_rel)
        left.addWidget(self.btn_del_rel)    
        left.addWidget(self.btn_delete)

        # CENTER (Canvas)
        center = QVBoxLayout()
        center.addWidget(QLabel("Canvas"))
        self.canvas = QGraphicsView()
        self.scene = QGraphicsScene()
        self.canvas.setScene(self.scene)
        center.addWidget(self.canvas)

        # RIGHT (SQL)
        right = QVBoxLayout()
        right.addWidget(QLabel("SQL Output"))
        self.sql_view = QTextEdit()
        self.sql_view.setReadOnly(True)
        self.sql_view.setMaximumHeight(300)
        right.addWidget(self.sql_view)

        right.addSpacing(10)

        right.addWidget(QLabel("Generer SQL"))
        self.console_input = QPlainTextEdit()
        self.console_input.setPlaceholderText("Write your SQL commands here...")
        right.addWidget(self.console_input)
        
        self.btn_run_console = QPushButton("Executer SQL")
        
        right.addWidget(self.btn_run_console)

        layout.addLayout(left, 1)
        layout.addLayout(center, 3)
        layout.addLayout(right, 1)

        central.setLayout(layout)
        self.setCentralWidget(central)
