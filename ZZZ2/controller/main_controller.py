from cmath import rect
from turtle import title
import math
from model.schema import Table, Attribute, Relationship
from view.table_dialog import TableDialog
from view.attribute_dialog import AttributeDialog
from view.relationship_dialog import RelationshipDialog
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QMessageBox, QInputDialog
from view.table_item import TableItem
from PySide6.QtGui import QPen, QColor, QFont
from PySide6.QtCore import Qt

class MainController:

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.y = 0
        self.table_items = {}
        self._connect()
        self.relationship_lines = []  # liste des lignes de relation


    def _connect(self):
        self.view.btn_new_table.clicked.connect(self.open_table_dialog)
        self.view.table_list.itemDoubleClicked.connect(self.add_attribute)
        self.view.btn_add_rel.clicked.connect(self.add_relationship)
        self.view.btn_mod_rel.clicked.connect(self.modify_relationship)
        self.view.btn_del_rel.clicked.connect(self.delete_relationship)
        self.view.btn_delete.clicked.connect(self.delete_table)
        self.view.btn_add_attr.clicked.connect(self.add_attribute_to_selected)
        self.view.btn_mod_attr.clicked.connect(self.modify_attribute)
        self.view.btn_del_attr.clicked.connect(self.remove_attribute)
        self.view.btn_run_console.clicked.connect(self.run_manual_sql)

    def open_table_dialog(self):
        d = TableDialog()
        d.btn_ok.clicked.connect(lambda: self.create_table(d))
        d.exec()

    def create_table(self, d):
        name = d.input.text().strip()
        if name:
            if self.model.get_table(name):
                QMessageBox.warning(self.view, "La Table existe déjà", f"Table '{name}' existe déjà.")
                return
            t = Table(name)
            self.model.add_table(t)
            self.view.table_list.addItem(name)
            self.redraw()
        d.close()    

    def add_attribute(self, item):
        table = self.model.get_table(item.text())
        if not table: return
        d = AttributeDialog()
        d.btn_ok.clicked.connect(lambda: self.save_attribute(d, table))
        d.exec()

    def save_attribute(self, d, table):
        attr = Attribute(
            d.name.text(),
            d.type.currentText(),
            not d.nn.isChecked(),
            d.pk.isChecked()
        )
        table.add_attribute(attr)
        self.redraw()
        d.close()    

    def add_attribute_to_selected(self):
        item = self.view.table_list.currentItem()
        if not item:
            QMessageBox.information(self.view, "Aucune Table Sélectionnée", "Veuillez d'abord sélectionner une table.")
            return
        self.add_attribute(item)

    def modify_attribute(self):
        item = self.view.table_list.currentItem()
        if not item:
            QMessageBox.information(self.view, "Aucune Table Sélectionnée", "Veuillez d'abord sélectionner une table.")
            return
        table = self.model.get_table(item.text())
        if not table or not table.attributes:
            QMessageBox.information(self.view, "Aucune Attribut", "La table sélectionnée n'a pas d'attributs.")
            return

        # For simplicity, show a list of attributes to choose
        attr_names = [a.name for a in table.attributes]
        attr_name, ok = QInputDialog.getItem(self.view, "Sélectionner un Attribut", "Choisissez l'attribut à modifier:", attr_names, 0, False)
        if not ok: return
        attr = next((a for a in table.attributes if a.name == attr_name), None)
        if not attr: return

        d = AttributeDialog(attribute=attr)
        d.btn_ok.clicked.connect(lambda: self.update_attribute(d, table, attr))
        d.exec()

    def update_attribute(self, d, table, old_attr):
        new_attr = Attribute(
            d.name.text(),
            d.type.currentText(),
            not d.nn.isChecked(),
            d.pk.isChecked()
        )
        table.update_attribute(old_attr, new_attr)
        self.redraw()
        d.close()

    def remove_attribute(self):
        item = self.view.table_list.currentItem()
        if not item:
            QMessageBox.information(self.view, "Aucune Table Sélectionnée", "Veuillez d'abord sélectionner une table.")
            return
        table = self.model.get_table(item.text())
        if not table or not table.attributes:
            QMessageBox.information(self.view, "Aucune Attribut", "La table sélectionnée n'a pas d'attributs.")
            return

        attr_names = [a.name for a in table.attributes]
        attr_name, ok = QInputDialog.getItem(self.view, "Sélectionner un Attribut", "Choisissez l'attribut à supprimer:", attr_names, 0, False)
        if not ok: return
        attr = next((a for a in table.attributes if a.name == attr_name), None)
        if not attr: return

        reply = QMessageBox.question(self.view, "Confirmer", f"Supprimer l'attribut '{attr_name}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            table.remove_attribute(attr)
            self.redraw()    

    def add_relationship(self):
        names = [t.name for t in self.model.tables]
        if len(names) < 2:
            return
        d = RelationshipDialog(names)
        d.btn_ok.clicked.connect(lambda: self.create_relationship(d))
        d.exec()

    def create_relationship(self, d):
        t1_name = d.src.currentText()
        t2_name = d.dst.currentText()
        rel_type = d.type_combo.currentText()

        if t1_name == t2_name and rel_type in ['11', 'NN', '1N']:
            QMessageBox.warning(self.view, "Invalid Relationship", f"Cannot create a {rel_type} relationship between the same table.")
            return
        
        table1 = self.model.get_table(t1_name)
        table2 = self.model.get_table(t2_name)
        
        pk1 = next((a.name for a in table1.attributes if a.primary_key), "id")
        pk2 = next((a.name for a in table2.attributes if a.primary_key), "id")  

        new_rel = Relationship(t1_name, t2_name, rel_type)

        new_rel.fk_table_name = None
        new_rel.fk_column_name = None
        pivot_name = None

        if rel_type in ['1N', '11']:
            fk_name = f"{t1_name.lower()}_{pk1}"
            if not any(a.name == fk_name for a in table2.attributes):
                table2.add_attribute(Attribute(fk_name, "INTEGER"))
                table2.add_foreign_key(fk_name, t1_name, pk1)

                new_rel.fk_table_name = t2_name
                new_rel.fk_column_name = fk_name          

        elif rel_type == 'NN':
            pivot_name = f"{t1_name}_{t2_name}"
            if not self.model.get_table(pivot_name):
                pivot_table = Table(pivot_name)
                col1, col2 = f"{t1_name.lower()}_{pk1}", f"{t2_name.lower()}_{pk2}"
                pivot_table.add_attribute(Attribute(col1, "INTEGER"))
                pivot_table.add_attribute(Attribute(col2, "INTEGER"))
                pivot_table.add_foreign_key(col1, t1_name, pk1)
                pivot_table.add_foreign_key(col2, t2_name, pk2)
                self.model.add_table(pivot_table)
                self.view.table_list.addItem(pivot_name)

        if pivot_name: new_rel.pivot_table_name = pivot_name
        self.model.add_relationship(new_rel)
        
        self.redraw() # appeller la fonction redraw
        d.close()

        #relations responsive
    def update_relationships(self):
        for rel, line, label in self.relationship_lines:
            t1_item = self.table_items.get(rel.table1)
            t2_item = self.table_items.get(rel.table2)
            if t1_item and t2_item:
                r1 = t1_item.sceneBoundingRect()
                r2 = t2_item.sceneBoundingRect()
                line.setLine(r1.right(), r1.center().y(), r2.left(), r2.center().y())
                label.setPos((r1.right() + r2.left()) / 2, (r1.center().y() + r2.center().y()) / 2 - 10)
    

    def draw_relationship_line(self, rel):
        if rel.table1 not in self.table_items or rel.table2 not in self.table_items:
            return
        line = QGraphicsLineItem(0, 0, 0, 0)
        line.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.view.scene.addItem(line)
        
        label = QGraphicsTextItem(rel.rel_type)
        label.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.view.scene.addItem(label)
        
        self.relationship_lines.append((rel, line, label))
        self.update_relationships()

    def redraw(self):
        self.view.scene.clear()
        self.table_items.clear()
        self.relationship_lines.clear()
        self.y = 0
        
        for t in self.model.tables:
            self.draw_table(t)

        self.update_relationships()

        self.view.sql_view.setPlainText(self.model.generate_sql())

    def draw_table(self, table):# dessiner un tableau sur le canvas
        height = 40 + 20 * len(table.attributes)  
        x_pos = 0

        rect = TableItem(
            x_pos,
            self.y,
            200,  # Fixed width
            height,
            controller=self,
            name=table.name
        )
        
        rect.setZValue(0)
        self.view.scene.addItem(rect)
        self.table_items[table.name] = rect

        rect.attached_items = []

        title = QGraphicsTextItem(table.name)
        # Center the title
        from PySide6.QtGui import QFontMetrics
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(table.name)
        title_x = x_pos + (200 - text_width) / 2
        title.setPos(title_x, self.y + 5)
        title.setZValue(1)
        title.setFont(font)
        title.setDefaultTextColor(QColor(25, 25, 112))  # Dark blue
        self.view.scene.addItem(title)
        rect.attached_items.append(title)

        # ligne entre le titre et les attributs
        from PySide6.QtWidgets import QGraphicsLineItem
        header_line = QGraphicsLineItem(x_pos, self.y + 25, x_pos + 200, self.y + 25)
        header_line.setPen(QPen(QColor(70, 130, 180), 1))
        header_line.setZValue(1)
        self.view.scene.addItem(header_line)
        rect.attached_items.append(header_line)

        y_text = self.y + 30
        for attr in table.attributes:
            # verifier si l'attribut est une clé étrangère
            is_fk = any(fk_col == attr.name for fk_col, _, _ in table.foreign_keys)
            
            # nom de l'attribut
            txt = QGraphicsTextItem(attr.name)
            txt.setPos(x_pos + 15, y_text)
            txt.setZValue(1)
            
            # amélioration du style du texte
            font = txt.font()
            font.setPointSize(9)
            
            if attr.primary_key:
                font.setBold(True)
                txt.setDefaultTextColor(QColor(139, 69, 19))  # color brun pour PK
                # ajout de l'indicateur PK
                pk_indicator = QGraphicsTextItem("(PK)")
                pk_indicator.setPos(x_pos + 170, y_text)
                pk_indicator.setZValue(1)
                self.view.scene.addItem(pk_indicator)
                rect.attached_items.append(pk_indicator)
            elif is_fk:
                txt.setDefaultTextColor(QColor(34, 139, 34))  # color vert pour FK
                # ajout de l'indicateur FK
                fk_indicator = QGraphicsTextItem("(FK)")
                fk_indicator.setPos(x_pos + 170, y_text)
                fk_indicator.setZValue(1)
                self.view.scene.addItem(fk_indicator)
                rect.attached_items.append(fk_indicator)
            else:
                txt.setDefaultTextColor(QColor(47, 79, 79))  # color gris foncé pour les autres
            
            txt.setFont(font)
            self.view.scene.addItem(txt) 
            rect.attached_items.append(txt)
            
            # type de l'attribut
            type_text = QGraphicsTextItem(attr.dtype)
            type_text.setPos(x_pos + 120, y_text)
            type_text.setZValue(1)
            type_font = type_text.font()
            type_font.setPointSize(8)
            type_font.setItalic(True)
            type_text.setFont(type_font)
            type_text.setDefaultTextColor(QColor(105, 105, 105))  # Dim gray
            self.view.scene.addItem(type_text)
            rect.attached_items.append(type_text)
            
            y_text += 20

        self.y += height + 30  

    def run_manual_sql(self):
        query = self.view.console_input.toPlainText().strip()
        if not query: return

         # 1. Exécuter la requête SQL
        success, message = self.model.execute_sql(query)

        if success:
            query_upper = query.upper()
            from model.schema import Table, Attribute, Relationship

            try:
                # nettoyer et diviser la requête pour l'analyse
                clean_query = query.replace('(', ' ( ').replace(')', ' ) ').replace(',', ' , ').replace(';', '')
                parts = clean_query.split()
                parts_upper = [p.upper() for p in parts]

                # cas 1: CREATE TABLE 
                if query_upper.startswith("CREATE TABLE"):
                    table_name = parts[2]
                    if not self.model.get_table(table_name):
                        new_table = Table(table_name)
                        if "(" in query:
                            content = query[query.find("(")+1 : query.rfind(")")]
                            definitions = content.split(",")
                            found_refs = []

                            for def_item in definitions:
                                d_parts = def_item.strip().split()
                                if len(d_parts) >= 2:
                                    col_name, col_type = d_parts[0], d_parts[1]
                                    is_pk = "PRIMARY" in def_item.upper()
                                    new_table.add_attribute(Attribute(col_name, col_type, primary_key=is_pk))
                                    
                                    if "REFERENCES" in def_item.upper():
                                        ref_idx = d_parts.index("REFERENCES")
                                        ref_t = d_parts[ref_idx + 1].split('(')[0]
                                        new_table.add_foreign_key(col_name, ref_t, "id")
                                        found_refs.append(ref_t)

                            if len(found_refs) >= 2:
                                self.model.add_relationship(Relationship(found_refs[0], found_refs[1], "NN", pivot_table_name=table_name))
                            elif len(found_refs) == 1:
                                self.model.add_relationship(Relationship(found_refs[0], table_name, "1N"))

                        self.model.add_table(new_table)
                        self.view.table_list.addItem(table_name)

                # cas 2: ALTER TABLE AjOUTER COLONNE
                elif "ALTER TABLE" in query_upper and "ADD" in query_upper:
                    t_name = parts[2]
                    target_table = self.model.get_table(t_name)
                    if target_table:
                        if "REFERENCES" in parts_upper:
                            ref_idx = parts_upper.index("REFERENCES")
                            start_idx = parts_upper.index("ADD") + 1
                            if parts_upper[start_idx] == "COLUMN": start_idx += 1
                            
                            fk_c = parts[start_idx] # nom de la colonne
                            # déterminer le type de données de la colonne 
                            type_parts = parts[start_idx + 1 : ref_idx]
                            d_type = " ".join(type_parts) if type_parts else "INTEGER"
                            
                            ref_t = parts[ref_idx + 1]
                            
                            if not any(a.name == fk_c for a in target_table.attributes):
                                target_table.add_attribute(Attribute(fk_c, d_type))
                            
                            target_table.add_foreign_key(fk_c, ref_t, "id")
                            self.model.add_relationship(Relationship(ref_t, t_name, "1N"))
                        else:
                            # Ajouter une colonne simple sans clé étrangère
                            idx = parts_upper.index("ADD") + 1
                            if parts_upper[idx] == "COLUMN": idx += 1
                            c_name, d_type = parts[idx], parts[idx+1]
                            target_table.add_attribute(Attribute(c_name, d_type))

                # cas 3: DROP TABLE 
                elif query_upper.startswith("DROP TABLE"):
                    t_name = parts[-1]
                    # Nettoyer toutes les relations associées à ce tableau
                    self.model.relationships = [r for r in self.model.relationships 
                                                if r.table1 != t_name and r.table2 != t_name and r.pivot_table_name != t_name]
                    self._remove_table_from_model(t_name)

            except Exception as e:
                print(f"Sync Error: {e}")

            # 2. mise à jour de l'affichage et du code SQL
            self.redraw()
            QMessageBox.information(self.view, "Succès", "Requête SQL exécutée avec succès.")
            self.view.console_input.clear()
        else:
            QMessageBox.critical(self.view, "Erreur SQL", message)

    def delete_table(self):
        curr = self.view.table_list.currentItem()
        if not curr:
            QMessageBox.warning(self.view, "Alerte", "selectionnez un tableau à supprimer.")
            return
        
        table_name = curr.text()
        confirm = QMessageBox.question(self.view, "Confirmer la suppression", 
                                     f"Êtes-vous sûr de vouloir supprimer définitivement le tableau '{table_name}' de la base de données ?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # 1. supprimer le tableau de la base de données
            success, msg = self.model.execute_sql(f"DROP TABLE IF EXISTS {table_name};")
            
            if success:
                # 2. Nettoyer toutes les relations associées à ce tableau
                self.model.relationships = [r for r in self.model.relationships 
                                           if r.table1 != table_name and r.table2 != table_name 
                                           and (not hasattr(r, 'pivot_table_name') or r.pivot_table_name != table_name)]
                
                # 3. Supprimer le tableau du modèle
                self._remove_table_from_model(table_name)
                
                # 4. mettre à jour le canvas et le code SQL
                self.redraw()
                self.view.sql_view.setPlainText(self.model.generate_sql())
                QMessageBox.information(self.view, "Succès", f"Le tableau '{table_name}' a été supprimé.")
            else:
                QMessageBox.critical(self.view, "Erreur", f"Échec de la suppression de la base de données: {msg}")


    def delete_relationship(self):
        selected_items = self.view.scene.selectedItems()
        if not selected_items: return

        to_remove = []
        for item in selected_items:
            for rel, line, label in self.relationship_lines:
                if item == line or item == label:
                    # 1. Nettoyer les modifications dans les tables impliquées
                    if rel.rel_type in ['1N', '11']:
                        # La relation stocke le tableau qui a reçu le FK dans fk_table_name
                        target_table_name = getattr(rel, 'fk_table_name', rel.table2)
                        target_table = self.model.get_table(target_table_name)
                        
                        if target_table:
                            # Supprimer la colonne de la liste des attributs pour qu'elle disparaisse du canvas
                            col_to_del = getattr(rel, 'fk_column_name', None)
                            if col_to_del:
                                target_table.attributes = [a for a in target_table.attributes if a.name != col_to_del]

                            # Supprimer le contrainte de clé étrangère pour qu'elle disparaisse du SQL Output
                            target_table.foreign_keys = [fk for fk in target_table.foreign_keys if fk[1] != rel.table1]

                    # 2. Si la relation est NN, on supprime le tableau pivot entièrement
                    elif rel.rel_type == 'NN' and hasattr(rel, 'pivot_table_name'):
                        p_name = rel.pivot_table_name
                        if p_name:
                            self.model.execute_sql(f"DROP TABLE IF EXISTS {p_name};")
                            self._remove_table_from_model(p_name)

                    to_remove.append(rel)
                    break
        
        # 3. Supprimer les relations du modèle
        for rel in to_remove:
            self.model.relationships = [r for r in self.model.relationships if r != rel]
        
        self.redraw()
        # mettre à jour le code SQL affiché immédiatement
        self.view.sql_view.setPlainText(self.model.generate_sql())

    def _remove_table_from_model(self, table_name):
        self.model.tables = [t for t in self.model.tables if t.name != table_name]
        for i in range(self.view.table_list.count()):
            if self.view.table_list.item(i) and self.view.table_list.item(i).text() == table_name:
                self.view.table_list.takeItem(i)
                break

    def modify_relationship(self):
        selected_items = self.view.scene.selectedItems()
        if not selected_items: return

        rel_to_mod = None
        for r, line, label in self.relationship_lines:
            if selected_items[0] == line or selected_items[0] == label:
                rel_to_mod = r
                break
        
        if not rel_to_mod: return

        names = [t.name for t in self.model.tables]
        d = RelationshipDialog(names)
        d.btn_ok.clicked.connect(d.accept) 

        d.src.setCurrentText(rel_to_mod.table1)
        d.dst.setCurrentText(rel_to_mod.table2)
        d.type_combo.setCurrentText(rel_to_mod.rel_type)

        if d.exec():
            # 1. Nettoyer l'état ancien complètement
            if hasattr(rel_to_mod, 'pivot_table_name') and rel_to_mod.pivot_table_name:
                self.model.execute_sql(f"DROP TABLE IF EXISTS {rel_to_mod.pivot_table_name};")
                self._remove_table_from_model(rel_to_mod.pivot_table_name)
            
            if hasattr(rel_to_mod, 'fk_table_name') and rel_to_mod.fk_table_name:
                target = self.model.get_table(rel_to_mod.fk_table_name)
                if target and hasattr(rel_to_mod, 'fk_column_name') and rel_to_mod.fk_column_name:
                    target.attributes = [a for a in target.attributes if a.name != rel_to_mod.fk_column_name]
                    target.foreign_keys = [fk for fk in target.foreign_keys if fk[0] != rel_to_mod.fk_column_name]

            # 2. mettre à jour les données de la relation et réinitialiser les références
            rel_to_mod.table1 = d.src.currentText()
            rel_to_mod.table2 = d.dst.currentText()
            rel_to_mod.rel_type = d.type_combo.currentText()
            rel_to_mod.fk_table_name = None
            rel_to_mod.fk_column_name = None
            rel_to_mod.pivot_table_name = None

            # 3. Appliquer les nouvelles modifications
            table1 = self.model.get_table(rel_to_mod.table1)
            table2 = self.model.get_table(rel_to_mod.table2)
            pk1 = table1.get_primary_key_name() if hasattr(table1, 'get_primary_key_name') else "id"
            pk2 = table2.get_primary_key_name() if hasattr(table2, 'get_primary_key_name') else "id"

            if rel_to_mod.rel_type in ['1N', '11']: 
                fk_name = f"{rel_to_mod.table1.lower()}_{pk1}"
                if not any(a.name == fk_name for a in table2.attributes):
                    table2.add_attribute(Attribute(fk_name, "INTEGER"))
                    table2.add_foreign_key(fk_name, rel_to_mod.table1, pk1)
                    
                    rel_to_mod.fk_table_name = rel_to_mod.table2
                    rel_to_mod.fk_column_name = fk_name
                    
                    self.model.execute_sql(f"ALTER TABLE {rel_to_mod.table2} ADD COLUMN {fk_name} INTEGER;")

            elif rel_to_mod.rel_type == 'NN':
                pivot_name = f"{rel_to_mod.table1}_{rel_to_mod.table2}"
                rel_to_mod.pivot_table_name = pivot_name
                if not self.model.get_table(pivot_name):
                    p_table = Table(pivot_name)
                    col1, col2 = f"{rel_to_mod.table1.lower()}_{pk1}", f"{rel_to_mod.table2.lower()}_{pk2}"
                    p_table.add_attribute(Attribute(col1, "INTEGER"))
                    p_table.add_attribute(Attribute(col2, "INTEGER"))
                    p_table.add_foreign_key(col1, rel_to_mod.table1, pk1)
                    p_table.add_foreign_key(col2, rel_to_mod.table2, pk2)
                    self.model.add_table(p_table)
                    self.view.table_list.addItem(pivot_name)
                    self.model.execute_sql(p_table.sql())

            self.redraw()
            QMessageBox.information(self.view, "Succés", "Modification et synchronisation terminées avec succès.")

    def update_relationships(self):
        # Nettoyer les anciennes lignes et étiquettes
        for _, line, label in self.relationship_lines:
            self.view.scene.removeItem(line)
            if label:
                self.view.scene.removeItem(label)
        self.relationship_lines = []

        for rel in self.model.relationships:
            if rel.rel_type == 'NN' and hasattr(rel, 'pivot_table_name') and rel.pivot_table_name:
                # les relations N:N passent par une table pivot
                self._draw_connection(rel.table1, rel.pivot_table_name, rel, "1:N")
                self._draw_connection(rel.table2, rel.pivot_table_name, rel, "1:N")
            else:
                # relations directes 1:N ou 1:1
                self._draw_connection(rel.table1, rel.table2, rel, rel.rel_type)

    def _draw_connection(self, t1_name, t2_name, rel, label_text):
        if t1_name in self.table_items and t2_name in self.table_items:
            item1 = self.table_items[t1_name]
            item2 = self.table_items[t2_name]
            
            # حساب مراكز الجداول لتوصيل الخطوط
            r1 = item1.sceneBoundingRect()
            r2 = item2.sceneBoundingRect()
            
            # créer la ligne de relation
            line = QGraphicsLineItem(r1.center().x(), r1.center().y(), r2.center().x(), r2.center().y())
            line.setFlag(QGraphicsItem.ItemIsSelectable, True)
            
            # Style the line based on relationship type
            pen = QPen()
            pen.setWidth(2)
            
            if rel.rel_type == '1N':
                pen.setColor(QColor(34, 139, 34))  # Forest green for 1:N
                pen.setStyle(Qt.PenStyle.SolidLine)
            elif rel.rel_type == '11':
                pen.setColor(QColor(0, 0, 205))  # Medium blue for 1:1
                pen.setStyle(Qt.PenStyle.DashLine)
            elif rel.rel_type == 'NN':
                pen.setColor(QColor(255, 69, 0))  # Red orange for N:N
                pen.setStyle(Qt.PenStyle.DotLine)
            
            line.setPen(pen)
            self.view.scene.addItem(line)
            
            # إضافة نص نوع العلاقة فوق الخط مع تحسين التصميم
            label = QGraphicsTextItem(label_text)
            label.setDefaultTextColor(pen.color())
            
            # Style the label
            font = label.font()
            font.setBold(True)
            font.setPointSize(8)
            label.setFont(font)
            
            # Position label slightly above the midpoint
            mid_x = (r1.center().x() + r2.center().x()) / 2
            mid_y = (r1.center().y() + r2.center().y()) / 2 - 10
            label.setPos(mid_x, mid_y)
            
            # Center the label text
            from PySide6.QtGui import QFontMetrics
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(label_text)
            label.setPos(mid_x - text_width/2, mid_y)
            
            self.view.scene.addItem(label)
            
            self.relationship_lines.append((rel, line, label))      

    