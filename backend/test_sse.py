import requests

# Test the SSE endpoint
url = "http://localhost:8000/run-agent-stream?goal=hello&stream_mode=updates"

print(f"Testing SSE endpoint: {url}")
print("=" * 50)

# Use stream=True to get a streaming response
response = requests.get(url, stream=True)

print(f"Status code: {response.status_code}")
print(f"Content type: {response.headers.get('Content-Type')}")
print("=" * 50)

# Read the stream
for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        print(f"Received: {decoded_line}")
        if decoded_line == "data: [DONE]":
            print("Stream completed!")
            break

print("=" * 50)
print("Test completed.")
