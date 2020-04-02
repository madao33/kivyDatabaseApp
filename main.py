from kivy.uix.textinput import TextInput
from datebase import DataBase
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty, ObjectProperty

class WindowManager(ScreenManager):
    pass

def popupWindow(title, text):
    pop = Popup(title=title,content=Label(text=text),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

# 传递全局变量类
class Val(App):
    title=""
    keyword = ""
    category=""
    article = ""
    id=""
    former = ""
    datalist = []

    def clear(self):
        self.title = ""
        self.keyword = ""
        self.category = ""
        self.article = ""
        self.id = ""

class SelectableRecycleBoxLayout(LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' 为标签添加选中与否的支持 '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
            
        if self.collide_point(*touch.pos) and self.selectable:
            print("点击文本:", self._label._text)
            text = self._label._text
            if sm.current == "list":
                keyword = text
                # 存在'->'为文章标题，根据文章获取,并进入详情页
                res = keyword.split("->")
                data = db.getArticleById(res[0])
                print("选中文章：",data)
                if len(data) != 1:
                    popupWindow("sqlError", "no exists this article!")
                else:
                    data=data[0]
                    val.id=data[0]
                    val.category = data[1]
                    val.title = data[2]
                    val.article = db.getDataByLink(data[3])
                    val.former = "list"
                    
                    sm.current = "detail"  

            elif sm.current == "main":
                res = text
                print("选中分类:"+res)
                docs = db.searchByCategory(res)
                val.datalist = []
                for doc in docs:
                    val.datalist.append(makedata(str(doc[0])+"->"+doc[2]))
                val.former="category"
                
                sm.current = "list"

            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        # !important! : index validation
        # if you remove raw data entry, The value of index arg be less than the value of self.index.
        # Or the value of index arg indicates out of bounds of 'data' array.
        # note: after leave this function, refresh_view_attrs() are called. so you should be re-assign self.index.
        if (self.index == index) and (index < len(rv.data)):
            rv.data[index]['selected'] = is_selected

            # 选中某条
            

            
            
            

def makedata(text, selectable=True, selected=False):
    return {'text': text, 'selectable': selectable, 'selected': selected}

def resetData(rv):
    for r in rv:
        r['selected'] = False
class MainView(Screen):
    
    # 初始化界面
    def on_enter(self):
        res = db.searchall(False)
        print(res)
        category = []
        data=[]
        for i in range(len(res)):
            # print(res[i][1])
            if res[i][1] not in category:
                category.append(res[i][1])
                data.append(makedata(res[i][1]))
        self.ids.rv.data = data
        print("category: ",data)
        print('进入主界面')


    def searchBtn(self):
        val.former = "keyword"
        sm.current = "list"
        

    def appendBtn(self):
        val.former = "append"
        val.clear()
        sm.current = "detail"


class ListView(Screen):

    keyword = ObjectProperty(None)
    def on_enter(self):
        if val.former == "category":
            print("传入列表:",val.datalist)
            print("原列表:",self.rv.data)
            self.rv.data = val.datalist
        elif val.former == "detail":
            pass

    def searchBtn(self):
        if self.keyword.text != "":
            print("搜索关键词:"+self.keyword.text)
            ids, categories, titles, links = db.searchByKeyword(self.keyword.text)
            data = []
            for k,v in ids.items():
                print("%s %s %s %s"%(ids[k],categories[k],titles[k],links[k]))
                print(db.getDataByLink(links[k]))
                data.append(makedata(k+"->"+titles[k]))
            self.rv.data = data
        else:
            popupWindow("No keywords", "Please input keywords to search!")

    def backBtn(self):
        val.former = "detail"
        sm.current = "main"

class DetailView(Screen):

    keyword = ObjectProperty(None)
    title = ObjectProperty(None)
    article = ObjectProperty(None)
    category = ObjectProperty(None)

    def on_enter(self):
        if val.former=="list":
            self.title.text = val.title
            self.keyword.text = val.keyword
            self.article.text = val.article
            self.category.text = val.category
            print(val.category)

        elif val.former=="append":
            self.title.text = ""
            self.keyword.text = ""
            self.article.text = ""
            self.category.text = ""
    def backBtn(self):
        val.former = "detail"
        val.clear()
        sm.current = "list"
    
    def deleteBtn(self):

        if val.former == "list":
            db.deleteArticle(val.title)
        else:
            popupWindow("Nothing to delete", "There is no existing record to delete!")
        val.former = "detail"
        val.clear()
        sm.current = "main"

    def saveBtn(self):
        keyword = self.keyword.text
        category = self.category.text
        article = self.article.text
        title = self.title.text
        if keyword != "" and category != "" and article != "" and title != "":
            db.insert(keyword,title,category,article)
            print("成功插入数据记录：%s %s %s \n%s"%(title, category, keyword, article))
            val.clear()
            sm.current = "main"
        else:
            popupWindow("No enough arguments!", "Please finish all the arguments to complish record this article!")
        

kv = Builder.load_file("my.kv")
# 利用screenmanager实现界面切换
sm = WindowManager()
db = DataBase()
val = Val()
screens = [MainView(name="main"),ListView(name="list"),DetailView(name="detail")]
for screen in screens:
    sm.add_widget(screen)
sm.current = "main"

class MyMainApp(App):
    def build(self):
        return sm

if __name__ == '__main__':
    MyMainApp().run()