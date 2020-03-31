# -*- coding = UTF-8 -*-
import pymysql
import datetime
import jieba
import jieba.analyse
import os

# 转换元组数据为字典数据
def tupleToDic(tups):
    data = dict()
    for tup in tups:
        data[tup[0]] = tup[1]
    return data

# 提取文章关键字
def extractKeywords(data):
    keywords = jieba.analyse.extract_tags(data,topK=20,withWeight=True,allowPOS=())
    return keywords

# 获取时间作为ID
def creatLink(which):
    path = ''
    if which:
        path = "keywords/"
    else:
        path = "documents/"
    return path + datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + ".txt"

# 数据库实现类，包含对数据增删改查相关方法的实现
class DataBase:
    def __init__(self):
        connect = pymysql.connect('localhost', user = "root", passwd="123456", charset='utf8')
        cursor = connect.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS pythonDB')
        sql1 = """
                create table if not exists pythonDB.documents(
                id int(100),
                categpry varchar(20) character set utf8,
                title varchar(100) character set utf8,
                link varchar(200) character set utf8);
                """
        sql2 = """
                create table if not exists pythonDB.keywords(
                id int(100),
                keyword varchar(20) character set utf8,
                link varchar(200) character set utf8);
                """
        cursor.execute(sql1)
        cursor.execute(sql2)
        self.cursor = cursor
        self.connect = connect

   
    # 插入数据，自动识别是新增还是修改
    def insert(self, keyword, title, category, data):
        
        # 文章不存在数据库中，自动生成文章ID和保存路径
        if not self.isInDatabase(title, False):
            dataLink = 'documents/' + title + '.txt'
            id = len(self.searchall(False))
        # 文章存在数据库中，获取原ID和文件路径，即为修改操作
        else:
            res = self.search(title, False)
            dataLink = res[0][3]
            id = res[0][0]
            predata = self.getDataByLink(dataLink)
            keywords = extractKeywords(predata)
            # 在关键字十字链表中删除之前的关键词
            for item in keywords:
                self.deleteKeywords(item[0], id)
        fdata = open(dataLink, 'w+')
        fdata.write(data)
        print('documents table插入数据:%s %s %s %s'%(id, category, title, dataLink))
        self.cursor.execute("insert into pythonDB.documents values(%s, %s, %s, %s)",(id, category, title, dataLink))
        self.connect.commit()
        keywords = extractKeywords(data)
        flag = False
        # 将用户定义的关键字添加进关键字链表
        for i in range(len(keywords)):
            if keywords[i][0] == keyword:
                keywords[i][1] == 1
                flag = True
        if flag is False:
            added = (keyword,1)
            keywords.append(added)
        # 添加关键字到十字链表
        for item in keywords:
            # 关键字已存在十字链表中
            if self.isInDatabase(item[0], True):
                link = self.getLink(item[0], True)
                file = open(link,'w+')
                rep = ""
                for line in file.readlines():
                    # 根据该文章相关度插入关键字链表中
                    if int(line.split(':')[-1]) < item[1]:
                        rep = rep + "\n" + str(id) + ":" + str(item[1])
                    rep = rep + "\n" + line
                file.write(rep)
            else:
                link = 'keywords/' + item[0] + '.txt'
                key_id = len(self.searchall(True))
                file = open(link, 'w+')
                rep = str(id) + ":" + str(item[1])
                file.write(rep)
                self.cursor.execute("insert into pythonDB.keywords values(%s, %s, %s)",(key_id, item[0], link))
                self.connect.commit()
    # 迭代删除关键字
    def deleteKeywords(self,keyword,id):
        res = self.search(keyword, True)
        filelink = res[0][2]
        file = open(filelink,'r+')
        rewrite = ""
        for line in file.readlines():
            if line.split(":")[0] != str(id):
                rewrite = rewrite + line
        # 链表为空,从数据库中删除该项记录，并删除相对应的链表文件
        if rewrite == "":
            self.cursor.execute("delete from pythonDB.keywords where keyword = %s", keyword)
            self.connect.commit()
            os.remove(filelink)

    # 删除文章，并迭代删除文章相关关键词     
    def deleteArticle(self, title):
        res = self.search(title,False)
        txt = self.getDataByLink(res[0][3])
        keywords = extractKeywords(txt)
        self.cursor.execute("delete from pythonDB.documents where title=%s", res[0][2])
        self.connect.commit()
        for keyword in keywords:
            self.deleteKeywords(keyword[0], res[0][0])
        os.remove(res[0][3])
    
    # 根据关键词查询相关文章
    def searchByKeyword(self,keyword):
        """
        输入keyword
        若存在则返回相关的文章id,所属类别category，文章标题title,文章正文保存路径
        不纯在返回none
        """
        res = self.search(keyword, True)
        
        if res is not None:
            link = res[0][2]
            id = self.getIdByLink(link)
            categories = dict()
            titles = dict()
            links = dict()
            for k,v in id.items():
                self.cursor.execute("select * from pythonDB.documents where id = %s",k)
                data = self.cursor.fetchall()
                categories[k] = data[0][1]
                titles[k] = data[0][2]
                links[k] = data[0][3]
            return id, categories, titles, links
        else:
            return None
            
    # 查询单个数据
    def search(self, value, which):
        data = dict()
        value = str(value)
        if which:
            self.cursor.execute("select * from pythonDB.keywords where keyword=%s", value)
            data = self.cursor.fetchall()
        else:
            self.cursor.execute("select * from pythonDB.documents where title=%s", value)
            data = self.cursor.fetchall()
        return data

    # 全部展示
    def searchall(self, which):
        data = dict()
        if which:
            self.cursor.execute("select * from pythonDB.keywords")
        else:
            self.cursor.execute("select * from pythonDB.documents")
        data = self.cursor.fetchall()
        return data

    # which为True搜索keyword Table，False则是搜索documents Table
    def isInDatabase(self, value, which):
        if which == True:
            res = self.cursor.execute("select * from pythonDB.keywords where keyword=%s",value)
            if res is 0:
                return False
            else:
                return True
        else:
            res = self.cursor.execute("select * from pythonDB.documents where title=%s",value)
            if res is 0:
                return False
            else:
                return True
    
    # 获取保存文件名
    def getLink(self, value, which):
        if which:
            self.cursor.execute("select * from pythonDB.keywords where keyword=%s",value)
            res = self.cursor.fetchall()
            return res[0][2]
        else: 
            self.cursor.execute("select * from pythonDB.documents where title=%s",value)
            res = self.cursor.fetchall()
            return res[0][3]

    # 根据文章ID获取文章内容
    def getDataByLink(self, link):
        print(link)
        file = open(link,'r')
        data = ""
        for line in file.readlines():
            data = data + line.replace('\n','').replace('\r','')
        return data
    
    def getIdByLink(self,link):
        file = open(link)
        data = dict()
        for line in file.readlines():
            res = line.split(":")
            data[res[0]] = res[1]
        return data

    
   

def insertTest():
    data = """
    规模养猪是指生产单位或专业户综合运用场舍、农业、经营管理、畜牧兽医等科学技术，达到优质高产的经济养猪效果，提供大量物美价廉的商品猪肉。规模养猪经营规模扩大，专业化、集约化程度提高，猪群生长肥育迅速，出栏周转加快，增重耗料下降，栏舍利用率高。我国人口众多，劳动力资源丰富，但人均资源缺乏，规模养猪应重视经济效益，社会效益与生态效益。
    自80年代以来由于养猪相继发展，养猪规模越来越大，年产肉猪1万、2万，商品猪场迅速发展。假定一个年产肥猪1万头的养猪场，按每头出栏重100千克，屠宰率75%计算，则年产猪肉可达75万千克左右，平均每月可出栏肥猪800头以上。经营规模在一定时期和范围内，与自然、经济、技术、社会等因素有着密切联系。特别是饲料资源的多少，质量的好坏对经营规模有着相当重要的作用。
    规模养猪单位必须根据生产规模与远景任务，建设相应规模的饲料加工厂。假设一个年产肥猪1万头的养猪场，出栏头重100千克，每增重1千克需精料3千克，则每头肥猪共需精料300千克，总计300万千克。全场要饲养种母猪500头，每头年产2胎，成活仔猪20头，在人工授精条件下，公母比例按1：100计算，需养公猪5头，每头种猪每年约需消耗精料0.1万千克，全年共需51万千克。所以，全场共需精料350万千克左右。
    规模养猪生产中的科学管理，是合理组织生产、提高工效、多出产品、降低成本的中心纽带。科学管理首先要制定好年度生产计划，安排好各部门之间的分工负责，协调配合，制定工作定额与岗位责任制。要求做到品种标准化、日粮标准化、饲养科学化。每个生产环节，必须衔接协调。定期公布各组生产进度、完成任务、产值与成本等情况，以便人人心中有数。
    规模养猪是猪群高度密集的场所，必须十分重视卫生防疫制度。主要包括：彻底消毒制度（净化环境，防止病原入侵）；定期防疫制度（疫苗种类、防疫时间）；定期驱虫制度（驱虫药物、时间）；紧急防疫制度（隔离封锁、病原确诊、采取措施）等。贯彻“以防为主，综合防治”的方针，做到严格检疫、严格消毒、定期免疫。
            """
    data2 = """
            Life is like a box of chocolate, you never know what you gonna get.
            """
    keywords = extractKeywords(data)
    print(keywords)
    db = DataBase()
    db.insert('养猪','规模养猪简介','养殖技术',data)


# 测试数据库代码
def searchTest(keyword):
    db = DataBase()
    ids, categories, titles, links = db.searchByKeyword(keyword)
    for k,v in ids.items():
        print("%s %s %s %s"%(ids[k],categories[k],titles[k],links[k]))
        print(db.getDataByLink(links[k]))

def deleteTest(article):
    db = DataBase()
    db.deleteArticle(article)

if __name__ == '__main__':
    # searchTest('养猪场')
    # insertTest()
    deleteTest('规模养猪简介')
