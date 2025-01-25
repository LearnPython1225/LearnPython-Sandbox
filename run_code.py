import sys

def main():
    try:
        # 从命令行接收代码文件路径
        if len(sys.argv) != 2:
            print("Usage: python3 run_code.py <file_path>")
            return

        file_path = sys.argv[1]

        # 读取并运行代码
        with open(file_path, 'r') as f:
            code = f.read()
            exec(code)  # 执行用户代码 (危险操作已在主服务中过滤)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()