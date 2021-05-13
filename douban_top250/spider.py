#-*- codeing = utf-8 -*-
#@Time : 2020/3/3 17:51
#@Author : 李巍
#@File : spider.py
#@Software: PyCharm

from bs4 import BeautifulSoup     #网页解析，获取数据
import re       #正则表达式，进行文字匹配
import urllib.request,urllib.error      #制定URL，获取网页数据
import csv
import lxml



def main():
    baseurl = "https://movie.douban.com/top250?start="
    #1.爬取网页
    datalist = getData(baseurl)
    savepath = "豆瓣电影Top250.csv"
    #3.保存数据
    saveData(datalist,savepath)



#影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')  
#影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)   #re.S 让换行符包含在字符中
#影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#找到评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#找到概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
#找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)



#爬取一级页面：top250的10页
def getData(baseurl):
    datalist = []
    #250条信息，共10页，每页25条，由于访问次数过多会被豆瓣禁用，此处只爬5页
    #for i in range(4,5): 
    for i in range(0,5): 
        url = baseurl + str(i*25)
        html = askURL(url)      #保存获取到的网页源码

         # 2.逐一解析数据
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):     #查找符合要求的字符串，形成列表
            data = []    #保存一部电影的所有信息
            item = str(item)

            link = re.findall(findLink,item)[0]     
            data.append(link)                       #添加电影详情链接

            data_detail_list = getData_detail(link) #爬取二级页面：电影详情页
            
            imgSrc = re.findall(findImgSrc,item)[0]
            data.append(imgSrc)                     #添加图片

            titles = re.findall(findTitle,item)     #片名可能只有中文名，没有外国名
            if(len(titles) == 2):
                ctitle = titles[0]                  #添加中文名
                data.append(ctitle)
                otitle = titles[1].replace("/","")  #去掉无关的符号
                data.append(otitle)                 #添加外国名
            else:
                data.append(titles[0])
                data.append(' ')        #外国名字留空

            rating = re.findall(findRating,item)[0]
            data.append(rating)                        #添加评分

            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum)                       #提加评价人数

            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq = inq[0].replace("。","")    #去掉句号
                data.append(inq)                # 添加概述
            else:
                data.append(" ")                #留空

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)   #去掉<br/>
            bd = re.sub('/'," ",bd)     #替换/
            data.append(bd.strip())     #去掉前后的空格

            data = data + data_detail_list
            #print(data,"\n\n")

            datalist.append(data)       #把处理好的一部电影信息放入datalist



    return datalist

#爬取二级页面：电影详情页
def getData_detail(link):
    data_detail_list = []
    html = askURL(link) #电影详情页源码
    
    soup = BeautifulSoup(html,"html.parser")
    soup_etree = str(soup)
    soup_etree = lxml.etree.HTML(soup_etree)

    #视频链接
    item = soup.find_all('ul',class_="bs")
    item = str(item)
    item = lxml.etree.HTML(item)

    platform = item.xpath('//li/a/text()') #需要strip()
    platform_link = item.xpath('//li/a/@href')
    #print(platform_link[0])
    video_link = {}
    for i in range(0,len(platform)):
        video_link[platform[i].strip()] = platform_link[i].strip()
    video_link = str(video_link).replace('{',"").replace("}","")
    #video_link = str(video_link).replace('{',"").replace("}","").replace(',',"\n")
    #print(str(video_link))

    data_detail_list.append(video_link)

    #剧情简介
    intro = soup.find_all('div',class_="indent",id="link-report")
    intro = str(intro)
    intro = lxml.etree.HTML(intro)

    #print(link)
    intro_text = intro.xpath('//span[last()-1]/text()') #含<br>、空格
    if(len(intro_text)==0):
        intro_text = intro.xpath('//span/text()') #含<br>、空格
    #intro_text = re.sub('<br>', "", intro_text[0]) 
    intro_text = intro_text[0]
    intro_text = intro_text.replace("<br>","")
    intro_text = intro_text.replace(" ","")
    intro_text = intro_text.replace("\n","")
    data_detail_list.append(intro_text)

    #print(intro_text)

    #部分获奖信息
    #award = soup.find_all("div",class_="award")
    award_name = soup_etree.xpath('//*[@id="content"]/div[3]/div[1]/div[8]/ul/li[1]//text()')
    award_type = soup_etree.xpath('//*[@id="content"]/div[3]/div[1]/div[8]/ul/li[2]//text()')
    award_actor_li = soup_etree.xpath('//*[@id="content"]/div[3]/div[1]/div[8]/ul/li[3]')

    try:
        while(1):
            award_name.remove('\n') #去除\n
    except Exception as e:
        pass
    try:
        while(1):
            award_type.remove('\n') #去除\n
    except Exception as e:
        pass
    
    award = ""
    for i in range(0, len(award_type)):
        #print(lxml.etree.tostring(award_actor_li[i]))
        award_actor = lxml.etree.tostring(award_actor_li[i],encoding='utf-8').decode('utf-8')
        #print(award_actor)
        award_actor = re.findall(r'<li><a href=".*" target="_blank">(.*?)</a></li>', award_actor)
        #print(award_actor)
        if(len(award_actor)!=0):
            award = award + award_name[i] + "/" + award_type[i] + "/" + award_actor[0] + "\n"
        else:
            award = award + award_name[i] + "/" + award_type[i] + "\n"
    #print(award)
    data_detail_list.append(award)
    

    #同类电影推荐
    recommend = soup.find_all("div",class_="recommendations-bd")
    recommend = str(recommend)
    #print(recommend)

    findRecommend = re.compile(r'<a.*?>(.*?)</a>')
    recommend = re.findall(findRecommend, recommend) #list
    recommend = "；".join(recommend)
    # recommend = str(recommend).replace('[', "").replace(']', "")
    data_detail_list.append(recommend)
    #print(recommend)

    return data_detail_list



#得到指定一个URL的网页内容
def askURL(url):
    head = {                #模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
        #askURL(url) #防止爬取不到
    return html


#保存数据
def saveData(datalist,savepath):
    print("save....")
    
    #创建csv文件
    f = open(savepath,'w',encoding='utf-8-sig',newline='')
    save_csv = csv.writer(f)

    col = ["电影详情链接","图片链接","影片中文名","影片外国名","评分","评价数","概况","相关信息","视频链接","剧情简介","获奖情况","同类电影推荐"]
    save_csv.writerow(col) #表头

    for i in range(0,125):
        print("存入第%d条" %(i+1))
        data = datalist[i]
        #print(data)
        save_csv.writerow(data)

    f.close()





if __name__ == "__main__":          #当程序执行时
#调用函数
    main()
    print("爬取完毕！")