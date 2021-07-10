

**目录：**

[TOC]



# 一、文件说明

**提交的文件包括以下内容：**

1. spider.py：基本网络爬虫源代码
2. readme.md：爬虫作业说明文档
3. 豆瓣电影Top250.csv：spider.py存储的爬虫结果

# 二、环境说明

**编程软件**：vscode

**语言**：python

**模拟浏览器**：Google Chrome

**使用的python类库**：

- **bs4.BeautifulSoup**：解析网页源码以获取数据
- **lxml**：使用xpath表达式解析源码以获取数据
- **re**：正则表达式，进行文字匹配，提取所需数据
- **urllib**：
  1. urllib.request：封装并发送网页请求
  2. urllib.error
- **csv**：爬取结果写入csv文件

# 三、爬取对象

**一级url**：豆瓣电影Top250的前125部电影，https://movie.douban.com/top250?start=...

- "电影详情链接"
- "图片链接"
- "影片中文名"
- "影片外国名"
- "评分"
- "评价数"
- "概况"
- "相关信息"

**二级url**：豆瓣电影Top250的影片详情，https://movie.douban.com/subject/.../

- "视频链接"
- "剧情简介"
- "获奖情况"
- "同类电影推荐"

# 四、实现功能

## 模拟翻页

页面中，"后页"按钮代码如下：

```html
<span class="next">
    <link rel="next" href="?start=25&amp;filter=">
    <a href="?start=25&amp;filter=">后页&gt;</a>
</span>
```

分析得，点击后页后，页面跳转到链接 "https://movie.douban.com/top250?start=25*当前页号"，如下代码实现模拟翻页：

```python
    baseurl = "https://movie.douban.com/top250?start="
    
    for i in range(0,5): 
        url = baseurl + str(i*25)
```

## 爬取两级页面

**爬取一级页面：**

1. `getData(baseurl)`

2. 调用：`main()` 里 `datalist = getData(baseurl)`

3. 返回：

   - 爬取的所有数据列表 `datalist `

   - 每个元素是一部电影的所有信息(list)：

     `["电影详情链接","图片链接","影片中文名","影片外国名","评分","评价数","概况","相关信息","视频链接","剧情简介","获奖情况","同类电影推荐"]`

**爬取二级页面：**

1. `getData_detail(link)`

2. 调用：爬取一级页面时，每获取到一个详情页链接 `link`，就调用`getData_detail(link)` 

3. 返回：

   爬取的详情页信息 `data_detail_list`：`["视频链接","剧情简介","获奖情况","同类电影推荐"]`

## 数据存储到csv

**功能函数**：`saveData(datalist,savepath)`

**功能**：将 `datalist = getData(baseurl)` 返回的每部电影相关信息存入 `豆瓣电影Top250.csv` 的每行。

## 使用cookie登录

**功能函数：**`login_comment(me_url)`

**成功实现：**手动输入浏览器登录后的当前cookie值，封装头部信息后获取登录后的个人页面。

**实现失败**：post实现留言时，因豆瓣对爬虫的限制，只能显示404

