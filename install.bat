@echo off

rem 设置项目根目录
set PROJECT_ROOT=%~dp0
set VENV_DIR=%PROJECT_ROOT%backend\venv

rem 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 开始安装自主决策Agent项目...

rem 删除旧的虚拟环境（如果存在）
if exist "%VENV_DIR%" (
    echo 删除旧的虚拟环境...
    rmdir /s /q "%VENV_DIR%"
)

rem 创建虚拟环境
echo 创建虚拟环境...
python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo 错误: 创建虚拟环境失败
    pause
    exit /b 1
)

rem 激活虚拟环境
echo 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo 错误: 激活虚拟环境失败
    pause
    exit /b 1
)

rem 升级pip
echo 升级pip...
pip install --upgrade pip
if %errorlevel% neq 0 (
    echo 警告: 升级pip失败，继续执行
)

rem 安装Python依赖
echo 安装Python依赖...
pip install -r "%PROJECT_ROOT%backend\requirements.txt"
if %errorlevel% neq 0 (
    echo 错误: 安装Python依赖失败
    pause
    exit /b 1
)

rem 检查前端目录是否存在
if exist "%PROJECT_ROOT%frontend" (
    echo 安装前端依赖...
    cd "%PROJECT_ROOT%frontend"
    
    rem 检查npm是否安装
    npm --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo 警告: 未找到npm，跳过前端依赖安装
    ) else (
        npm install
        if %errorlevel% neq 0 (
            echo 警告: 安装前端依赖失败，继续执行
        )
    )
    
    cd "%PROJECT_ROOT%"
)

rem 安装完成
echo 安装完成！
echo 项目已成功安装，您可以使用 start.bat 脚本启动项目
echo 按任意键退出...
pause >nul
exit /b 0