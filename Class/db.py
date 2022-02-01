import sqlite3
import os.path


class DB():
    """Work with databases"""

    def __init__(self):
        """Initsialition DB"""
        path = os.getcwd()
        db_path = os.path.join(path, "maindb.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()


    def condition(self, conditions, logic='AND'):
        """Generation substrings for WHERE"""

        if conditions is None:

            where = ""

        else:

            where = "WHERE "
            tempCondition = []

            for key in conditions:

                if isinstance(conditions[key], dict):
                    sep = conditions[key][1]
                    cond_val = conditions[key][0]
                else:
                    sep = ' = '
                    cond_val = conditions[key]

                if isinstance(conditions[key], str):
                    val = f"{sep}'{cond_val}'"
                else:
                    val = f"{sep}{cond_val}"

                tempCondition.append(f"{key}{val}")

            tempCondition = map(str, tempCondition)

            where += "("
            where += f' {logic} '.join(tempCondition)
            where += ")"

            # print(where)
            return where


    def columns(self,columns):

        cols = ''
        tempCols = []

        for key in columns:
            tempCols.append(key)

        tempCols = map(str, tempCols)

        cols += ','.join(tempCols)
        return cols


    def vals(self,columns):

        vals = ''
        tempVals = []

        for key in columns:

            if isinstance(key, str):
                val = f"'{key}'"
            else:
                val = key
            tempVals.append(f"{val}")

        tempVals = map(str, tempVals)

        vals += ','.join(tempVals)

        return vals


    def selectQuery(self, table, columns=None, conditions=None, orderBy=None, groupBy=None, logic='AND'):
        """Generation query by SELECT"""

        if columns is None:
            queryTable = '*'
        else:
            queryTable = self.columns(columns)

        where = self.condition(conditions=conditions, logic=logic)

        query = f"SELECT {queryTable} FROM {table} {where}"

        db = self.conn.execute(query)

        return db


    def fetchall(self, table, columns=None, conditions=None, orderBy=None, groupBy=None, closed=None, logic='AND'):

        db = self.selectQuery(table, columns, conditions, orderBy, groupBy, logic=logic)

        rows = db.fetchall()

        if closed is None:
            self.conn.close()

        return rows


    def fetchone(self, table, columns=None, conditions=None, orderBy=None, groupBy=None, closed=None, logic='AND'):

        db = self.selectQuery(table, columns, conditions, orderBy, groupBy, logic=logic)

        rows = db.fetchone()

        if closed is None:
            self.conn.close()

        return rows


    def deleteRow(self, table, conditions=None, closed=None):

        where = self.condition(conditions)

        query = f"DELETE FROM {table} {where}"

        self.conn.execute(query)

        self.conn.commit()

        if closed is None:
            self.conn.close()


    def insert(self, table, columns, values, closed=None):

        cols = self.columns(columns=columns)

        vals = self.vals(columns=values)

        conditions = {}

        for key in range(len(columns)):

            conditions[columns[key]] = values[key]

        isSet = self.fetchone(table=table, conditions=conditions,closed=False)

        if isSet is None:

            query = f"INSERT INTO {table} ({cols}) VALUES ({vals})"

            self.conn.execute(query)

            self.conn.commit()

        if closed is None:
            self.conn.close()


    def update(self, table, sets, conditions, closed=None):

        set = ""
        tempCondition = []

        for key in sets:

            if isinstance(sets[key], str):
                val = f"'{sets[key]}'"
            else:
                val = sets[key]

            tempCondition.append(f"{key}={val}")

        tempCondition = map(str, tempCondition)

        set += ','.join(tempCondition)

        where = self.condition(conditions)

        query = f"UPDATE {table} SET {set} {where}"

        self.conn.execute(query)

        self.conn.commit()

        if closed is None:
            self.conn.close()


    def getColumns(self, table):

        db = self.selectQuery(table)

        columns=[i[0] for i in db.description]

        return columns

# conditions = {}
# sets = {}
# conditions['user_id'] = {}
# conditions['user_id'][0] = 234234
# conditions['user_id'][1] = '>'
# conditions['user_name'] = 'Тест'

# newDB.deleteRow(table="users", conditions=conditions)
# sets['user_name'] = 'New Name'
# newDB.update(table='users',sets=sets, conditions=conditions)

# newDB = DB()
# newDB.insert(table='users',columns=['user_id','user_name','phone','edu'],values=[234234,'nddff','02','ffd'])

# newDB = DB()
# print(newDB.fetchall(table='users',conditions=conditions))