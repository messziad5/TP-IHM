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
        self.btn_new_table = QPushButton("Cree une Table")
        self.btn_add_rel = QPushButton("Ajouter une Relation")
        self.btn_mod_rel = QPushButton("Modifier la Relation")
        self.btn_del_rel = QPushButton("Supprimer la Relation")
        self.btn_delete = QPushButton("Supprimer la Table")

        left.addWidget(self.table_list)
        left.addWidget(self.btn_new_table)
        left.addWidget(self.btn_add_rel)
        left.addWidget(self.btn_mod_rel)
        left.addWidget(self.btn_del_rel)    
        left.addWidget(self.btn_delete)

        left.addSpacing(10)
        left.addWidget(QLabel("Attributes"))
        self.btn_add_attr = QPushButton("Ajouter un Attribut")
        self.btn_mod_attr = QPushButton("Modifier l'Attribut")
        self.btn_del_attr = QPushButton("Supprimer l'Attribut")

        left.addWidget(self.btn_add_attr)
        left.addWidget(self.btn_mod_attr)
        left.addWidget(self.btn_del_attr)


        # CENTER (Canvas)
        center = QVBoxLayout()
        center.addWidget(QLabel("Canvas"))
        self.canvas = QGraphicsView()
        self.scene = QGraphicsScene()
        self.canvas.setScene(self.scene)
        center.addWidget(self.canvas)

        # RIGHT (SQL)
        right = QVBoxLayout()
        right.addWidget(QLabel("SQL Schema"))
        self.sql_view = QTextEdit()
        self.sql_view.setReadOnly(True)
        self.sql_view.setMaximumHeight(300)
        right.addWidget(self.sql_view)

        right.addSpacing(10)

        right.addWidget(QLabel("Generer SQL"))
        self.console_input = QPlainTextEdit()
        self.console_input.setPlaceholderText("Ecrire des commandes SQL ici...")
        right.addWidget(self.console_input)
        
        self.btn_run_console = QPushButton("Executer SQL")
        
        right.addWidget(self.btn_run_console)

        layout.addLayout(left, 1)
        layout.addLayout(center, 3)
        layout.addLayout(right, 1)

        central.setLayout(layout)
        self.setCentralWidget(central)
