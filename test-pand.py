# -*- coding: utf-8 -*-
"""
@Time    : 2021/11/23 18:38
@Author  : summer
@File    : test-pand.py
@Software: PyCharm
"""
import random
import re
import string
import time
import json
from itertools import chain
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.commons.utils import JsCode


def checkABC(str):
    my_re = re.compile(r'[A-Za-z]', re.S)
    res = re.findall(my_re, str)
    if len(res):
        return True
    else:
        return False


def export_data_to_excel():
    # encoding编码方式，sheet_name表示要写到的sheet名称， 默认为0， header=None表示不含列名
    df.to_excel("./test.xlsx", encoding="utf_8_sig", sheet_name=0, header=None)


df = pd.read_table(r"D:\file\vdyu\summary.html", sep='\t', na_filter=False,
                   encoding='gbk', index_col=False, header=None, names=['All'])

print("开始处理数据" + time.strftime("%Y-%m-%d %H:%M:%S"))

for index, content in zip(df.index, df.values):
    if checkABC(str(content[0])):
        df.drop(index, inplace=True)
df["All"] = df["All"].str.split(expand=False)
df[['Time', 'Interval', 'rate1', 'resp1', 'total1', 'sys', 'pct', 'rate2', 'resp2', 'rate3', 'resp3', 'read', 'write',
    'total2',
    'size', 'rate4', 'resp4', 'rate5', 'resp5', 'rate6', 'resp6', 'rate7', 'resp7', 'rate8', 'resp8', 'rate9',
    'resp9']] = pd.DataFrame(list(chain(df.All.values)), index=df.index)
df.drop('All', axis=1, inplace=True)
# print("删除前810行")
# df.drop(df.index[0:810], inplace=True)
# df[['total2']] = df[['total2']].apply(pd.to_numeric)
print("处理数据结束" + time.strftime("%Y-%m-%d %H:%M:%S"))
# 重命名
# df.rename(columns={'total2':'value','Time':'text'},inplace=True)
# a = df[['value','text']].to_dict('records')
# print(a)
print('###########################')
print("导出数据到excl" + time.strftime("%Y-%m-%d %H:%M:%S"))
excel_file_name = time.strftime('%Y-%m-%d_%H-%S-%M', time.localtime(time.time())) + ''.join(
    random.sample(string.digits, 6)) + '.xlsx'
df.to_excel(excel_file_name, sheet_name='Sheet1')
print("导出数据完成" + time.strftime("%Y-%m-%d %H:%M:%S"))
print('###########################')


print("生成html文件" + time.strftime("%Y-%m-%d %H:%M:%S"))
html_file_name = time.strftime('%Y-%m-%d_%H-%S-%M', time.localtime(time.time())) + ''.join(
    random.sample(string.digits, 6)) + '.html'


(
    Line(init_opts=opts.InitOpts(width="1800px", height="800px",page_title='vdbench可视化'))
        .add_xaxis(xaxis_data=list(chain(df["Interval"])))
        # 在顶部添加x轴
        .extend_axis(xaxis_data=list(chain(df["Time"])),
                     xaxis=opts.AxisOpts(position='top',
                                         # axistick_opts=opts.AxisTickOpts(is_align_with_label=True),  # 设置标签位置
                                         # axisline_opts=opts.AxisLineOpts(is_on_zero=False,
                                         #                                 linestyle_opts=opts.LineStyleOpts(
                                         #                                     color="#6e9ef1"))
                                         ))
        .add_yaxis(
        series_name="带宽",
        # is_connect_nones=True,
        is_smooth=True,
        y_axis=list(chain(df["total2"])),
        # y_axis=a,
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
            ]
        ),
        markline_opts=opts.MarkLineOpts(
            data=[opts.MarkLineItem(type_="average", name="平均值"),
                  opts.MarkLineItem(y=250, name="标记线")]
        ),
        )
        .set_global_opts(
        title_opts=opts.TitleOpts(title="vdbench创建文件速度测试结果",
                                  pos_top='30px',
                                  pos_left='left',
                                  subtitle=time.strftime("%Y-%m-%d %H:%M:%S")),
        tooltip_opts=opts.TooltipOpts(is_show=True,
                                      trigger='axis',
                                      axis_pointer_type="cross"),
        # tooltip_opts=opts.TooltipOpts(formatter=JsCode(
        #         """function(params){
        #             return '时间:'+params.data[text]+'<br/>'+'带宽:'+params.data[value]
        #         }
        #         """)
        # ),
        toolbox_opts=opts.ToolboxOpts(is_show=True,
                                      feature={"saveAsImage": {},
                                               "dataZoom": {"yAxisIndex": "none"},
                                               "restore": {},
                                               "magicType": {"show": True, "type": ["line", "bar"]},
                                               "dataView": {}}),
        xaxis_opts=opts.AxisOpts(type_="category",
                                 boundary_gap=False),
        datazoom_opts=opts.DataZoomOpts(is_show=True,
                                        orient='horizontal',
                                        xaxis_index=[0, 1]),
        visualmap_opts=opts.VisualMapOpts(type_='color',
                                          min_=0,
                                          max_=350,
                                          pos_right=0,
                                          pos_bottom=100,
                                          ), )

        #     visualmap_opts=opts.VisualMapOpts(
        #         is_piecewise=True,
        #         dimension=0,
        #         pieces=[
        #             {"lte": 270, "color": "green"},
        #             {"gt": 270, "lte": 280, "color": "red"},
        #             {"gt": 280, "lte": 290, "color": "yellow"},
        #             {"gt": 290, "lte": 300, "color": "red"},
        #             {"gt": 300, "color": "green"},
        #         ],
        #         pos_right=0,
        #         pos_bottom=100
        #     ),
        # )
        .render(html_file_name)
)
