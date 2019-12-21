import pandas as pd
import numpy as np
import json

''' 
关于pandas的学习
来源: https://github.com/BrambleXu/pydata-notebook
      -->https://nbviewer.jupyter.org/github/LearnXu/pydata-notebook/blob/master/Chapter-14/14.4%20USDA%20Food%20Database%EF%BC%88USDA%E9%A3%9F%E5%93%81%E6%95%B0%E6%8D%AE%E5%BA%93%EF%BC%89.ipynb
使用的数据集：datasets--> usda_food --> json
''' 

'''
这个数据是关于食物营养成分的。存储格式是JSON，看起来像这样：

{
    "id": 21441, 
    "description": "KENTUCKY FRIED CHICKEN, Fried Chicken, EXTRA CRISPY, Wing, meat and skin with breading", 
    "tags": ["KFC"], 
    "manufacturer": "Kentucky Fried Chicken", 
    "group": "Fast Foods", 
    "portions": [ 
        { "amount": 1, 
          "unit": "wing, with skin", 
          "grams": 68.0
        }
        ...
      ],
    "nutrients": [ 
      { "value": 20.8, 
        "units": "g", 
        "description": "Protein", 
        "group": "Composition" 
      },
      ...
     ]
}
manufacturer 制造商
portions 部分
grams 克
amount 营养物
nutrients 营养
每种食物都有一系列特征，其中有两个list，protions和nutrients。我们必须把这样的数据进行处理，方便之后的分析
'''

pd.options.display.max_rows = 10

db = json.load(open('/home/ubuntu/work/venv/pydata-notebook/datasets/usda_food/database.json')) # db is list

print(db[0].keys()) # db[0] is dict
print(db[0]['nutrients'][0])

nutrients = pd.DataFrame(db[0]['nutrients'])

info_keys = ['description', 'group', 'id', 'manufacturer']

info = pd.DataFrame(db, columns=info_keys)

print(info[:5])
print(info.info())

# 查看食物群的分布 使用value_counts
print(pd.value_counts(info.group)[:10]) # =info['fgroup'].value_counts(normalize=True)[:10]
# value_counts()函数可以对Series里面的每个值进行计数并且排序 回的结果是一个Series数组，可以跟别的数组进行运算
# 默认从最高到最低降序 加入参数ascending=True升序 加参数normalize=True得出计数占比

# 对nutrient的数据进行一些分析
nutrients_all = pd.DataFrame()

for food in db:
    nutrients = pd.DataFrame(food['nutrients'])
    nutrients['id'] = food['id']
    nutrients_all = nutrients_all.append(nutrients, ignore_index=True)

print(nutrients_all)

# 查看重复的行
print(nutrients_all.duplicated().sum())

# 去除重复的部分
nutrients_all = nutrients_all.drop_duplicates()
print(nutrients_all)

# 更改列名
col_mapping = {"description":"food", "group":"fgroup"}
info = info.rename(columns=col_mapping, copy=False)
print(info.info())

col_mapping = {"description":"nutrient", "group":"nutgroup"}
nutrients_all = nutrients_all.rename(columns=col_mapping, copy=False)
print(nutrients_all)

# 合并info和nutrients_all
ndata = pd.merge(nutrients_all, info, on='id', how='outer')
print(ndata.info())
print(ndata.iloc[30000])  # 优化过的 Pandas 数据访问方法：.at、.iat、.loc 和 .iloc

# 对食物群（food group）和营养类型（nutrient type）分组后，对中位数进行绘图
result = ndata.groupby(['nutrient', 'fgroup'])['value'].quantile(0.5)
%matplotlib inline # “%matplotlib inline”就是模仿命令行来访问magic函数的在IPython中独有的形式
'''
问题：ModuleNotFoundError: No module named 'ipykernel'
解决：https://stackoverflow.com/questions/28831854/how-do-i-add-python3-kernel-to-jupyter-ipython

衍生问题：No event loop integration for 'inline'. Supported event loops are: qt, qt4, qt5, gtk, gtk2, gtk3, tk, wx, pyglet, glut, osx
解决：这个是ipython不支持图形化，所以可以使用ipython notebook，即jupyter 安装使用jupyter
'''
# 绘图
result['Zinc', 'Zn'].sort_values().plot(kind='barh', figsize=(10, 8))

# 查找每一种营养成分含量最多的食物是什么
by_nutrient = ndata.groupby(['nutgroup', 'nutrient'])
get_maximum = lambda x: x.loc[x.value.idxmax()]
get_minimum = lambda x: x.loc[x.value.idxmin()]

max_foods = by_nutrient.apply(get_maximum)[['value', 'food']]

max_foods.food = max_foods.food.str[:50]
max_foods.loc['Amino Acids']['food']


