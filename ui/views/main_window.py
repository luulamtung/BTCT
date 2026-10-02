"""Cửa sổ chính của ứng dụng BTCT."""

from PySide6.QtWidgets import QMainWindow
from ui.views.beam_view import BeamView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "PHẦN MỀM THIẾT KẾ DẦM BTCT - TCVN 5574:2018 (MVP)"
        )
        self.resize(1000, 750)

        self.beam_view = BeamView()
        self.setCentralWidget(self.beam_view)