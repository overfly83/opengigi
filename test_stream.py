import requests

# 测试流式输出
url = "http://localhost:8000/run-agent-stream?goal=日本的首相是谁&stream_mode=messages"

print("Testing streaming output...")
print("=" * 50)

# 发送GET请求并流式获取响应
response = requests.get(url, stream=True)

# 处理流式响应
for line in response.iter_lines():
    if line:
        # 解码并打印每一行
        decoded_line = line.decode('utf-8')
        print(decoded_line)

print("=" * 50)
print("Test completed.")