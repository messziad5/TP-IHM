from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem

class TableItem(QGraphicsRectItem):
    def __init__(self, x, y, w, h, controller, name):
        super().__init__(x, y, w, h)
        self.controller = controller
        self.name = name
        self.text_items = []
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.old_pos = self.pos()#موضع قديم 

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:

            delta = value - self.old_pos#nboujiw tableau m3a attributs

            for item in self.text_items:
                item.setPos(item.pos() + delta)

            self.old_pos = value

            self.controller.update_relationships()# les line avec tableaux
        return super().itemChange(change, value)
