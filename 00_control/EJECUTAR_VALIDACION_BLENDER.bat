@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "SCRIPT=%~dp0preview_isometrico_blender_v2.py"
set "BLENDER_EXE="
where blender.exe >nul 2>nul
if not errorlevel 1 set "BLENDER_EXE=blender.exe"
if not defined BLENDER_EXE (
    for /f "delims=" %%D in ('dir /b /ad /o-n "C:\Program Files\Blender Foundation\Blender *" 2^>nul') do (
        if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\%%D\blender.exe" (
            set "BLENDER_EXE=C:\Program Files\Blender Foundation\%%D\blender.exe"
        )
    )
)
if not defined BLENDER_EXE (
    echo ERROR: No se encuentra Blender. Instala Blender 4.x o 5.x, o anadelo al PATH.
    pause
    exit /b 1
)
if not exist "%SCRIPT%" (
    echo ERROR: No se encuentra el script junto a este archivo BAT.
    pause
    exit /b 1
)
echo Ejecutando revision isometrica de materiales...
"%BLENDER_EXE%" -b -P "%SCRIPT%"
if errorlevel 1 (
    echo ERROR: No se pudieron producir los renders. Revisa los mensajes anteriores.
    pause
    exit /b 1
)
echo.
echo Renderizados terminados en la subcarpeta 00_control\revision_v2.
pause
