@echo off

rem 设置项目根目录
set PROJECT_ROOT=%~dp0
set VENV_DIR=%PROJECT_ROOT%backend\venv

rem 检查虚拟环境是否存在
if not exist "%VENV_DIR%" (
    echo 错误: 虚拟环境不存在，请先运行 install.bat 安装项目
    pause
    exit /b 1
)

echo 启动自主决策Agent项目...

rem 询问是否启用调试模式
echo 请选择日志级别:
echo 1. 普通模式（INFO级别）
echo 2. 调试模式（DEBUG级别，详细日志）

rem 读取用户输入
set /p log_level=请输入选项 (1-2): 

rem 设置日志级别环境变量
if "%log_level%"=="1" (
    set LOG_LEVEL=info
) else if "%log_level%"=="2" (
    set LOG_LEVEL=debug
) else (
    echo 无效选项，默认使用普通模式
    set LOG_LEVEL=info
)

echo 日志级别: %LOG_LEVEL%
echo.

rem 显示启动选项
echo 请选择启动模式:
echo 1. 启动后端服务（FastAPI）
echo 2. 启动前端服务（Vue）
echo 3. 同时启动前后端服务
echo 4. 退出

rem 读取用户输入
set /p choice=请输入选项 (1-4): 

if "%choice%"=="1" goto start_backend
if "%choice%"=="2" goto start_frontend
if "%choice%"=="3" goto start_both
if "%choice%"=="4" goto exit

rem 无效输入
echo 错误: 无效的选项，请重新输入
pause
goto :eof

:start_backend
echo 启动后端服务（FastAPI）...

rem 激活虚拟环境
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo 错误: 激活虚拟环境失败
    pause
    exit /b 1
)

rem 设置PYTHONPATH环境变量
set PYTHONPATH=%PROJECT_ROOT%\backend

rem 启动FastAPI服务
echo 正在启动FastAPI服务...
echo 服务将运行在 http://localhost:8000
echo 按 Ctrl+C 停止服务

cd "%PROJECT_ROOT%backend"
uvicorn app.api.api:app --host 0.0.0.0 --port 8000 --reload

if %errorlevel% neq 0 (
    echo 错误: 启动后端服务失败
    pause
    exit /b 1
)

cd "%PROJECT_ROOT%"
goto :eof

:start_frontend
rem 检查前端目录是否存在
if not exist "%PROJECT_ROOT%frontend" (
    echo 错误: 前端目录不存在
    pause
    exit /b 1
)

echo 启动前端服务（Vue）...

rem 切换到前端目录
cd "%PROJECT_ROOT%frontend"

rem 检查npm是否安装
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到npm，请先安装Node.js
    pause
    exit /b 1
)

rem 启动Vue开发服务器
echo 正在启动Vue开发服务器...
echo 服务将运行在 http://localhost:3000
echo 按 Ctrl+C 停止服务

npm run dev

if %errorlevel% neq 0 (
    echo 错误: 启动前端服务失败
    pause
    exit /b 1
)

cd "%PROJECT_ROOT%"
goto :eof

:start_both
echo 同时启动前后端服务...
echo 后端服务将运行在 http://localhost:8000
echo 前端服务将运行在 http://localhost:3000
echo 按 Ctrl+C 停止服务

rem 启动后端服务（新窗口）
start "后端服务" cmd /c "call "%VENV_DIR%\Scripts\activate.bat" && set PYTHONPATH=%PROJECT_ROOT%\backend && cd "%PROJECT_ROOT%backend" && uvicorn app.api.api:app --host 0.0.0.0 --port 8000 --reload"

rem 等待后端服务启动
echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

rem 启动前端服务（新窗口）
if exist "%PROJECT_ROOT%frontend" (
    start "前端服务" cmd /c "cd "%PROJECT_ROOT%frontend" && npm run dev"
) else (
    echo 警告: 前端目录不存在，仅启动后端服务
)

echo 前后端服务已启动，请在浏览器中访问:
echo - 前端: http://localhost:3000
echo - 后端API文档: http://localhost:8000/docs
echo 按任意键退出...
pause >nul
goto :eof

:exit
echo 退出...
exit /b 0