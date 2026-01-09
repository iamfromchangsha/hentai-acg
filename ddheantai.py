# remote_server.py
import os
import re
from flask import Flask, request, jsonify

app = Flask(__name__)
BASE_DIR = "/mnt/mydev/写真/"
os.makedirs(BASE_DIR, exist_ok=True)

def safe_filename(filename):
    """安全地处理包含中文的文件名"""
    # 移除危险字符，但保留中文和其他Unicode字符
    if filename is None:
        return None
    # 移除一些危险的字符，保留字母、数字、中文、空格、连字符和下划线
    safe_name = re.sub(r'[<>:"/\\|?*]', '', filename).strip()
    # 防止路径遍历攻击
    safe_name = safe_name.replace('../', '').replace('..\\', '')
    return safe_name

@app.route('/exists')
def file_exists():
    title = request.args.get('title')
    page = request.args.get('page')
    fmt = request.args.get('format', 'jpg')

    if not title or not page:
        return jsonify({"error": "Missing title or page"}), 400

    safe_title = safe_filename(title)
    filename = f"{page}.{fmt}"
    filepath = os.path.join(BASE_DIR, safe_title, filename)
    exists = os.path.isfile(filepath)
    return jsonify({"exists": exists})

@app.route('/upload', methods=['POST'])
def upload_file():
    title = request.form.get('title')
    page = request.form.get('page')
    file = request.files.get('file')

    if not title or not page or not file:
        return jsonify({"error": "Missing title, page or file"}), 400

    safe_title = safe_filename(title)
    upload_dir = os.path.join(BASE_DIR, safe_title)
    os.makedirs(upload_dir, exist_ok=True)

    # 对文件名使用secure_filename以确保安全
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    return jsonify({"message": "OK"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5066)  # 注意端口不要和主程序冲突