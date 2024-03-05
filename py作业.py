import requests  # 发送请求
from bs4 import BeautifulSoup  # 解析网页
import pandas as pd  # 存取csv
from time import sleep  # 等待时间
import os
from urllib.request import unquote
import urllib
from pyecharts import options as opts
from pyecharts.charts import Bar

book_name = []  # 书名
book_star = []  # 书籍评分
book_star_people = []  # 评分人数
book_author = []  # 书籍作者
book_publisher = []  # 出版社
book_pub_year = []  # 年份
book_comment = []  # 一句话评价


def get_book_info(url, headers):
	res = requests.get(url, headers=headers)
	soup = BeautifulSoup(res.text, 'html.parser')
	for book in soup.select('.item'):
		name = book.select('.pl2 a')[0]['title']  # 书名
		book_name.append(name)
		star = book.select('.rating_nums')[0].text  # 书籍评分
		book_star.append(star)
		star_people = book.select('.pl')[1].text  # 评分人数
		star_people = star_people.strip().replace(' ', '').replace('人评价', '').replace('(\n', '').replace('\n)', '')  # 数据清洗
		book_star_people.append(star_people)

		# 没有一句话评价，比如倒数第二名，君主论
		if book.select('.quote span'):
			book_comment.append(book.select('.quote span')[0].text)
		else:
			book_comment.append(None)

		info = book.select('.pl')[0].text.split('/')
		if len(info) == 5:  # 正常情况
			book_author.append(info[0])
			book_publisher.append(info[2])

			info[3] = (info[3].encode('utf-8')).decode("utf-8")
			info[3] = info[3][0:5]
			book_pub_year.append(info[3])

		elif len(info) == 4:  # 没有译者，比如：第一名，红楼梦
			book_author.append(info[0])
			book_publisher.append(info[1])

			info[2] = (info[2].encode('utf-8')).decode("utf-8")
			info[2] = info[2][0:5]
			book_pub_year.append(info[2])
   
		elif len(info) == 6:  # 有2个价格，比如：第一页，福尔摩斯探案全集（上中下）
			book_author.append(info[0])

			if (info[3][1] == '2' or info[3][1] == '1'):
				info[3] = (info[3].encode('utf-8')).decode("utf-8")
				info[3] = info[3][0:5]
				book_publisher.append(info[2])
				book_pub_year.append(info[3])
			else:
				info[4] = (info[4].encode('utf-8')).decode("utf-8")
				info[4] = info[4][0:5]
				book_publisher.append(str(info[2]) + '/' + str(info[3]))
				book_pub_year.append(info[4])
			
		elif len(info) == 3:  # 没有作者，且没有译者，比如：第5页，十万个为什么
			book_author.append(None)
			book_publisher.append(info[0])

			info[1] = (info[1].encode('utf-8')).decode("utf-8")
			info[1] = info[1][0:5]
			book_pub_year.append(info[1])
   
		else:
			pass


def save_to_csv(csv_name):
	df = pd.DataFrame()  # 初始化一个DataFrame对象
	df['书名'] = book_name
	df['作者'] = book_author
	df['出版社'] = book_publisher
	df['年份'] = book_pub_year
	df['评分'] = book_star
	df['评分人数'] = book_star_people
	df['一句话评价'] = book_comment
	df.to_csv(csv_name, encoding='utf_8_sig')  # 将数据保存到csv文件

def getHTMLText(url, headers):
    try:
        r = requests.get(url,headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
        
    except:
        return ""
def parsePage(ilt,html):
    try:
        soup=BeautifulSoup(html,"html.parser")
        for img in soup.find_all('img',{"width":"90"}):
            ilt.append(img['src'])
            
    except:
        print("")
def main(headers):
    last_url=urllib.request.unquote('https://book.douban.com/top250?start=')
    
    imalist=[]
    for i in range(10):
        try:
            url=last_url+str(25*i)
            html = getHTMLText(url, headers)
            parsePage(imalist,html)
        except:
            continue
    x=0
    for u in imalist:
        r =requests.get(u)
        x=x+1
        dir_name='./images'
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        with open( dir_name+ "/" +'{}.jpg'.format(x),'wb') as f:
            f.write(r.content)


def getzoombar(data):
    year_counts = data['年份'].value_counts()
    year_counts.columns = ['年份', '数量']
    year_counts = year_counts.sort_index()
    c = (
        Bar()
        .add_xaxis(list(year_counts.index))
        .add_yaxis('出版数量', year_counts.values.tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title='各年份出版图书数量'),
            yaxis_opts=opts.AxisOpts(name='出版数量'),
            xaxis_opts=opts.AxisOpts(name='年份'),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_='inside')],)
        .render('各年份出版图书数量.html')
        )
    
def getcountrybar(data):
    country_counts = data['出版社'].value_counts()
    country_counts.columns = ['出版社', '数量']
    country_counts = country_counts.sort_values(ascending=True)
    c = (
        Bar()
        .add_xaxis(list(country_counts.index)[-10:])
        .add_yaxis('出版社出版数量', country_counts.values.tolist()[-10:])
        .reversal_axis()
        .set_global_opts(
        title_opts=opts.TitleOpts(title='出版社出版图书数量'),
        yaxis_opts=opts.AxisOpts(name='出版社'),
        xaxis_opts=opts.AxisOpts(name='出版数量'),
        )
        .set_series_opts(label_opts=opts.LabelOpts(position="right"))
        .render('各出版社出版图书数量前十.html')
        )
    
if __name__ == "__main__":
	# 定义一个请求头
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.0.7271 SLBChan/105'}
	# 开始爬取豆瓣数据
	for i in range(10):  # 爬取共10页，每页25条数据
		page_url = 'https://book.douban.com/top250?start={}'.format(str(i * 25))
		print('开始爬取第{}页，地址是:{}'.format(str(i + 1), page_url))
		get_book_info(page_url, headers)
		sleep(1)  # 等待1秒
	# 保存到csv文件
	save_to_csv(csv_name="BookDouban250.csv")
	main(headers)
	data = pd.read_csv("BookDouban250.csv")
	getzoombar(data)
	getcountrybar(data)
