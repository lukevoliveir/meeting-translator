@echo off
echo.
echo ======================================
echo Installer - Tradutor de Reunioes
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao foi encontrado!
    echo.
    echo Certifique-se de que Python 3.11+ esta instalado e adicionado ao PATH.
    echo Baixe em: https://www.python.org/
    pause
    exit /b 1
)

echo Criando ambiente virtual...
python -m venv venv

if errorlevel 1 (
    echo ERRO: Falha ao criar o ambiente virtual!
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERRO: Falha ao ativar o ambiente virtual!
    pause
    exit /b 1
)

echo.
echo Atualizando pip...
python -m pip install --upgrade pip >nul 2>&1

echo.
echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ======================================
echo ✓ Instalacao concluida com sucesso!
echo ======================================
echo.
echo IMPORTANTE - Habilitar Stereo Mix no Windows:
echo.
echo 1. Abra Control Panel ^(Painel de Controle^)
echo 2. Va para Sound ^(Som^)
echo 3. Clique na aba Recording ^(Gravacao^)
echo 4. Clique com botao direito em espaco vazio
echo 5. Marque "Show Disabled Devices" ^(Mostrar Dispositivos Desativados^)
echo 6. Clique com botao direito em "Stereo Mix"
echo 7. Clique "Enable" ^(Ativar^)
echo 8. Clique com botao direito em "Stereo Mix" ^> "Set as Default Device"
echo 9. Clique "Apply" e "OK"
echo.
echo Apos ativar o Stereo Mix, execute: run.bat
echo.
pause
