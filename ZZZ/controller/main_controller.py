from cmath import rect
from turtle import title
from model.schema import Table, Attribute, Relationship
from view.table_dialog import TableDialog
from view.attribute_dialog import AttributeDialog
from view.relationship_dialog import RelationshipDialog
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QMessageBox
from view.table_item import TableItem


class MainController:

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.y = 0
        self.table_items = {}
        self._connect()
        self.relationship_lines = []  # list of (rel, line, label)


    def _connect(self):
        self.view.btn_new_table.clicked.connect(self.open_table_dialog)
        self.view.table_list.itemDoubleClicked.connect(self.add_attribute)
        self.view.btn_add_rel.clicked.connect(self.add_relationship)
        self.view.btn_mod_rel.clicked.connect(self.modify_relationship)
        self.view.btn_del_rel.clicked.connect(self.delete_relationship)
        self.view.btn_delete.clicked.connect(self.delete_table)
        self.view.btn_run_console.clicked.connect(self.run_manual_sql)

    def open_table_dialog(self):
        d = TableDialog()
        d.btn_ok.clicked.connect(lambda: self.create_table(d))
        d.exec()

    def create_table(self, d):
        name = d.input.text().strip()
        if name:
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
        
        self.redraw() # هي التي ستنادي دالة الرسم
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
        
        # رسم الجداول أولاً لكي تتوفر إحداثياتها للخطوط
        for t in self.model.tables:
            self.draw_table(t)

        # رسم العلاقات باستخدام المنطق الجديد
        self.update_relationships()

        self.view.sql_view.setPlainText(self.model.generate_sql())

    def draw_table(self, table):# draw in canvas
        height = 30 + 15 * len(table.attributes)
        x_pos = 0

        rect = TableItem(
            x_pos,
            self.y,
            180,
            height,
            controller=self,
            name=table.name
        )
        
        rect.setZValue(0)
        self.view.scene.addItem(rect)
        self.table_items[table.name] = rect

        rect.text_items = []

        title = QGraphicsTextItem(table.name)
        title.setPos(x_pos+ 5, self.y)
        title.setZValue(1)
        self.view.scene.addItem(title)
        rect.text_items.append(title)

        y_text = self.y + 20
        for attr in table.attributes:
            display_name = attr.name
            if attr.primary_key:
                display_name += " (PK) "

            txt = QGraphicsTextItem(attr.name)
            txt.setPos(x_pos + 10, y_text)
            txt.setZValue(1)

            if attr.primary_key:
                font = txt.font()
                font.setBold(True)
                txt.setFont(font)

            self.view.scene.addItem(txt) 
            rect.text_items.append(txt)
            y_text += 15


        self.y += height + 20 # table ta7t khatha
        print("ATTRIBUTES:", [a.name for a in table.attributes])

    def run_manual_sql(self):
        query = self.view.console_input.toPlainText().strip()
        if not query: return

        # 1. تنفيذ في قاعدة البيانات الحقيقية
        success, message = self.model.execute_sql(query)

        if success:
            query_upper = query.upper()
            from model.schema import Table, Attribute, Relationship

            try:
                # تنظيف النص لاستخراج الكلمات بدقة
                clean_query = query.replace('(', ' ( ').replace(')', ' ) ').replace(',', ' , ').replace(';', '')
                parts = clean_query.split()
                parts_upper = [p.upper() for p in parts]

                # --- الحالة 1: CREATE TABLE (دعم الأنواع المخصصة و NN التلقائي) ---
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

                # --- الحالة 2: ALTER TABLE (إضافة عمود أو علاقة بنوع بيانات مخصص) ---
                elif "ALTER TABLE" in query_upper and "ADD" in query_upper:
                    t_name = parts[2]
                    target_table = self.model.get_table(t_name)
                    if target_table:
                        if "REFERENCES" in parts_upper:
                            ref_idx = parts_upper.index("REFERENCES")
                            start_idx = parts_upper.index("ADD") + 1
                            if parts_upper[start_idx] == "COLUMN": start_idx += 1
                            
                            fk_c = parts[start_idx] # اسم العمود
                            # التقاط النوع بين اسم العمود وكلمة REFERENCES
                            type_parts = parts[start_idx + 1 : ref_idx]
                            d_type = " ".join(type_parts) if type_parts else "INTEGER"
                            
                            ref_t = parts[ref_idx + 1]
                            
                            # إضافة العمود والـ FK للموديل (للمزامنة مع الرسم و SQL Output)
                            if not any(a.name == fk_c for a in target_table.attributes):
                                target_table.add_attribute(Attribute(fk_c, d_type))
                            
                            target_table.add_foreign_key(fk_c, ref_t, "id")
                            self.model.add_relationship(Relationship(ref_t, t_name, "1N"))
                        else:
                            # إضافة عمود عادي
                            idx = parts_upper.index("ADD") + 1
                            if parts_upper[idx] == "COLUMN": idx += 1
                            c_name, d_type = parts[idx], parts[idx+1]
                            target_table.add_attribute(Attribute(c_name, d_type))

                # --- الحالة 3: DROP TABLE (الحذف من الكونسول) ---
                elif query_upper.startswith("DROP TABLE"):
                    t_name = parts[-1]
                    # مسح العلاقات المرتبطة بالجدول المحذوف أولاً
                    self.model.relationships = [r for r in self.model.relationships 
                                                if r.table1 != t_name and r.table2 != t_name and r.pivot_table_name != t_name]
                    self._remove_table_from_model(t_name)

            except Exception as e:
                print(f"Sync Error: {e}")

            # 2. التحديث الإجباري لكل شيء (Canvas + SQL Output)
            self.redraw()
            QMessageBox.information(self.view, "نجاح", "تم تنفيذ الأمر وتحديث الرسم والكود")
            self.view.console_input.clear()
        else:
            QMessageBox.critical(self.view, "خطأ SQL", message)

    def delete_table(self):
        curr = self.view.table_list.currentItem()
        if not curr:
            QMessageBox.warning(self.view, "تنبيه", "يرجى اختيار جدول لحذفه")
            return
        
        table_name = curr.text()
        confirm = QMessageBox.question(self.view, "تأكيد الحذف", 
                                     f"هل أنت متأكد من حذف الجدول '{table_name}' نهائياً من قاعدة البيانات؟",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # 1. حذفه من قاعدة البيانات الفعلية (SQLite)
            success, msg = self.model.execute_sql(f"DROP TABLE IF EXISTS {table_name};")
            
            if success:
                # 2. حذف كل العلاقات المرتبطة بهذا الجدول من الموديل لكي لا يحدث خطأ في الرسم
                self.model.relationships = [r for r in self.model.relationships 
                                           if r.table1 != table_name and r.table2 != table_name 
                                           and (not hasattr(r, 'pivot_table_name') or r.pivot_table_name != table_name)]
                
                # 3. حذفه من الموديل (Schema) ومن القائمة الجانبية
                self._remove_table_from_model(table_name)
                
                # 4. تحديث الكانفا والـ SQL Output
                self.redraw()
                self.view.sql_view.setPlainText(self.model.generate_sql())
                QMessageBox.information(self.view, "نجاح", f"تم حذف الجدول '{table_name}' كلياً")
            else:
                QMessageBox.critical(self.view, "خطأ", f"فشل الحذف من قاعدة البيانات: {msg}")


    def delete_relationship(self):
        selected_items = self.view.scene.selectedItems()
        if not selected_items: return

        to_remove = []
        for item in selected_items:
            for rel, line, label in self.relationship_lines:
                if item == line or item == label:
                    # 1. تنظيف الجداول من بيانات العلاقة (FK)
                    if rel.rel_type in ['1N', '11']:
                        # العلاقة تخزن الجدول الذي استقبل الـ FK في fk_table_name
                        target_table_name = getattr(rel, 'fk_table_name', rel.table2)
                        target_table = self.model.get_table(target_table_name)
                        
                        if target_table:
                            # حذف العمود من قائمة الخصائص ليختفي من المربع في الرسم
                            col_to_del = getattr(rel, 'fk_column_name', None)
                            if col_to_del:
                                target_table.attributes = [a for a in target_table.attributes if a.name != col_to_del]
                            
                            # حذف قيد المفتاح الأجنبي ليختفي من الـ SQL Output
                            target_table.foreign_keys = [fk for fk in target_table.foreign_keys if fk[1] != rel.table1]

                    # 2. إذا كانت علاقة NN، نحذف الجدول الوسيط كلياً
                    elif rel.rel_type == 'NN' and hasattr(rel, 'pivot_table_name'):
                        p_name = rel.pivot_table_name
                        if p_name:
                            self.model.execute_sql(f"DROP TABLE IF EXISTS {p_name};")
                            self._remove_table_from_model(p_name)

                    to_remove.append(rel)
                    break
        
        # 3. حذف العلاقة من قائمة العلاقات وتحديث الواجهة
        for rel in to_remove:
            self.model.relationships = [r for r in self.model.relationships if r != rel]
        
        self.redraw()
        # تحديث كود SQL المعروض فوراً
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
            # 1. تنظيف الحالة القديمة تماماً
            if hasattr(rel_to_mod, 'pivot_table_name') and rel_to_mod.pivot_table_name:
                self.model.execute_sql(f"DROP TABLE IF EXISTS {rel_to_mod.pivot_table_name};")
                self._remove_table_from_model(rel_to_mod.pivot_table_name)
            
            if hasattr(rel_to_mod, 'fk_table_name') and rel_to_mod.fk_table_name:
                target = self.model.get_table(rel_to_mod.fk_table_name)
                if target and hasattr(rel_to_mod, 'fk_column_name') and rel_to_mod.fk_column_name:
                    target.attributes = [a for a in target.attributes if a.name != rel_to_mod.fk_column_name]
                    target.foreign_keys = [fk for fk in target.foreign_keys if fk[0] != rel_to_mod.fk_column_name]

            # 2. تحديث بيانات العلاقة وتصفير المراجع
            rel_to_mod.table1 = d.src.currentText()
            rel_to_mod.table2 = d.dst.currentText()
            rel_to_mod.rel_type = d.type_combo.currentText()
            rel_to_mod.fk_table_name = None
            rel_to_mod.fk_column_name = None
            rel_to_mod.pivot_table_name = None

            # 3. بناء المنطق الجديد
            table1 = self.model.get_table(rel_to_mod.table1)
            table2 = self.model.get_table(rel_to_mod.table2)
            pk1 = table1.get_primary_key_name() if hasattr(table1, 'get_primary_key_name') else "id"
            pk2 = table2.get_primary_key_name() if hasattr(table2, 'get_primary_key_name') else "id"

            if rel_to_mod.rel_type in ['1N', '11']:
                fk_name = f"{rel_to_mod.table1.lower()}_{pk1}"
                if not any(a.name == fk_name for a in table2.attributes):
                    table2.add_attribute(Attribute(fk_name, "INTEGER"))
                    table2.add_foreign_key(fk_name, rel_to_mod.table1, pk1)
                    
                    # --- التعديل الجوهري هنا ---
                    # نخزن اسم الجدول والعمود في العلاقة لكي تعرف دالة الحذف ماذا تمسح لاحقاً
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
            QMessageBox.information(self.view, "نجاح", "تم التعديل والمزامنة بنجاح")

    def update_relationships(self):
        # حذف الخطوط القديمة من الكانفا
        for _, line, label in self.relationship_lines:
            self.view.scene.removeItem(line)
            if label:
                self.view.scene.removeItem(label)
        self.relationship_lines = []

        for rel in self.model.relationships:
            if rel.rel_type == 'NN' and hasattr(rel, 'pivot_table_name') and rel.pivot_table_name:
                # في حالة NN، نرسم خطين يربطان الجداول الأصلية بالجدول الوسيط (Pivot)
                self._draw_connection(rel.table1, rel.pivot_table_name, rel, "1:N")
                self._draw_connection(rel.table2, rel.pivot_table_name, rel, "1:N")
            else:
                # الرسم العادي لعلاقات 1:N و 1:1
                self._draw_connection(rel.table1, rel.table2, rel, rel.rel_type)

    def _draw_connection(self, t1_name, t2_name, rel, label_text):
        if t1_name in self.table_items and t2_name in self.table_items:
            item1 = self.table_items[t1_name]
            item2 = self.table_items[t2_name]
            
            # حساب مراكز الجداول لتوصيل الخطوط
            r1 = item1.sceneBoundingRect()
            r2 = item2.sceneBoundingRect()
            
            line = QGraphicsLineItem(r1.center().x(), r1.center().y(), r2.center().x(), r2.center().y())
            line.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.view.scene.addItem(line)
            
            # إضافة نص نوع العلاقة فوق الخط
            label = QGraphicsTextItem(label_text)
            label.setPos((r1.center().x() + r2.center().x()) / 2, (r1.center().y() + r2.center().y()) / 2)
            self.view.scene.addItem(label)
            
            self.relationship_lines.append((rel, line, label))      
            