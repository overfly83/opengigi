@echo off

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo 虚拟环境不存在，请先运行 install.bat 安装依赖
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate

REM 启动后端API服务（在新窗口）
echo 启动后端API服务...
start "Backend API" cmd /k "uvicorn api:app --host 0.0.0.0 --port 8000 --reload"

REM 等待后端服务启动
ping 127.0.0.1 -n 3 > nul

REM 启动前端开发服务器（在新窗口）
echo 启动前端开发服务器...
cd frontend
start "Frontend Dev Server" cmd /k "npm run dev"

REM 保持当前窗口打开
echo 服务启动完成！
echo 后端API服务地址: http://localhost:8000
echo 前端开发服务器地址: http://localhost:3000
echo 请在浏览器中访问 http://localhost:3000 开始使用
pause