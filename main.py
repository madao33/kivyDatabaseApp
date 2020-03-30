from kivy.properties import BooleanProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.app import App
from kivy.lang import Builder
from datebase import DataBase
from kivy.factory import Factory
from kivy.properties import ObjectProperty
import kivy

Builder.load_string("""
<SelectableLabel>:
    font_name:'DroidSansFallback.ttf'
    canvas.before:
        Color:
            rgba: (0, 0.4, 0.6, 1) if self.selected else (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    color: (0, 0, 0, 1) if self.selected else (1, 1, 1, 1)

<MainView>:
    keyword: keyword
    data: data 
    rv:rv
    BoxLayout:
        orientation: 'vertical'
        ActionBar:
            ActionView:
                ActionPrevious:
                ActionButton:
                    text: '搜索'
                    font_name:'DroidSansFallback.ttf'
                    on_release: root.on_search()
                ActionButton:
                    text: '全部显示'
                    font_name:'DroidSansFallback.ttf'
                    on_release: root.on_showall()
                ActionButton:
                    text: '详细'
                    font_name:'DroidSansFallback.ttf'
                    on_release: root.on_modify()
                ActionButton:
                    text: '添加'
                    font_name:'DroidSansFallback.ttf'
                    on_release: root.on_adddata()
                ActionButton:
                    text: '删除选中'
                    font_name:'DroidSansFallback.ttf'
                    on_release: root.on_removedata()
        TextInput:
            id: keyword
            font_name:'DroidSansFallback.ttf'
            pos_hint: {"x":0.2, "top":0.8-0.13}
            size_hint: 0.6, 0.12
            multiline: False
            
            font_size: (root.width**2 + root.height**2) / 14**4
        TextInput:
            id: data
            font_name:'DroidSansFallback.ttf'
            pos_hint: {"x":0.2, "top":0.8}
            size_hint: 0.6, 0.4
            multiline: True
            font_size: (root.width**2 + root.height**2) / 14**4
        RecycleView:
            id: rv
            viewclass: 'SelectableLabel'
            font_name:'DroidSansFallback.ttf'
            SelectableRecycleBoxLayout:
                key_selection: 'selectable'  
                default_size: None, dp(56)
                default_size_hint: 1.0, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                font_name:'DroidSansFallback.ttf'
                multiselect: True
                touch_multiselect: True
""")

class SelectableRecycleBoxLayout(LayoutSelectionBehavior, RecycleBoxLayout):
    pass    

class SelectableLabel(RecycleDataViewBehavior, Label):
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
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if (self.index == index) and (index < len(rv.data)):
            rv.data[index]['selected'] = is_selected

def makedata(text, selectable=True, selected=False):
    return {'text': text, 'selectable': selectable, 'selected': selected}

def procData(res):
    data = []
    for k,v in res.items():
        data.append(makedata(k+"："+v))
    return data
    

class MainView(ModalView):
    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
    
    def on_search(self):
        keyword = self.keyword.text
        if keyword != "":
            res = db.search(keyword)
            data = procData(res)
            self.ids.rv.data = data

    def on_showall(self):
        res = db.searchall()
        print(res)
        if res != None:
            data = procData(res)
            self.ids.rv.data = data

    def on_modify(self):
        rv = self.ids.rv
        count=0
        data = ""
        for i,v in enumerate(rv.data):
            if v['selected']:
                count = count+1
                data = v['text']
        if count==1:
            self.keyword.text = data.split(':')[0]
            self.data.text = data.split(':')[-1]

    def on_adddata(self):
        if self.keyword.text != "" and self.data.text != "":
            db.insert(self.keyword.text, self.data.text)
        else:
            pass
        
    def on_removedata(self):
        rv = self.ids.rv
        lm = rv.layout_manager
        temp = []
        for i,v in enumerate(rv.data):
            if v['selected']:
                val = v['text'].split('：')
                db.delete(val[0])
            else:
                temp.append(v)
        rv.data = temp
        lm.clear_selection()

db = DataBase()

class MyApp(App):
    def build(self):
        return MainView()


if __name__ == '__main__':
    MyApp().run()