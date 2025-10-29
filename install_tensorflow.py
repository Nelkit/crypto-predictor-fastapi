import platform
import subprocess
import sys

system = platform.system()

if system == "Darwin":
    print("Installing TensorFlow for Mac (tensorflow-macos + tensorflow-metal)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow-macos", "tensorflow-metal"])
elif system == "Windows":
    print("Installing TensorFlow for Windows...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow"])
else:
    print("Unsupported OS for TensorFlow. Please install manually.")
