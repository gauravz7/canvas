import sys
import os

try:
    import canvas_module
    import canvas_module.executors.audio_executor as ae
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

print("Executable:", sys.executable)
print("CWD:", os.getcwd())
print("Path:", sys.path)
print("Canvas Module File:", canvas_module.__file__)
print("Audio Executor File:", ae.__file__)
