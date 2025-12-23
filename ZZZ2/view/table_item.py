from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem
from PySide6.QtGui import QBrush, QPen, QColor, QFont
from PySide6.QtCore import Qt

class TableItem(QGraphicsRectItem):
    def __init__(self, x, y, w, h, controller, name):
        super().__init__(x, y, w, h)
        self.controller = controller
        self.name = name
        self.attached_items = []  # All items that should move with the table
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.old_pos = self.pos()

        # Enhanced styling
        self.setBrush(QBrush(QColor(240, 248, 255)))  # Light blue background
        self.setPen(QPen(QColor(70, 130, 180), 2))    # Steel blue border

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            delta = value - self.old_pos

            for item in self.attached_items:
                item.setPos(item.pos() + delta)

            self.old_pos = value
            self.controller.update_relationships()
        return super().itemChange(change, value)
