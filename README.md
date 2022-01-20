


思路：本文讲解两种方式，其一是拿到vdbench的数据结果，使用工具或者python，将数据json序列化；然后写一个html页面，使用Ajax，拿到json文件并通过echarts展示之；其二是使用pyecharts和pandas
<!-- more -->

# 思路一
## vdbench数据处理

- 一般vdbench的数据都长这样：

![](https://cdn.jsdelivr.net/gh/summerking1/image@main/2021-7-6-1.png)  

- 数据先预处理一波，我使用的是shell语句预处理


```
cat run.log  | grep "[00-59]:[00-59]" | grep -v "[a-zA-Z]\|*"  | awk  '{print $1,$2,$3}' > newrun.log
```
### 方式一
- 转json工具是[text-2-json](https://github.com/danwild/text2json)
- 首行手动加入 time keep speed 最后长这样：

![](https://cdn.jsdelivr.net/gh/summerking1/image@main/2021-7-6-2.png)  

- 使用
`node .\index.js --i=./Input/test.txt --o=./Input/txt.json -h`

### 方式二

- python处理
```python
# coding=utf-8
import re
import json
import os


def txtToJson():
    # 文件路径
    path = "./Input/test.txt"
    # 读取文件
    with open(path, 'r', encoding="utf-8") as file:
        # 定义一个用于切割字符串的正则
        seq = re.compile("\s+")
        result = []
        # 逐行读取
        for line in file:
            lst = seq.split(line.strip())
            item = {
                "time": lst[0],
                "keep": lst[1],
                "speed": lst[2],
            }
            result.append(item)

        print(type(result))
    # 关闭文件
    with open('./Output/txtToJson.json', 'w') as dump_f:
        json.dump(result, dump_f)


if __name__ == '__main__':

    if os.path.exists("./Output/txtToJson.json"):
        os.remove("./Output/txtToJson.json")
        txtToJson()
    else:
        print("The file does not exist")
        txtToJson()
```

## 处理后的json
- 不管是使用方式一还是二，最终的效果如下：
```json
[
    {
        "time": "19:11:42",
        "keep": "1",
        "speed": "19712"
    },
    {
        "time": "19:11:43",
        "keep": "2",
        "speed": "8478.0"
    },
    {
        "time": "19:11:44",
        "keep": "3",
        "speed": "3978.0"
    },
    {
        "time": "19:11:45",
        "keep": "4",
        "speed": "3568.0"
    },
    {
        "time": "19:11:46",
        "keep": "5",
        "speed": "1982.0"
    }
]
```

## 前端echarts代码

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Vdbench结果展示图</title>
    <style type="text/css">
        #main {
            height: 600px;
            width: 1300px;
        }
    </style>
    <script src="https://cdn.staticfile.org/jquery/2.1.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.1.2/dist/echarts.min.js"></script>
</head>

<body>
    <div id="main"></div>
    <script type="text/javascript">
        var myChart = echarts.init(document.getElementById('main'));
        var option = {
            title: {
                text: "Vdbench结果展示图",
                subtext: "test-time"
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: ['时间', '带宽速率']
            },
            toolbox: {
                show: true,
                feature: {
                    mark: {
                        show: true
                    },
                    dataView: {
                        show: true,
                        title: '数据视图',
                        optionToContent: function (opt) {
                            var axisData = opt.xAxis[0].data;
                            var series = opt.series;
                            var tdHeads = '<td  style="padding:0 10px">名称</td>';
                            series.forEach(function (item) {
                                tdHeads += '<td style="padding: 0 10px">' + item.name + '</td>';
                            });
                            var table =
                                '<table border="1" style="margin-left:20px;border-collapse:collapse;font-size:14px;text-align:center"><tbody><tr>' +
                                tdHeads + '</tr>';
                            var tdBodys = '';
                            for (var i = 0, l = axisData.length; i < l; i++) {
                                for (var j = 0; j < series.length; j++) {
                                    if (typeof (series[j].data[i]) == 'object') {
                                        tdBodys += '<td>' + series[j].data[i].value + '</td>';
                                    } else {
                                        tdBodys += '<td>' + series[j].data[i] + '</td>';
                                    }
                                }
                                table += '<tr><td style="padding: 0 10px">' + axisData[i] + '</td>' + tdBodys +
                                    '</tr>';
                                tdBodys = '';
                            }
                            table += '</tbody></table>';
                            return table;
                        }
                    },

                    magicType: {
                        show: true,
                        type: ['line', 'bar']
                    },
                    restore: {
                        show: true
                    },
                    saveAsImage: {
                        show: true
                    }
                }
            },
            xAxis: {
                type: 'category',
                data: [],
                axisLabel: {
                    show: true,
                    interval: 0,
                    textStyle: {
                        color: '#ccc'
                    }
                },
                axisLine: {
                    show: false
                },
                axisTick: {
                    show: true
                },
                splitLine: {
                    show: true,
                    lineStyle: {
                        color: '#EAEAEA'
                    }
                },

            },
            yAxis: {
                type: 'value'
            },
            series: [{
                    name: '带宽速率',
                    type: 'line',
                    data: []
                },
                {
                    name: '时间',
                    type: 'line',
                    data: []
                }
            ]
        };
        myChart.setOption(option);
        $.ajax({
            url: "./Output/txtToJson.json",
            dataType: "json"
        }).done(function (res) {
            list = res;
            // list = res.data;
            console.log('Data: ', list);
            const xData = [];
            const maxData = [];
            const minData = [];
            for (let i in list) {
                minData.push(list[i].time);
                maxData.push(list[i].speed);
                xData.push(list[i].keep);

            }
            myChart.setOption({ //在option添加数据
                xAxis: {
                    data: xData
                },
                series: [{
                        data: maxData
                    },
                    {
                        data: minData
                    }
                ]
            });
        }).fail(function (jqXHR) {
            console.log("Ajax Fail: ", jqXHR.status, jqXHR.statusText);
        })
    </script>
</body>

</html>
```

## 效果
![](https://cdn.jsdelivr.net/gh/summerking1/image@main/2021-7-12.PNG) 

# 思路二

## 使用pandas分析数据


```python
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
```

### 生成的图表展示

![](https://cdn.jsdelivr.net/gh/summerking1/image@main/2022-1-20.png)


[相关代码请查看github](https://github.com/summerking1/vdbench-show)

