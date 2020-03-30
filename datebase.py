# -*- coding = UTF-8 -*-
import pymysql
import datetime

# 转换元组数据为字典数据
def tupleToDic(tups):
    data = dict()
    for tup in tups:
        data[tup[0]] = tup[1]
    return data

class DataBase:
    def __init__(self):
        connect = pymysql.connect('localhost', user = "root", passwd="123456", charset='utf8')
        cursor = connect.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS pythonDB')
        sql = """
                create table if not exists pythonDB.documents(
                keyword varchar(20),
                data varchar(1000))character set=utf8;
                """
        cursor.execute(sql)
        self.cursor = cursor
        self.connect = connect

    # 插入数据
    def insert(self, keyword, data):
        self.cursor.execute("insert into pythonDB.documents values(%s, %s)",(keyword, data))
        self.connect.commit()

    # 删除数据
    def delete(self, keyword):
        self.cursor.execute("delete from pythonDB.documents where keyword = %s",keyword)
        self.connect.commit()
    
    # 根据全文删除
    def deleteByData(self,data):
        self.cursor.execute("delete from pythonDB.documents where data = %s",data)
        self.connect.commit()
    
    # 修改数据
    def change(self, keyword1, keyword2, data):
        self.cursor.execute("update pythonDB.documents set keyword = %s where keyword = %s",(keyword2,keyword1))
        self.cursor.execute("update pythonDB.documents set data = %s where keyword = %s",(data, keyword1))
        self.connect.commit()
    
    # 查询数据
    def search(self, keyword):
        data = dict()
        keyword = str(keyword)
        self.cursor.execute("select * from pythonDB.documents where keyword=%s", keyword)
        data = self.cursor.fetchall()
        data = tupleToDic(data)
        return data

    # 全部展示
    def searchall(self):
        data = dict()
        self.cursor.execute("select * from pythonDB.documents")
        data = self.cursor.fetchall()
        data = tupleToDic(data)
        return data

db = DataBase()
keyword = "test"
data = "hello, kivy"
print(keyword, data)
db.insert(keyword, data)