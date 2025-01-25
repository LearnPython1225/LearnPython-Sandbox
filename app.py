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

    # 安全检查：禁止危险关键字
    blacklist = [
        'import os', 'import sys', 'import subprocess', '__import__',
        'eval(', 'exec(', 'open(', 'write(', 'read(', 'os.system'
    ]
    if any(keyword in code for keyword in blacklist):
        return jsonify({"error": "Forbidden keyword in code"}), 403

    try:
        # 临时文件保存用户代码
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            file_name = temp_file.name

        # 使用 Docker 运行代码
        container_name = f"sandbox-{uuid.uuid4()}"
        command = [
            "docker", "run", "--rm", "--network", "none", "--memory=128m", "--cpus=0.5",
            "--name", container_name,
            "-v", f"{file_name}:/sandbox/user_code.py:ro",
            "python:3.10-slim", "python3", "/sandbox/user_code.py"
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)

        # 删除临时文件
        os.unlink(file_name)

        # 返回结果
        return jsonify({
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timeout"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)