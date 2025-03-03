# Kokoro-TTS-GPU
 Kokoro-TTS-GPU


Somehow I got this running on GPU on Windows, so here's the whole folder.

Make sure to follow the standard kokoro-tts set up to get things to work first. Basically all you need to do is run:

    uv sync



The two main files you are going to be using is kokoro.py and kokoro.bat. 

kokoro.py will call kokoro.bat

run the program like this:

    kokoro.py alice.txt

And it will launch a gui where you can set all the options.

I'm not sure if this repository will work as is when you download it, but all the files you need are in here.

By all right, I don't think it will work. So here's how i got the GPU working from default kokoro tts clone:

**Steps to Enable GPU for `kokoro-tts` (Windows/NVIDIA):**

1.  **Modify `pyproject.toml`:**
    *   Open the `pyproject.toml` file in your `F:\AI\kokoro-tts` directory.
    *   **Change the `kokoro-onnx` dependency line to:**
        ```toml
        kokoro-onnx = { version = ">=0.3.6", extras = ["gpu"] }
        ```
    *   **Add `onnxruntime-gpu` as a direct dependency in the `[project.dependencies]` section:**
        ```toml
        dependencies = [
            # ... other dependencies ...
            kokoro-onnx = { version = ">=0.3.6", extras = ["gpu"] },
            "onnxruntime-gpu>=1.20.1",  # Add this line
            # ... rest of your dependencies ...
        ]
    ```
    *   **Save the `pyproject.toml` file.**

2.  **Update `kokoro.bat` Script:**
    *   Open your `kokoro.bat` file in a text editor.
    *   **Add these lines *before* the `call .venv\Scripts\activate.bat` line:**
        ```batch
        :: **GPU Enablement Start**
        :: Set ONNX_PROVIDER environment variable to CUDAExecutionProvider for GPU usage
        echo Setting ONNX_PROVIDER=CUDAExecutionProvider for GPU...
        set ONNX_PROVIDER=CUDAExecutionProvider
        echo ONNX_PROVIDER is now set to: %ONNX_PROVIDER%
        :: **GPU Enablement End**
        ```
    *   **Save the `kokoro.bat` file.**

3.  **Synchronize Virtual Environment:**
    *   Open a command prompt and navigate to your `F:\AI\kokoro-tts` directory.
    *   **Activate your virtual environment:** `call .venv\Scripts\activate`
    *   **Run `uv sync` to update dependencies:** `uv sync`

4.  **Verify `onnxruntime-gpu` Installation:**
    *   In the activated virtual environment command prompt, run:
        ```bash
        pip list | findstr onnxruntime
        ```
    *   **Check that `onnxruntime-gpu` is listed in the output.** You should see both `onnxruntime` and `onnxruntime-gpu`.

5.  **Run `kokoro-tts` using `kokoro.bat`:**
    *   Execute your `kokoro.bat` script as you normally would, for example:
        ```bash
        F:\AI\kokoro-tts> kokoro.bat --text "Your text here" --output output_gpu.wav
        ```

6.  **Monitor GPU Usage (Crucial Step):**
    *   While `kokoro-tts` is running, **open NVIDIA Task Manager** (or use `nvidia-smi` in a separate command prompt).
    *   **Check the "GPU" utilization graph.**  If GPU acceleration is working, you should see a noticeable increase in GPU usage while speech is being generated. If GPU usage remains very low, it's likely still running on the CPU.

**If you *still* don't see GPU usage after these steps, then the next thing to try would be:**

*   **Workaround - Uninstall `onnxruntime` and Reinstall `onnxruntime-gpu`:**
    *   In your activated virtual environment command prompt:
        ```bash
        uv pip uninstall onnxruntime
        uv pip install onnxruntime-gpu
        ```
    *   **Then, re-run `kokoro.bat` and check GPU usage again.**


good luck