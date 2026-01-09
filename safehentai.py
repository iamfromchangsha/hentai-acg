import requests
import cloudscraper
from bs4 import BeautifulSoup
import os
from pathlib import Path
import re
from urllib.parse import urlparse, urljoin
import time
import random
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


REMOTE_SERVER_URL = "http://192.168.1.103:5066/"  # 替换为实际IP或域名

# 创建带重试机制的会话
def create_session():
    # 使用cloudscraper创建会话，它已经内置了反反爬虫功能
    session = cloudscraper.create_scraper()
    return session

# 用户代理列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

def download_cos_photos():
    # 创建会话
    session = create_session()
    
    # 创建基础目录
    base_dir = Path("")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    shuliang = int(input("请输入起始页面数: "))
    while True:
        cosurl = get_cos_url(shuliang)
        print(f"\n正在处理页面: {cosurl}")
        shuliang += 1
        
        try:
            results = parse_cos_list(cosurl, session)
            if not results:
                print(f"页面 {shuliang-1} 未找到有效内容，跳过")
                continue
                
            print(f"找到 {len(results)} 个COS作品")
            
            for href, title in results:
                if not is_valid_cos_item(href, title):
                    continue
                    
                print(f"\n开始处理作品: {title}")
                
                # 使用清理后的标题名，保留中文字符
                clean_title = clean_filename(title)
                
                cos_page_url = "https://acgmhn.com" + href
                max_page = get_max_page_number(cos_page_url, session)
                
                if max_page is None:
                    print(f"无法获取 {title} 的页数，跳过")
                    continue
                    
                print(f"检测到 {title} 有 {max_page} 张图片")
                download_cos_album(cos_page_url, clean_title, max_page, base_dir, session)
                
        except Exception as e:
            print(f"处理页面时出错: {str(e)}")
            continue

def get_cos_url(page_num):
    return f"https://www.acgmhn.com/cos/index-{page_num}.html"

def parse_cos_list(url, session):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = session.get(url, headers=headers, timeout=10)  # 移除了verify=False参数，cloudscraper默认不验证SSL
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        list_items = soup.find_all('a')
        results = []
        
        for item in list_items:   
            href = item.get('href')
            title = item.get('title')
            if href and title:  # 确保两者都有值
                results.append((href, title))
        
        # 过滤掉无效元素 - 根据实际页面结构调整
        if len(results) > 49:
            return results[14:-35]
        return results
        
    except Exception as e:
        print(f"解析列表页面出错: {str(e)}")
        return []

def is_valid_cos_item(href, title):
    if not title or title == "None":
        return False
    if '3D' in title:
        return False
    if not href.endswith('.html'):
        return False
    if not re.search(r'\d', href):
        return False
    return True

def get_max_page_number(page_url, session):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = session.get(page_url, headers=headers, timeout=10)  # 移除了verify=False参数
        
        if response.status_code != 200:
            print(f"获取页面失败，状态码: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 更精确地查找分页元素
        pagination = soup.find('div', class_='pagination')
        if pagination:
            page_links = pagination.find_all('a')
            if page_links:
                # 获取倒数第二个链接的页码（最后一个通常是"下一页"）
                last_page_link = page_links[-2]
                try:
                    return int(last_page_link.text.strip())
                except ValueError:
                    pass
        
        # 回退方法：查找所有链接中的数字
        a_tags = soup.find_all('a')
        max_number = 0
        
        for tag in a_tags:
            text = tag.get_text().strip()
            if text.isdigit():
                page_num = int(text)
                if page_num > max_number:
                    max_number = page_num
                    
        return max_number if max_number > 0 else None
        
    except Exception as e:
        print(f"获取最大页数出错: {str(e)}")
        return None

def get_image_url(page_url, session):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = session.get(page_url, headers=headers, timeout=10)  # 移除了verify=False参数
        
        if response.status_code != 200:
            print(f"获取图片页面失败，状态码: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 尝试多种方式查找图片
        img_tag = soup.find('img', class_='lazyload')
        if img_tag:
            data_src = img_tag.get('data-src')
            if data_src:
                # 确保URL完整
                if data_src.startswith('//'):
                    data_src = 'https:' + data_src
                elif data_src.startswith('/'):
                    data_src = 'https://www.hentai-acg.com' + data_src
                return data_src
                
        img_tag = soup.find('img', class_='content-image')
        if img_tag:
            src = img_tag.get('src')
            if src:
                # 确保URL完整
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://www.hentai-acg.com' + src
                return src
                
        # 尝试source标签
        source_tag = soup.find('source')
        if source_tag:
            srcset = source_tag.get('srcset')
            if srcset:
                # 取第一个URL
                src = srcset.split()[0]
                # 确保URL完整
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://www.hentai-acg.com' + src
                return src
        
        # 最后尝试第一个img标签
        img_tags = soup.find_all('img')
        if img_tags:
            img_src = img_tags[0].get('src') or img_tags[0].get('data-src')
            if img_src:
                # 确保URL完整
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    img_src = 'https://www.hentai-acg.com' + img_src
                return img_src
                
        return None
        
    except Exception as e:
        print(f"获取图片URL出错: {str(e)}")
        return None

def get_image_format(url):
    if not url:
        return "jpg"
    
    try:
        path = urlparse(url).path
        if '.' in path:
            extension = path.split('.')[-1].lower()
            # 移除可能存在的查询参数
            extension = extension.split('?')[0]
            if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'avif']:
                return extension
        return "jpg"
    except:
        return "jpg"

def folder_exists(folder_path):
    return os.path.exists(folder_path) and os.path.isdir(folder_path)

def file_exists(file_path):
    return os.path.isfile(file_path)

def download_cos_album(first_page_url, title, max_page, base_dir, session):
    print(f"\n📁 处理作品: {title} (共 {max_page} 页)")

    for page_num in range(1, max_page + 1):
        # 构建页面URL
        if page_num == 1:
            page_url = first_page_url
        else:
            page_url = first_page_url.replace('.html', f'-{page_num}.html')

        # 获取图片URL
        img_url = get_image_url(page_url, session)
        if not img_url:
            print(f"⚠️ 第 {page_num} 页无法获取图片URL")
            continue

        img_format = get_image_format(img_url)

        # ✅ 关键：先检查远程是否已存在
        if remote_file_exists(title, page_num, img_format):
            print(f"⏭️ {title} 第 {page_num} 页 已存在，跳过")
            continue

        # 下载图片内容（不保存到本地，直接上传）
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = session.get(img_url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"❌ 下载失败: {img_url} ({response.status_code})")
                continue

            # 创建临时文件或直接用 BytesIO（这里用临时文件更简单）
            temp_path = base_dir / f"temp_{page_num}.{img_format}"
            with open(temp_path, 'wb') as f:
                f.write(response.content)

            # 上传到远程
            if upload_to_remote(title, page_num, temp_path, img_format):
                pass  # 上传成功

            # 删除临时文件
            temp_path.unlink(missing_ok=True)

            time.sleep(random.uniform(0.8, 1.8))

        except Exception as e:
            print(f"💥 下载/上传第 {page_num} 页失败: {e}")



def remote_file_exists(title, page, img_format):
    """检查远程服务器是否存在该文件"""
    try:
        url = f"{REMOTE_SERVER_URL}/exists"
        params = {'title': title, 'page': page, 'format': img_format}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json().get('exists', False)
        else:
            print(f"[Remote Check] 请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[Remote Check] 异常: {e}")
        return False

def upload_to_remote(title, page, file_path, img_format):
    """上传单个文件到远程服务器"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (f"{page}.{img_format}", f)}
            data = {'title': title, 'page': str(page)}
            response = requests.post(f"{REMOTE_SERVER_URL}/upload", data=data, files=files, timeout=30)
            if response.status_code == 200:
                print(f"✅ 已上传 {title} 第 {page} 页 到远程服务器")
                return True
            else:
                print(f"❌ 上传失败: {response.text}")
                return False
    except Exception as e:
        print(f"⚠️ 上传异常: {e}")
        return False
    

def clean_filename(filename):
    """移除文件名中的非法字符，但保留中文字符"""
    # 移除一些危险的字符，保留字母、数字、中文、空格、连字符和下划线
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename).strip()
    # 防止路径遍历攻击
    cleaned = cleaned.replace('../', '').replace('..\\', '')
    return cleaned

if __name__ == "__main__":
    print("COS写真下载器 - 开发者：暗信打中单")
    print("=" * 50)
    print("注意：此程序会忽略SSL证书验证以解决CDN问题")
    print("=" * 50)
    download_cos_photos()