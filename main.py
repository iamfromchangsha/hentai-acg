import requests
import json
import os
from bs4 import BeautifulSoup
from pathlib import Path
import re
from urllib.parse import quote 
from urllib.parse import urlparse
from utils.AuthV3Util import addAuthParams

#                      10行到53行是对接有道云翻译和正则提取中文
APP_KEY = '6aa02c2db6cf989c'
# 应用密钥
APP_SECRET = 'vF2QGmwVuNHEz6L2ERfAylkK3ygkB7g6'

def extract_chinese_characters(text):
    # 正则表达式模式，匹配所有的中文字符
    pattern = re.compile(r'[\u4e00-\u9fff]+')
    
    # 查找所有匹配项
    matches = pattern.findall(text)
    
    # 将列表中的所有匹配项连接成一个字符串
    chinese_text = ''.join(matches)
    
    return chinese_text
def createRequest(titlea):
    '''
    note: 将下列变量替换为需要请求的参数
    '''
    q = titlea
    lang_from = 'auto'
    lang_to = 'zh-CHS'

    data = {'q': q, 'from': lang_from, 'to': lang_to,}

    addAuthParams(APP_KEY, APP_SECRET, data)

    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = doCall('https://openapi.youdao.com/api', header, data, 'post')
    pattern = re.compile(r'[\u4e00-\u9fff]+')
    hhh = res.content.decode('utf-8')
    matches = pattern.findall(hhh)
    chinese_text = ''.join(matches)
    print(chinese_text)
    return chinese_text


def doCall(url, header, params, method):
    if 'get' == method:
        return requests.get(url, params)
    elif 'post' == method:
        return requests.post(url, params, header)
#                                                                  开头是得到资源获取链接

print("欢迎使用涩涩程序，开发者：暗信打中单\n")
print("请输入要获取的漫画类别：\n")
print("1.漫画(有故障)\n2.图集(未开发)\n3.gif动画(可用)\n4.全彩(未开发)\n5.写真(可用)\n6.有声(可用)\n7.里番(未开发)")
leibie = int(input("请输入数字："))
shuliang = int(input("请输入页面数"))
url = "https://www.hentai-acg.com/"
def urlcounter(leibie,shuliang): #这个函数组合链接，传入类别和页数，传出链接
    if leibie == 1:
        furl = "https://www.hentai-acg.com/h/"
    elif leibie == 2:
        furl = "https://www.hentai-acg.com/hentai/"
    elif leibie == 3:
        furl = "https://www.hentai-acg.com/gif/"
    elif leibie == 4:
        furl = "https://www.hentai-acg.com/tags/full-color.html"
    elif leibie == 5:
        furl = "https://www.hentai-acg.com/cos/"
    elif leibie == 6:
        furl = "https://www.hentai-acg.com/asmr/"
    elif leibie == 7:
        furl = "https://www.hentai-acg.com/hanime/"
    furl = furl + "index-"+str(shuliang)+".html"
    return furl

def foundfm(furl): #这个函数负责解析漫画作品列表页面的html，传入页面链接，传出作品链接，标题，语言列表
    response = requests.get(furl)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    list_items = soup.find_all('li')
    results = []
    for item in list_items:   
        link = item.find('a')
        if link:
            href = link.get('href')
            title = link.get('title')
            lang_span = item.find('span', class_='lang fr')
            if lang_span:
                language = lang_span.text.strip()
                print(str(title)+str(href)+str(language))
                results.append((href, title, language))
    return results

def asmrfound(furl):#这个函数负责解析asmr作品列表页面的html，传入页面链接，传出作品链接，标题列表
    response = requests.get(furl)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    list_items = soup.find_all('li')
    results = []
    for item in list_items:   
        link = item.find('a')
        if link:
            href = link.get('href')
            title = link.get('title')
            results.append((href, title))
            
    
    # 删除前十个元素
    results = results[10:] #这里是为了去除head里面的一些链接
    print(results) # 这里使用切片操作，从第11个元素（索引为10）开始截取列表
    
    return results

def giffound(furl):#同上
    response = requests.get(furl)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    list_items = soup.find_all('a')
    results = []
    for item in list_items:   
        href = item.get('href')
        title = item.get('title')
        results.append((href, title))
            
    
    # 删除前十个元素
    '''
    results = results[10:] 
    '''
    results = results[14:] 
    results = results[:-35]

    print(results) # 这里使用切片操作，从第11个元素（索引为10）开始截取列表
    
    return results
def sefound(href):#这个函数复制解析漫画作品页面，传入作品链接，传出漫画图片链接列表
    surl = url + href
    response = requests.get(surl)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    a_tags = soup.find_all('a')
    max_number = None
    for tag in a_tags:
        text = tag.get_text()
        try:
            number = int(text)
            if max_number is None or number > max_number:
                 max_number = number
        except ValueError:
             continue
    source_tag = soup.find('source')
    srcset_value = source_tag.get('srcset')
    srcset_value = srcset_value[:-6]
    a=0
    aresults = []
    while a< max_number:
        imgurl = srcset_value + str(a)+".avif"
        a = a + 1
        aresults.append(imgurl)
    return aresults

def yema(href):#负责cos部分单个作品内所有照片解析的函数组中获取最大页码的函数，有问题需要检修！！！！！！！！！！！
    surl = url + href
    response = requests.get(surl)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    a_tags = soup.find_all('a')
    max_number = None
    for tag in a_tags:
        text = tag.get_text()
        try:
            number = int(text)
            if max_number is None or number > max_number:
                 max_number = number
        except ValueError:
             continue
    return max_number

def minnum(url):
    numbers_with_leading_zeros = url[-8:-5]

# 去掉前面的零，并转换为整数
# 使用 lstrip('0') 去除左侧的零
# 如果去除零后字符串为空，则表示原数字是0
    number = int(numbers_with_leading_zeros.lstrip('0')) if numbers_with_leading_zeros.lstrip('0') else 0
    return number

def zhijiepa(cosurl):#这个函数负责直接从作品页面直接获取图片链接，传入作品链接，传出图片链接列表
    response = requests.get(cosurl)
    soup = BeautifulSoup(response.text, "html.parser")
    list_items = soup.find_all('img')
    firstimg = list_items[0]
    imgurl = firstimg.get('src')
    return imgurl

def check_and_download(target_directory):#这个函数负责判断文件夹是否存在，如果存在就跳过下载，传入作品名，作品链接，目标文件夹，完成判断
    # 构建完整的路径
    folder_path = os.path.join(target_directory)
    
    # 检查文件夹是否已经存在
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return True
    else:
        return False

def sanshyy(file_path):   #这个函数负责检查文件是否已经存在
 
    if os.path.isfile(file_path):
        return True
    else:
        return False

def downloadimg(imgurl,b,leibie,language,title):#这个函数只负责漫画作品的下载，传入图片链接，图片序号，作品类型，语言，作品名，下载图片，完成下载后打印下载路径
    asaresponse = requests.get(imgurl)
    filename = str(b)+".avif"
    if leibie == 1:
        name = "漫画"
    elif leibie == 2:
        name = "图集"
    elif leibie == 3:
        name = "gif动画"
    elif leibie == 4:
        name = "全彩"
    elif leibie == 5:
        name = "写真"
    elif leibie == 6:
       name = "有声"
    elif leibie == 7:
        name = "里番"
    save_path = Path("./涩涩/"+name+"/"+language+"/"+title)
    save_path.mkdir(parents=True, exist_ok=True)
    full_path = save_path / filename
    with open(full_path, 'wb') as f:
        f.write(asaresponse.content)
    print(f"图片已保存到 {full_path}")

def get_image_format_from_url(url):#这个函数获取图片格式，传入图片链接，返回图片格式
    # 解析URL
    parsed_url = urlparse(url)
    # 获取路径
    path = parsed_url.path
    # 分割路径，获取文件扩展名
    extension = path.split('.')[-1].lower()
    
    # 根据常见的图片扩展名返回图片格式
    if extension in ['jpg', 'jpeg']:
        return 'JPEG'
    elif extension == 'png':
        return 'PNG'
    elif extension == 'gif':
        return 'GIF'
    elif extension == 'bmp':
        return 'BMP'
    elif extension == 'webp':
        return 'WebP'
    elif extension == 'avif':
        return 'AVIF'
    else:
        return 'Unknown'
def downloadmp(imgurl,leibie,title):#这个函数只负责gif动画作品下载，传入图片链接，作品类型，作品名，下载图片，完成下载后打印下载路径
    asaresponse = requests.get(imgurl)
    filename = title+".mp4"
    if leibie == 1:
        name = "漫画"
    elif leibie == 2:
        name = "图集"
    elif leibie == 3:
        name = "gif动画"
    elif leibie == 4:
        name = "全彩"
    elif leibie == 5:
        name = "写真"
    elif leibie == 6:
       name = "有声"
    elif leibie == 7:
        name = "里番"
    save_path = Path("./涩涩/"+name)
    save_path.mkdir(parents=True, exist_ok=True)
    full_path = save_path / filename
    with open(full_path, 'wb') as f:
        f.write(asaresponse.content)
    print(f"图片已保存到 {full_path}")

# 主函数开始
if leibie == 1:
    furl =  urlcounter(leibie,shuliang)
    results = foundfm(furl)
    for href, title, language in results:
         aresults = sefound(href)
         b=1
         print(title+"\n"+"开发者：暗信打中单"+"\n"+"我永远喜欢牧濑红莉栖")
         yunfanyi = createRequest(title)
        
         '''
         title = title[:5]
         '''
        
         for imgurl in aresults:
            downloadimg(imgurl,b,leibie,language,yunfanyi)
            print(title)
            b = b + 1
elif leibie == 6:#asmr
     furl = urlcounter(leibie,shuliang)
     results = asmrfound(furl)
     for href, title in results:
        mpresponse = requests.get(url+href)
        html = mpresponse.text
        soup = BeautifulSoup(html, "html.parser")
        audio_tags = soup.find_all('audio')
        for audio in audio_tags:
            srmc = audio.find('source')['src']
            mfile_name = title + '.mp3'
            save_path = Path("./涩涩/声音/")
            filename = title+".mp3"
            save_path.mkdir(parents=True, exist_ok=True)
            response = requests.get(srmc)
            full_path = save_path / filename
            with open(full_path, 'wb') as file:
                file.write(response.content)
                print(f"文件已保存到 {full_path}")
elif leibie == 3:#gif动画
    furl = "https://www.hentai-acg.com/gif/index-"+str(shuliang)+".html"
    response = requests.get(furl)
    if 'charset' in response.headers.get('content-type', '').lower():
    # 如果响应头中包含字符集信息，则直接使用该字符集
        response.encoding = response.apparent_encoding
    else:
    # 否则假设为 UTF-8
        response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    list_items = soup.find_all('a')
    results = []
    for item in list_items:   
        href = item.get('href')
        title = item.get('title')
        results.append((href, title))
    results = results[14:] 
    print(results)
    for href, title in results:
        gifurl = "https://www.hentai-acg.com"+href
        response = requests.get(gifurl)
        soup = BeautifulSoup(response.text, "html.parser")
        video = soup.find('source')
        src = video.get('src')
        print(src)
        yunfanyigif = createRequest(title)
        filename =  yunfanyigif+".mp4"
        savepath = Path("./涩涩/gif动画/")
        savepath.mkdir(parents=True, exist_ok=True)
        with open(savepath / filename, 'wb') as f:
            f.write(requests.get(src).content)
elif leibie == 5:#cos
    while True:
        cosurl= urlcounter(leibie,shuliang)
        shuliang = shuliang + 1
        results = giffound(cosurl)
        print(results)
        for href, title in results:
            tityy = str(title)
            if tityy == "None":
                print("skip")
            else:
                if '3D' in tityy:
                    print("skip")
                else:
                    if href[-4:] != 'html':
                        print("skip")
                    else:
                        if not re.search(r'\d', href):
                            print("skip")
                        else:
                            cosurl = "https://www.hentai-acg.com"+href
                            '''
                            response = requests.get(cosurl)
                            soup = BeautifulSoup(response.text, "html.parser")
                            list_items = soup.find_all('img')
                            firstimg = list_items[0]
                            imgurl = firstimg.get('src')
                            '''
                            rinima = 1#用来控制循环次数,还有文件名
                            maxnum = yema(href)
                            if maxnum == None:
                                print("skip")
                            else:
                                
                                    
                                '''
                                minnumer = minnum(imgurl)
                                '''
                                print("检测到"+title+"有"+str(maxnum)+"张图片,愿你能和重要之人再度重逢")
                                save_path = Path("./涩涩/写真/"+str(title))
                                cesave_path = Path("./涩涩/写真/"+str(title)+"[暗信打中单]")
                                buyaoneishe=check_and_download(cesave_path)#路径重复排除
                                if buyaoneishe==True:
                                    print(title+"已下载\n"+"比希望更炙热，比绝望更深邃的，是爱啊!")
                                    continue
                                save_path.mkdir(parents=True, exist_ok=True)
                                ybmq = False
                                while rinima<=maxnum:
                                    imgurl = zhijiepa(cosurl)
                                    woliejakai=get_image_format_from_url(imgurl)
                                    filename = str(rinima)+"."+woliejakai
                                    
                                    wantneishe = sanshyy(save_path / filename)
                                    if wantneishe == True:
                                        print(filename+"已存在")
                                        rinima = rinima + 1
                                        ybmq = True
                                        continue
                                    if ybmq == True:
                                        rinima = rinima - 1
                                        cosurl = "https://www.hentai-acg.com"+href[:-5]+"-"+str(rinima)+".html"
                                        imgurl = zhijiepa(cosurl)
                                        ybmq = False
                                        filename = str(rinima)+"."+woliejakai
                                        print("已找到断点"+str(rinima)+"."+woliejakai)
                                    with open(save_path / filename, 'wb') as f:
                                        f.write(requests.get(imgurl).content)
                                        print(f"{shuliang-1}图片已保存到 {save_path / filename}.\n这就是世界的真理，连关天则哦")
                                    rinima = rinima + 1
                                    cosurl = "https://www.hentai-acg.com"+href[:-5]+"-"+str(rinima)+".html"
                                    if rinima > maxnum:
                                        new_path = Path("./涩涩/写真/"+str(title)+"[暗信打中单]")
                                        os.rename(save_path, new_path)


            



'''
             jii = minnumer
             maxnum = maxnum + minnumer
             
             while jii < maxnum:
                if jii < 10:
                    jiis = "00"+str(jii)
                elif jii < 100:
                    jiis = "0"+str(jii)
                else:
                    jiis = str(jii)
                imgurla = imgurl[:-8]+str(jiis)+".webp"
                print(imgurla)
                filename = str(jii)+".webp"
                jii = jii + 1
                


'''
#嗨喽嗨喽，这里记载一下11/7号已经完成的一些功能。
#漫画方面实现了作品名的翻译
#asmr和gif动画方面都完成了下载功能
#cos方面实现了断点下载
            
        
#4月中旬来做维护，修改替换了现ACG英文网站，修改了部分furl未定义的问题，预计加入错误skip功能
#四月下旬给写真功能加入了页面数的递增,加入了对href的有效性判断
