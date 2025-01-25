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
    forbidden_keywords = ['import os', 'import sys', 'subprocess', '__import__', 'eval(', 'exec(']
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