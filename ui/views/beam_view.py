"""
Giao diện nhập liệu, tính toán dầm và xuất báo cáo Word.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit,
    QMessageBox, QFileDialog, QGroupBox
)
from PySide6.QtGui import QFont

from core.materials import ConcreteGrade, RebarGrade
from core.calculations.beam import calculate_beam
from reporters.word_reporter import export_word_report

class BeamView(QWidget):
    def __init__(self):
        super().__init__()
        self.calc_result = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Panel trái: Nhập thông tin & Dữ liệu kỹ thuật
        left_panel = QVBoxLayout()
        
        # 1. Thông tin chung
        grp_info = QGroupBox("1. Thông tin dự án")
        grid_info = QGridLayout(grp_info)
        self.txt_project = QLineEdit("Công trình Nhà dân dụng 4 tầng")
        self.txt_item = QLineEdit("Dầm D1 trục 2 (200x400)")
        self.txt_designer = QLineEdit("Kỹ sư Kết cấu")
        grid_info.addWidget(QLabel("Dự án:"), 0, 0)
        grid_info.addWidget(self.txt_project, 0, 1)
        grid_info.addWidget(QLabel("Cấu kiện:"), 1, 0)
        grid_info.addWidget(self.txt_item, 1, 1)
        grid_info.addWidget(QLabel("Kỹ sư:"), 2, 0)
        grid_info.addWidget(self.txt_designer, 2, 1)
        left_panel.addWidget(grp_info)

        # 2. Tiết diện & Lực
        grp_geom = QGroupBox("2. Kích thước & Nội lực")
        grid_geom = QGridLayout(grp_geom)
        self.txt_b = QLineEdit("200")
        self.txt_h = QLineEdit("400")
        self.txt_a = QLineEdit("35")
        self.txt_M = QLineEdit("75")
        self.txt_Q = QLineEdit("90")
        grid_geom.addWidget(QLabel("Bề rộng b (mm):"), 0, 0)
        grid_geom.addWidget(self.txt_b, 0, 1)
        grid_geom.addWidget(QLabel("Chiều cao h (mm):"), 1, 0)
        grid_geom.addWidget(self.txt_h, 1, 1)
        grid_geom.addWidget(QLabel("Lớp bảo vệ a (mm):"), 2, 0)
        grid_geom.addWidget(self.txt_a, 2, 1)
        grid_geom.addWidget(QLabel("Mô men M (kNm):"), 3, 0)
        grid_geom.addWidget(self.txt_M, 3, 1)
        grid_geom.addWidget(QLabel("Lực cắt Q (kN):"), 4, 0)
        grid_geom.addWidget(self.txt_Q, 4, 1)
        left_panel.addWidget(grp_geom)

        # 3. Vật liệu
        grp_mat = QGroupBox("3. Cấp độ bền vật liệu")
        grid_mat = QGridLayout(grp_mat)
        self.cb_concrete = QComboBox()
        self.cb_concrete.addItems(list(ConcreteGrade.DATA.keys()))
        self.cb_concrete.setCurrentText("B25")

        self.cb_steel = QComboBox()
        self.cb_steel.addItems(list(RebarGrade.DATA.keys()))
        self.cb_steel.setCurrentText("CB400-V")

        self.cb_stirrup = QComboBox()
        self.cb_stirrup.addItems(list(RebarGrade.DATA.keys()))
        self.cb_stirrup.setCurrentText("CB240-T")

        grid_mat.addWidget(QLabel("Bê tông:"), 0, 0)
        grid_mat.addWidget(self.cb_concrete, 0, 1)
        grid_mat.addWidget(QLabel("Thép dọc:"), 1, 0)
        grid_mat.addWidget(self.cb_steel, 1, 1)
        grid_mat.addWidget(QLabel("Thép đai:"), 2, 0)
        grid_mat.addWidget(self.cb_stirrup, 2, 1)
        left_panel.addWidget(grp_mat)

        # 4. Bố trí cốt thép
        grp_rebar = QGroupBox("4. Chọn & Bố trí cốt thép")
        grid_rebar = QGridLayout(grp_rebar)
        self.txt_n_bars = QLineEdit("3")
        self.txt_phi_bars = QLineEdit("18")
        self.txt_n_stirrup = QLineEdit("2")
        self.txt_phi_stirrup = QLineEdit("8")
        self.txt_s_stirrup = QLineEdit("100")

        grid_rebar.addWidget(QLabel("Số thanh thép dọc n:"), 0, 0)
        grid_rebar.addWidget(self.txt_n_bars, 0, 1)
        grid_rebar.addWidget(QLabel("Đường kính d (mm):"), 1, 0)
        grid_rebar.addWidget(self.txt_phi_bars, 1, 1)
        grid_rebar.addWidget(QLabel("Số nhánh đai:"), 2, 0)
        grid_rebar.addWidget(self.txt_n_stirrup, 2, 1)
        grid_rebar.addWidget(QLabel("Đường kính đai (mm):"), 3, 0)
        grid_rebar.addWidget(self.txt_phi_stirrup, 3, 1)
        grid_rebar.addWidget(QLabel("Bước đai s (mm):"), 4, 0)
        grid_rebar.addWidget(self.txt_s_stirrup, 4, 1)
        left_panel.addWidget(grp_rebar)

        # Nút thao tác
        self.btn_calc = QPushButton("TÍNH TOÁN & KIỂM TRA")
        self.btn_calc.setStyleSheet("background-color: #2E5B82; color: white; font-weight: bold; padding: 8px;")
        self.btn_calc.clicked.connect(self.run_calculation)
        left_panel.addWidget(self.btn_calc)

        self.btn_word = QPushButton("XUẤT THUYẾT MINH WORD")
        self.btn_word.setStyleSheet("background-color: #1E7E34; color: white; font-weight: bold; padding: 8px;")
        self.btn_word.clicked.connect(self.export_word)
        self.btn_word.setEnabled(False)
        left_panel.addWidget(self.btn_word)

        main_layout.addLayout(left_panel, stretch=1)

        # Panel phải: Kết quả & Vết công thức TCVN
        right_panel = QVBoxLayout()
        lbl_res = QLabel("KẾT QUẢ TÍNH TOÁN & TRUY VẾT CÔNG THỨC TCVN 5574:2018")
        lbl_res.setFont(QFont("Arial", 11, QFont.Bold))
        right_panel.addWidget(lbl_res)

        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setFont(QFont("Consolas", 10))
        right_panel.addWidget(self.txt_output)

        main_layout.addLayout(right_panel, stretch=2)

    def run_calculation(self):
        try:
            b = float(self.txt_b.text())
            h = float(self.txt_h.text())
            a = float(self.txt_a.text())
            M = float(self.txt_M.text())
            Q = float(self.txt_Q.text())
            B_grade = self.cb_concrete.currentText()
            rebar_grade = self.cb_steel.currentText()
            stirrup_grade = self.cb_stirrup.currentText()

            n_bars = int(self.txt_n_bars.text())
            phi_bar = float(self.txt_phi_bars.text())
            n_stirrup = int(self.txt_n_stirrup.text())
            phi_stirrup = float(self.txt_phi_stirrup.text())
            s_stirrup = float(self.txt_s_stirrup.text())

            res = calculate_beam(
                b, h, a, B_grade, rebar_grade, stirrup_grade, M, Q,
                n_bars, phi_bar, n_stirrup, phi_stirrup, s_stirrup
            )

            res['project_name'] = self.txt_project.text()
            res['structural_item'] = self.txt_item.text()
            res['designer'] = self.txt_designer.text()
            self.calc_result = res

            # Hiển thị minh bạch lên giao diện
            out = []
            out.append("=== KẾT QUẢ TÍNH TOÁN DẦM BTCT ===")
            out.append(f"Khả năng chịu UỐN: {res['status_rebar_flex']}")
            out.append(f"  + As yêu cầu = {res['As_yc']:.1f} mm² (alpha_m = {res['alpha_m']:.4f} <= alpha_R = {res['alpha_R']:.4f})")
            out.append(f"  + As bố trí = {res['As_chon']:.1f} mm² ({res['n_bars']}Φ{res['phi_bar']:.0f})")
            out.append(f"  + Hàm lượng μ = {res['mu_chon']:.2f}%")
            out.append(f"\nKhả năng chịu CẮT: {res['status_shear']}")
            out.append(f"  + Lực cắt tính toán Q = {res['Q_kN']:.1f} kN")
            out.append(f"  + Khả năng chịu lực cắt [Q] = {res['Q_capacity_kN']:.1f} kN")
            out.append(f"  + Cốt đai: {res['n_stirrup']} nhánh Φ{res['phi_stirrup']:.0f}a{res['s_stirrup']:.0f}")

            out.append("\n" + "="*50)
            out.append("VẾT TÍNH TOÁN GIẢI TÍCH (TCVN 5574:2018):")
            out.append("\n--- CHỊU UỐN ---")
            out.extend(res['flex_trace'])
            out.append("\n--- CHỊU CẮT ---")
            out.extend(res['shear_trace'])

            self.txt_output.setText("\n".join(out))
            self.btn_word.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi dữ liệu", str(e))

    def export_word(self):
        if not self.calc_result:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu thuyết minh", "Bao_Cao_Tinh_Toan_Dam.docx", "Word Documents (*.docx)")
        if file_path:
            try:
                export_word_report(self.calc_result, template_path="template.docx", output_path=file_path)
                QMessageBox.information(self, "Thành công", f"Đã xuất thuyết minh thành công ra file:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi xuất file", str(e))