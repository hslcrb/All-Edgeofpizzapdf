import sys
import multiprocessing
import os
import tkinter as tk

# src 폴더 내부 모듈을 절대경로로 인식하도록 path 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.main_window import MainWindow

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MainWindow()
    app.mainloop()
