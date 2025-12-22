import sqlite3

class Attribute:#column de attributs
    def __init__(self, name, dtype="TEXT", nullable=True, primary_key=False):
        self.name = name
        self.dtype = dtype
        self.nullable = nullable
        self.primary_key = primary_key

    def sql(self):#generer sql ta3na
        s = f"{self.name} {self.dtype}"
        if self.primary_key:
            s += " PRIMARY KEY"
        if not self.nullable:
            s += " NOT NULL"
        return s


class Table:
    def __init__(self, name):
        self.name = name
        self.attributes = []
        self.foreign_keys = []

    def add_attribute(self, attr):
        self.attributes.append(attr)

    def get_primary_key_name(self):
        for attr in self.attributes:
            if attr.primary_key:
                return attr.name
        return "id"    

    def add_foreign_key(self, col, ref_table, ref_col):
        self.foreign_keys.append((col, ref_table, ref_col))

    def sql(self):
        cols = [a.sql() for a in self.attributes]
        for col, rt, rc in self.foreign_keys:
            cols.append(f"FOREIGN KEY({col}) REFERENCES {rt}({rc})")
        return f"CREATE TABLE IF NOT EXISTS {self.name} (\n  " + ",\n  ".join(cols) + "\n);"


class Relationship:#
    def __init__(self, table1, table2, rel_type, pivot_table_name=None):
        self.table1 = table1
        self.table2 = table2
        self.rel_type = rel_type  # '1N', '11', 'NN'
        self.pivot_table_name = pivot_table_name
        self.fk_table = None
        self.fk_col = None
        
class Schema:
    def __init__(self):
        self.tables = []
        self.relationships = []

    def add_table(self, table):
        self.tables.append(table)

    def add_relationship(self, rel):
        self.relationships.append(rel)

    def get_table(self, name):
        for t in self.tables:
            if t.name == name:
                return t
        return None

    def generate_sql(self):
        sql = "\n\n".join(t.sql() for t in self.tables)
        # For NN, junction tables are already added as tables
        return sql
    
    def execute_sql(self, sql_text, db_name="schema.db"):
        try:
            con = sqlite3.connect(db_name)
            cur = con.cursor()
            cur.executescript(sql_text)
            con.commit()
            con.close()
            return True, "تم تنفيذ الاستعلام بنجاح (Success)"
        except sqlite3.Error as e:
            return False, f"خطأ في SQL: {str(e)}"