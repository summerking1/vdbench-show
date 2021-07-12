

思路：拿到vdbench的数据结果，使用工具或者python，将数据json化；然后写一个html页面，使用Ajax，拿到json文件并通过echarts展示之

<!-- more -->


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
        seq = re.compile(" ")
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