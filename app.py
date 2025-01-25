from flask import Flask, request, jsonify
import subprocess
import uuid
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Python Sandbox Service!"})

@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    code = data.get('code', '')

    # 黑名单检查，避免危险代码
    forbidden_keywords = [
    # 模块导入
    'import os', 'import sys', 'import subprocess', 'import shutil',
    'import socket', 'import multiprocessing', 'import threading', 'import asyncio',
    'import logging', 'import pathlib', 'import pickle', 'import base64',
    'import ctypes', 'import pwd', 'import grp',

    # 内置危险函数
    '__import__', 'eval(', 'exec(', 'compile(', 'execfile(', 'input(', 'globals(',
    'locals(', 'vars(', 'delattr(', 'setattr(', 'getattr(', 'open(', 'file(', 
    'os.system', 'os.popen', 'os.execl', 'os.execle', 'os.execlp', 'os.execvp',
    'os.fork', 'os.spawn', 'os.remove', 'os.unlink', 'os.rmdir', 'os.makedirs',
    'os.chmod', 'os.chown', 'os.rename', 'os.kill', 'os.abort',

    # subprocess and shell
    'subprocess.Popen', 'subprocess.run', 'subprocess.call', 'subprocess.check_output',
    'subprocess.check_call', 'shlex.split', 'shutil.rmtree', 'shutil.copy', 'shutil.move',

    # 网络和套接字
    'socket.socket', 'socket.bind', 'socket.connect', 'socket.listen',
    'socket.accept', 'socket.recv', 'socket.send', 'http.client', 'urllib',

    # 多线程/多进程
    'threading.Thread', 'multiprocessing.Process', 'multiprocessing.Pool',

    # 数据操作
    'pickle.load', 'pickle.loads', 'base64.b64decode', 'marshal.loads', 'marshal.load',

    # 文件操作
    'open(', 'write(', 'read(', 'delete(', 'save(', 'chmod(', 'chown(', 'unlink(',

    # 其他危险函数
    'ctypes.', 'getattr(', 'setattr(', 'delattr(', 'globals()', 'locals()',

    'import turtle',
]
    if any(keyword in code for keyword in forbidden_keywords):
        return jsonify({"error": "Forbidden keyword in code"}), 403

    try:
        # 创建临时文件保存代码
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        # 执行用户代码（在隔离环境中运行）
        result = subprocess.run(
            ['python3', temp_file_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        # 删除临时文件
        subprocess.run(['rm', temp_file_path])

        return jsonify({
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)