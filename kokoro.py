import os
import sys
import glob
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import configparser
import ftfy  # Import the ftfy module
import codecs  # Import the codecs module for encoding/decoding

CONFIG_FILE = "config.ini"
DEFAULT_KOKORO_PATH = r"kokoro.bat"

class KokoroGUI:
    def __init__(self, root, initial_files):
        self.root = root
        root.title("Kokoro TTS Processor")
        self.voices = [
            "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica",
            "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah",
            "af_sky", "am_adam", "am_echo", "am_eric", "am_fenrir",
            "am_liam", "am_michael", "am_onyx", "am_puck", "am_santa",
            "bf_alice", "bf_emma", "bf_isabella", "bf_lily", "bm_daniel",
            "bm_fable", "bm_george", "bm_lewis", "ef_dora", "em_alex",
            "em_santa", "ff_siwis", "ff_siwis", "hf_alpha", "hf_beta", "hm_omega",
            "hm_psi", "if_sara", "im_nicola", "jf_alpha", "jf_gongitsune",
            "jf_nezumi", "jf_tebukuro", "jm_kumo", "pf_dora", "pm_alex",
            "pm_santa", "zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi"
        ]
        self.languages = [
            ("en-gb", "English (British)"),
            ("en-us", "English (American)"),
            ("fr-fr", "French"),
            ("it", "Italian"),
            ("ja", "Japanese"),
            ("cmn", "Mandarin Chinese")
        ]
        self.file_list = []
        self.actual_lang_code = "en-gb"

        # Configuration handling
        self.config = configparser.ConfigParser()
        self.kokoro_path = self.load_kokoro_path()

        self.create_widgets()
        if initial_files:
            self.add_files(initial_files)

    def load_kokoro_path(self):
        if not os.path.exists(CONFIG_FILE):
            self.create_default_config()
        self.config.read(CONFIG_FILE)
        return self.config.get("Paths", "kokoro_path", fallback=DEFAULT_KOKORO_PATH)

    def create_default_config(self):
        self.config["Paths"] = {"kokoro_path": DEFAULT_KOKORO_PATH}
        with open(CONFIG_FILE, "w") as configfile:
            self.config.write(configfile)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Path Configuration Frame
        path_frame = ttk.LabelFrame(main_frame, text="Kokoro TTS Path")
        path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(path_frame, text="kokoro.bat Path:").grid(row=0, column=0, padx=5, sticky="w")
        self.path_var = tk.StringVar(value=self.kokoro_path)
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=0, column=1, padx=5, sticky="ew")
        path_frame.columnconfigure(1, weight=1) # Make entry expand

        def browse_kokoro_path():
            filepath = filedialog.askopenfilename(
                title="Select kokoro.bat",
                filetypes=[("Batch files", "*.bat"), ("All Files", "*.*")]
            )
            if filepath:
                self.path_var.set(filepath)
                self.save_kokoro_path()

        ttk.Button(path_frame, text="Browse", command=browse_kokoro_path).grid(row=0, column=2, padx=5)

        file_frame = ttk.LabelFrame(main_frame, text="Files to Process")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED, width=60, height=8)
        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        scrollbar.grid(row=0, column=1, sticky="ns")
        file_frame.columnconfigure(0, weight=1) # Make listbox expand
        file_frame.rowconfigure(0, weight=1)   # Make listbox expand

        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=0, column=2, sticky="nsew", padx=5)
        ttk.Button(btn_frame, text="Add Files", command=self.browse_files).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_files).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Move Up", command=lambda: self.move_file(-1)).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Move Down", command=lambda: self.move_file(1)).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(fill=tk.X, pady=2)

        voice_frame = ttk.LabelFrame(main_frame, text="TTS Settings")
        voice_frame.pack(fill=tk.X, pady=5)
        ttk.Label(voice_frame, text="Voice:").grid(row=0, column=0, padx=5, sticky="w")
        self.voice_var = tk.StringVar(value=self.voices[21])
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var,
                                         values=self.voices, width=25, state="readonly")
        self.voice_dropdown.grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(voice_frame, text="Language:").grid(row=0, column=2, padx=5, sticky="w")
        self.lang_var = tk.StringVar(value="English (British)")
        self.lang_dropdown = ttk.Combobox(voice_frame, textvariable=self.lang_var,
                                        values=[name for code, name in self.languages],
                                        width=15, state="readonly")
        self.lang_dropdown.grid(row=0, column=3, padx=5)
        self.lang_dropdown.bind("<<ComboboxSelected>>", self.update_lang_code)
        ttk.Label(voice_frame, text="Speed:").grid(row=0, column=4, padx=5, sticky="w")
        self.speed_var = tk.DoubleVar(value=0.8)
        ttk.Spinbox(voice_frame, from_=0.5, to=2.0, increment=0.1,
                   textvariable=self.speed_var, width=5).grid(row=0, column=5, padx=5)
        ttk.Label(voice_frame, text="Format:").grid(row=0, column=6, padx=5, sticky="w")
        self.format_var = tk.StringVar(value="wav")
        ttk.Combobox(voice_frame, textvariable=self.format_var, values=["wav", "mp3"],
                    width=5, state="readonly").grid(row=0, column=7, padx=5)


        split_frame = ttk.Frame(main_frame)
        split_frame.pack(fill=tk.X, pady=5)
        ttk.Label(split_frame, text="Split Directory:").pack(side=tk.LEFT, padx=5)
        self.split_var = tk.StringVar()
        ttk.Entry(split_frame, textvariable=self.split_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(split_frame, text="Browse", command=self.browse_split_dir).pack(side=tk.LEFT)

        ttk.Button(main_frame, text="Start Processing", command=self.process_files).pack(pady=10)

    def save_kokoro_path(self):
        self.kokoro_path = self.path_var.get()
        self.config["Paths"]["kokoro_path"] = self.kokoro_path
        with open(CONFIG_FILE, "w") as configfile:
            self.config.write(configfile)

    def add_files(self, files):
        new_files = []
        for pattern in files:
            expanded = glob.glob(pattern, recursive=True)
            for path in expanded:
                abs_path = os.path.abspath(path)
                if os.path.isfile(abs_path) and abs_path not in self.file_list:
                    new_files.append(abs_path)
        self.file_list.extend(new_files)
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for f in self.file_list:
            self.listbox.insert(tk.END, os.path.basename(f))

    def browse_files(self):
        files = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=[("Supported Files", "*.txt *.epub *.pdf"), ("All Files", "*.*")]
        )
        if files:
            self.add_files(files)

    def remove_files(self):
        selected = self.listbox.curselection()
        if selected:
            for index in reversed(sorted(selected)):
                del self.file_list[index]
            self.update_listbox()

    def move_file(self, direction):
        selected = self.listbox.curselection()
        if len(selected) == 1:
            index = selected[0]
            new_index = index + direction
            if 0 <= new_index < len(self.file_list):
                self.file_list.insert(new_index, self.file_list.pop(index))
                self.update_listbox()
                self.listbox.select_set(new_index)

    def clear_files(self):
        self.file_list = []
        self.update_listbox()

    def browse_split_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.split_var.set(os.path.abspath(directory))

    def update_lang_code(self, event):
        display_name = self.lang_var.get()
        for code, name in self.languages:
            if name == display_name:
                self.actual_lang_code = code
                return
        self.actual_lang_code = "en-gb"

    def sanitize_input_text(self, input_file):
        """Sanitizes the input file content using ftfy and saves it as a new file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f: # Try UTF-8 first
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(input_file, 'r', encoding='cp1252') as f: # Try cp1252 if UTF-8 fails
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(input_file, 'r', encoding='latin-1') as f: # Try latin-1 as fallback
                        content = f.read()
                except Exception as e: # If all fail, raise error and return None
                    messagebox.showerror("Encoding Error", f"Could not decode file: {input_file}\nError: {e}")
                    return None, None

        try:
            fixed_text = ftfy.fix_text(content) # Sanitize with ftfy
        except Exception as e:
            messagebox.showerror("ftfy Error", f"Error sanitizing text with ftfy for file: {input_file}\nError: {e}")
            return None, None

        # Create a new filename for sanitized version
        base, ext = os.path.splitext(input_file)
        sanitized_file = base + "_sanitized" + ext
        try:
            with open(sanitized_file, 'w', encoding='utf-8') as f:
                f.write(fixed_text)
            return sanitized_file # Return new sanitized file path
        except Exception as e:
            messagebox.showerror("File Save Error", f"Could not save sanitized file: {sanitized_file}\nError: {e}")
            return None


    def process_files(self):
        import threading  # Import threading here - already present
        import time       # ADD THIS LINE - Import time here!

        if not self.file_list:
            messagebox.showerror("Error", "No files selected for processing")
            return

        if not os.path.exists(self.kokoro_path):
            messagebox.showerror("Error", f"Kokoro TTS batch file not found at:\n{self.kokoro_path}\nPlease check the path in the 'Kokoro TTS Path' section.")
            return

        processing_params = {
            "voice": self.voice_var.get(),
            "language": self.actual_lang_code,
            "speed": str(self.speed_var.get()),
            "format": self.format_var.get(),
            "split_dir": self.split_var.get() or "None",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.root.destroy() # Consider moving this after a success message or removing it

        for original_file_path in self.file_list:
            input_file_path = original_file_path # Default to original path

            input_file_path_sanitized = self.sanitize_input_text(original_file_path) # Sanitize input using ftfy
            if not input_file_path_sanitized: # If sanitization failed for this file, skip to next
                continue # sanitize_input_text already showed an error message
            input_file_path = input_file_path_sanitized # Use the new sanitized file for processing


            output_file = os.path.splitext(input_file_path)[0] + f".{processing_params['format']}" # Output based on *input_file_path*
            log_file = output_file + ".log"
            cmd = [
                self.kokoro_path,  # Use self.kokoro_path here
                input_file_path,    # Use input_file_path (original or sanitized)
                output_file,
                "--voice", processing_params["voice"],
                "--lang", processing_params["language"],
                "--speed", processing_params["speed"],
                "--format", processing_params["format"]
            ]
            if processing_params["split_dir"] != "None":
                cmd += ["--split-output", processing_params["split_dir"]]

            # Explicitly set environment for subprocess to use UTF-8
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            with open(log_file, "w", encoding="utf-8") as log:
                log.write(f"Kokoro TTS Processing Log\n{'='*30}\n")
                log.write(f"Timestamp: {processing_params['timestamp']}\n")
                log.write(f"Input File (Original): {original_file_path}\n") # Log original path
                log.write(f"Input File (Sanitized with ftfy): {input_file_path}\n") # Log sanitized path
                log.write(f"Output File: {output_file}\n")
                log.write(f"Voice: {processing_params['voice']}\n")
                log.write(f"Language: {processing_params['language']}\n")
                log.write(f"Speed: {processing_params['speed']}\n")
                log.write(f"Format: {processing_params['format']}\n")
                log.write(f"Split Directory: {processing_params['split_dir']}\n")
                log.write("\nProcessing Details:\n")

                # ASCII Spinning Wheel in GUI - Define it here, inside process_files for scope
                def spinning_wheel_gui(message, log):
                    spin_chars = ["-", "\\", "|", "/"]
                    stop_event = threading.Event()
                    def spin_thread_func():
                        import time # Import time here - although it's imported outside as well now.
                        while not stop_event.is_set():
                            for spin in spin_chars:
                                if stop_event.is_set():
                                    break
                                sys.stdout.write(f"\r{message} {spin}") # This stdout is for *console* output
                                sys.stdout.flush()
                                time.sleep(0.1)
                        sys.stdout.write(f"\r{message} Done!   \n")
                        sys.stdout.flush()
                    spin_thread = threading.Thread(target=spin_thread_func)
                    spin_thread.start()
                    return stop_event, spin_thread


                stop_spin_event, spin_thread = spinning_wheel_gui("Processing...", log) # Start ASCII spin in console

                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8', # Explicitly set encoding for subprocess output
                        errors='replace',
                        cwd=os.path.dirname(self.kokoro_path),
                        env=env # Pass the environment with PYTHONIOENCODING
                    )
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            print(output.strip()) # Print to *GUI console* - might still have encoding issues here
                            log.write(output)
                    exit_code = process.poll()
                    stop_spin_event.set() # Stop spinning wheel
                    spin_thread.join() # Wait for spin thread to finish

                    if exit_code == 0:
                        log.write("\nSUCCESSFUL PROCESSING\n")
                        print(f"\nSuccessfully created: {output_file}")
                        print(f"Log file created: {log_file}")
                    else:
                        log.write(f"\nPROCESSING FAILED (Code: {exit_code})\n")
                        print(f"\nError processing {original_file_path} (Code: {exit_code})") # Use original_file_path in error message
                except Exception as e:
                    stop_spin_event.set() # Ensure spinning wheel stops on error
                    spin_thread.join()
                    log.write(f"\nUNEXPECTED ERROR: {str(e)}\n")
                    print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    initial_files = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            for path in glob.glob(arg, recursive=True):
                if os.path.isfile(path):
                    initial_files.append(os.path.abspath(path))
    root = tk.Tk()
    app = KokoroGUI(root, initial_files)
    root.mainloop()
