@echo off
setlocal

cd /d "%~dp0"

set "PY_CMD="
py -3.12 -c "import sys" >nul 2>nul && set "PY_CMD=py -3.12"
if not defined PY_CMD (
    py -3.11 -c "import sys" >nul 2>nul && set "PY_CMD=py -3.11"
)
if not defined PY_CMD (
    py -3.10 -c "import sys" >nul 2>nul && set "PY_CMD=py -3.10"
)
if not defined PY_CMD (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info < (3,14) else 1)" >nul 2>nul && set "PY_CMD=py -3"
)
if not defined PY_CMD (
    echo.
    echo Nao encontrei Python 3.10, 3.11 ou 3.12.
    echo O pygame pode falhar no Python 3.14.
    echo Instale Python 3.12 em https://www.python.org/downloads/
    pause
    goto :end
)

echo Usando: %PY_CMD%
echo [1/2] Instalando dependencias...
%PY_CMD% -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :fallback
%PY_CMD% -m pip install -r requirements.txt
if errorlevel 1 goto :fallback

echo [2/2] Iniciando o projeto...
%PY_CMD% main.py
goto :end

:fallback
echo Tentando com comando "python"...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error
python main.py
goto :end

:error
echo.
echo Nao foi possivel instalar/rodar automaticamente.
echo Verifique se Python esta instalado e no PATH.
pause

:end
endlocal
