@echo off
chcp 65001 > nul
chcp  & rem Display current code page to verify UTF-8 is set
setlocal

:: Check if .venv exists
if not exist ".venv\" (
    echo Virtual environment not found. First run:
    echo   uv venv .venv
    echo   uv sync
    exit /b 1
)

:: **GPU Enablement Start**
:: Set ONNX_PROVIDER environment variable to CUDAExecutionProvider for GPU usage
echo Setting ONNX_PROVIDER=CUDAExecutionProvider for GPU...
set ONNX_PROVIDER=CUDAExecutionProvider
echo ONNX_PROVIDER is now set to: %ONNX_PROVIDER%
:: **GPU Enablement End**

:: Activate environment
call .venv\Scripts\activate.bat

:: Run kokoro-tts with all arguments
python kokoro-tts %*

:: Deactivate environment when finished (optional, but good practice)
:: deactivate
:: endlocal  <- 'endlocal' already handles environment cleanup, no need for 'deactivate' here in this script structure

endlocal
