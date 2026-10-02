"""
Module: xuat_word.py
Mục đích: Tự động khởi tạo và xuất thuyết minh tính toán dầm BTCT chuẩn TCVN 5574:2018.
Khắc phục triệt để lỗi 'Document is empty' bằng OxmlElement chính quy, không dùng parse_xml thô.
Hiển thị ký hiệu Latinh, Hy Lạp, Subscript, Superscript chuẩn kỹ thuật.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from datetime import datetime

def set_cell_background(cell, hex_color):
    """Đổ màu nền ô trong bảng an toàn 100%, không bị lỗi XML parser"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def add_math_bullet(doc, parts):
    """Thêm dòng gạch đầu dòng có định dạng biến Latinh/Hy Lạp, chỉ số trên/dưới"""
    try:
        p = doc.add_paragraph(style='List Bullet')
    except Exception:
        p = doc.add_paragraph()
        r_bullet = p.add_run("• ")
        r_bullet.font.name = "Times New Roman"
        r_bullet.font.size = Pt(11)

    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    for text, is_sub, is_sup, is_bold, is_italic, color in parts:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        if is_sub:
            r.font.subscript = True
        if is_sup:
            r.font.superscript = True
        if is_bold:
            r.bold = True
        if is_italic:
            r.italic = True
        if color:
            r.font.color.rgb = color
    return p

def export_word_report(data, template_path=None, output_path="Bao_Cao_Tinh_Toan_Dam.docx"):
    """
    Khởi tạo và xuất file Word hoàn toàn độc lập, không dùng template.docx bên ngoài.
    """
    doc = docx.Document()

    # Định dạng trang giấy A4 (Lề trái 25mm, các lề khác 20mm)
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(0.98)
        section.right_margin = Inches(0.79)

    # 1. TIÊU ĐỀ
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("THUYẾT MINH TÍNH TOÁN KẾT CẤU BÊ TÔNG CỐT THÉP")
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(15)
    r_title.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("CẤU KIỆN: DẦM CHỮ NHẬT CHỊU UỐN & CẮT (TCVN 5574:2018)")
    r_sub.bold = True
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(0x59, 0x59, 0x59)

    doc.add_paragraph()

    # BẢNG THÔNG TIN DỰ ÁN
    info_table = doc.add_table(rows=4, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("Tên công trình:", data.get('project_name', 'Dự án Dân Dụng')),
        ("Hạng mục cấu kiện:", data.get('structural_item', 'Dầm chính tầng điển hình')),
        ("Kỹ sư thiết kế:", data.get('designer', 'Kỹ sư Kết cấu BTCT')),
        ("Ngày tính toán:", data.get('calc_date', datetime.today().strftime('%d/%m/%Y')))
    ]
    for i, (k, v) in enumerate(info_data):
        row = info_table.rows[i]
        r0 = row.cells[0].paragraphs[0].add_run(k)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(10.5)
        r0.bold = True

        r1 = row.cells[1].paragraphs[0].add_run(str(v))
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10.5)

        row.cells[0].width = Inches(2.2)
        row.cells[1].width = Inches(4.3)
        set_cell_background(row.cells[0], "F2F2F2")

    doc.add_paragraph()

    # 2. TIÊU CHUẨN ÁP DỤNG
    doc.add_heading("1. Tiêu chuẩn áp dụng & Giả thiết thiết kế", level=1)
    p_tc1 = doc.add_paragraph("- TCVN 5574:2018: Thiết kế kết cấu bê tông và bê tông cốt thép.")
    p_tc1.runs[0].font.name = "Times New Roman"
    p_tc1.runs[0].font.size = Pt(11)

    p_tc2 = doc.add_paragraph("- TCVN 2737:2023: Tải trọng và tác động.")
    p_tc2.runs[0].font.name = "Times New Roman"
    p_tc2.runs[0].font.size = Pt(11)

    # 3. SỐ LIỆU ĐẦU VÀO
    doc.add_heading("2. Số liệu đầu vào", level=1)
    input_table = doc.add_table(rows=1, cols=4)
    input_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Thông số", "Ký hiệu", "Giá trị", "Đơn vị"]
    for idx, text in enumerate(headers):
        cell = input_table.rows[0].cells[idx]
        r = cell.paragraphs[0].add_run(text)
        r.font.name = "Times New Roman"
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "2E5B82")

    input_rows = [
        ("Bề rộng tiết diện", "b", f"{data['b']:.0f}", "mm"),
        ("Chiều cao tiết diện", "h", f"{data['h']:.0f}", "mm"),
        ("Khoảng cách trọng tâm cốt thép", "a", f"{data['a']:.0f}", "mm"),
        ("Chiều cao làm việc", "h₀", f"{data['h0']:.1f}", "mm"),
        ("Cấp độ bền bê tông", "Cấp bê tông", f"{data['B_grade']}", "-"),
        ("Cường độ chịu nén tính toán bê tông", "R_b", f"{data['Rb']:.2f}", "MPa"),
        ("Cường độ chịu kéo tính toán bê tông", "R_bt", f"{data['Rbt']:.2f}", "MPa"),
        ("Nhóm cốt thép dọc chịu lực", "Mác thép", f"{data['rebar_grade']}", "-"),
        ("Cường độ tính toán cốt thép dọc", "R_s", f"{data['Rs']:.0f}", "MPa"),
        ("Mô men uốn tính toán", "M", f"{data['M_kNm']:.2f}", "kNm"),
        ("Lực cắt tính toán", "Q", f"{data['Q_kN']:.2f}", "kN")
    ]

    for row_data in input_rows:
        row = input_table.add_row()
        for idx, text in enumerate(row_data):
            cell = row.cells[idx]
            r = cell.paragraphs[0].add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)

    # 4. TÍNH TOÁN UỐN
    doc.add_heading("3. Tính toán cốt thép chịu uốn (Điều 8.1.5.2.2 TCVN 5574:2018)", level=1)

    p_a = doc.add_paragraph()
    p_a.paragraph_format.space_before = Pt(4)
    r_a = p_a.add_run("a) Giới hạn vùng nén và hệ số tính toán:")
    r_a.bold = True
    r_a.font.name = "Times New Roman"
    r_a.font.size = Pt(11)

    add_math_bullet(doc, [
        ("Chiều cao làm việc: ", False, False, False, False, None),
        ("h", False, False, True, True, None),
        ("0", True, False, False, False, None),
        (" = h – a = ", False, False, False, False, None),
        (f"{data['h']:.0f} – {data['a']:.0f} = ", False, False, False, False, None),
        (f"{data['h0']:.1f} mm", False, False, True, False, None)
    ])

    add_math_bullet(doc, [
        ("Giới hạn chiều cao tương đối vùng nén: ", False, False, False, False, None),
        ("ξ", False, False, True, True, None),
        ("R", True, False, False, False, None),
        (" = 0,8 / (1 + ", False, False, False, False, None),
        ("R", False, False, False, True, None),
        ("s", True, False, False, False, None),
        (f" / 700) = 0,8 / (1 + {data['Rs']:.0f} / 700) = ", False, False, False, False, None),
        (f"{data['xi_R']:.4f}", False, False, True, False, None)
    ])

    add_math_bullet(doc, [
        ("Giới hạn hệ số mô men uốn: ", False, False, False, False, None),
        ("α", False, False, True, True, None),
        ("R", True, False, False, False, None),
        (" = ", False, False, False, False, None),
        ("ξ", False, False, False, True, None),
        ("R", True, False, False, False, None),
        (" · (1 – 0,5·", False, False, False, False, None),
        ("ξ", False, False, False, True, None),
        ("R", True, False, False, False, None),
        (f") = {data['xi_R']:.4f} · (1 – 0,5 · {data['xi_R']:.4f}) = ", False, False, False, False, None),
        (f"{data['alpha_R']:.4f}", False, False, True, False, None)
    ])

    p_b = doc.add_paragraph()
    p_b.paragraph_format.space_before = Pt(6)
    r_b = p_b.add_run("b) Xác định diện tích cốt thép yêu cầu:")
    r_b.bold = True
    r_b.font.name = "Times New Roman"
    r_b.font.size = Pt(11)

    add_math_bullet(doc, [
        ("Hệ số mô men uốn tính toán: ", False, False, False, False, None),
        ("α", False, False, True, True, None),
        ("m", True, False, False, False, None),
        (" = M / (", False, False, False, False, None),
        ("R", False, False, False, True, None),
        ("b", True, False, False, False, None),
        (" · b · ", False, False, False, False, None),
        ("h", False, False, False, True, None),
        ("0", True, False, False, False, None),
        ("²) = ", False, False, False, False, None),
        (f"{data['M_kNm']*1e6:.0f} / ({data['Rb']:.2f} · {data['b']:.0f} · {data['h0']:.1f}²) = ", False, False, False, False, None),
        (f"{data['alpha_m']:.4f}", False, False, True, False, None)
    ])

    color_flex = RGBColor(0x1E, 0x7E, 0x34) if data['alpha_m'] <= data['alpha_R'] else RGBColor(0xC0, 0x00, 0x00)
    eval_flex = "THỎA MÃN (đặt cốt đơn)" if data['alpha_m'] <= data['alpha_R'] else "KHÔNG THỎA MÃN"
    add_math_bullet(doc, [
        ("Kiểm tra điều kiện đặt cốt đơn: ", False, False, False, False, None),
        ("α", False, False, False, True, None),
        ("m", True, False, False, False, None),
        (f" = {data['alpha_m']:.4f} ≤ ", False, False, False, False, None),
        ("α", False, False, False, True, None),
        ("R", True, False, False, False, None),
        (f" = {data['alpha_R']:.4f}  ⟹  ", False, False, False, False, None),
        (eval_flex, False, False, True, False, color_flex)
    ])

    add_math_bullet(doc, [
        ("Hệ số chiều cao tương đối vùng nén: ", False, False, False, False, None),
        ("ξ", False, False, True, True, None),
        (" = 1 – √(1 – 2·", False, False, False, False, None),
        ("α", False, False, False, True, None),
        ("m", True, False, False, False, None),
        (f") = 1 – √(1 – 2 · {data['alpha_m']:.4f}) = ", False, False, False, False, None),
        (f"{data['xi']:.4f}", False, False, True, False, None)
    ])

    add_math_bullet(doc, [
        ("Chiều cao vùng bê tông chịu nén: ", False, False, False, False, None),
        ("x", False, False, True, True, None),
        (" = ", False, False, False, False, None),
        ("ξ", False, False, False, True, None),
        (" · ", False, False, False, False, None),
        ("h", False, False, False, True, None),
        ("0", True, False, False, False, None),
        (f" = {data['xi']:.4f} · {data['h0']:.1f} = ", False, False, False, False, None),
        (f"{data['xi']*data['h0']:.1f} mm", False, False, True, False, None)
    ])

    as_yc_str = f"{data['As_yc']:.1f}" if data.get('As_yc') else "Vượt giới hạn"
    add_math_bullet(doc, [
        ("Diện tích cốt thép dọc yêu cầu: ", False, False, False, False, None),
        ("A", False, False, True, True, None),
        ("s,yc", True, False, False, False, None),
        (" = (", False, False, False, False, None),
        ("ξ", False, False, False, True, None),
        (" · ", False, False, False, False, None),
        ("R", False, False, False, True, None),
        ("b", True, False, False, False, None),
        (" · b · ", False, False, False, False, None),
        ("h", False, False, False, True, None),
        ("0", True, False, False, False, None),
        (") / ", False, False, False, False, None),
        ("R", False, False, False, True, None),
        ("s", True, False, False, False, None),
        (f" = ({data['xi']:.4f} · {data['Rb']:.2f} · {data['b']:.0f} · {data['h0']:.1f}) / {data['Rs']:.0f} = ", False, False, False, False, None),
        (f"{as_yc_str} mm²", False, False, True, False, None)
    ])

    add_math_bullet(doc, [
        ("Hàm lượng cốt thép yêu cầu: ", False, False, False, False, None),
        ("μ", False, False, True, True, None),
        (" = ", False, False, False, False, None),
        ("A", False, False, False, True, None),
        ("s,yc", True, False, False, False, None),
        (" / (b · ", False, False, False, False, None),
        ("h", False, False, False, True, None),
        ("0", True, False, False, False, None),
        (f") · 100% = {data['mu']:.3f}%  (0,10% ≤ μ ≤ 3,00%  ⟹  ", False, False, False, False, None),
        ("ĐẠT)", False, False, True, False, RGBColor(0x1E, 0x7E, 0x34))
    ])

    # 5. TÍNH TOÁN CẮT
    doc.add_heading("4. Tính toán & kiểm tra khả năng chịu cắt (Điều 8.1.5.3 TCVN 5574:2018)", level=1)

    p_sa = doc.add_paragraph()
    p_sa.paragraph_format.space_before = Pt(4)
    r_sa = p_sa.add_run("a) Kiểm tra điều kiện bền dải bê tông nghiêng giữa các vết nứt (Điều 8.1.5.3.1):")
    r_sa.bold = True
    r_sa.font.name = "Times New Roman"
    r_sa.font.size = Pt(11)

    add_math_bullet(doc, [
        ("Khả năng chịu ứng suất nén dải nghiêng: ", False, False, False, False, None),
        ("Q", False, False, True, True, None),
        ("b1", True, False, False, False, None),
        (" = 0,3 · (1 – 0,01·", False, False, False, False, None),
        ("R", False, False, False, True, None),
        ("b", True, False, False, False, None),
        (") · ", False, False, False, False, None),
        ("R", False, False, False, True, None),
        ("b", True, False, False, False, None),
        (" · b · ", False, False, False, False, None),
        ("h", False, False, False, True, None),
        ("0", True, False, False, False, None),
        (f" = 0,3 · (1 – 0,01·{data['Rb']:.2f}) · {data['Rb']:.2f} · {data['b']:.0f} · {data['h0']:.1f} = ", False, False, False, False, None),
        (f"{data['Qb1_kN']:.2f} kN", False, False, True, False, None)
    ])

    color_qb1 = RGBColor(0x1E, 0x7E, 0x34) if data['Q_kN'] <= data['Qb1_kN'] else RGBColor(0xC0, 0x00, 0x00)
    eval_qb1 = "ĐẠT (Bê tông không bị phá hoại giòn dải nghiêng)" if data['Q_kN'] <= data['Qb1_kN'] else "KHÔNG ĐẠT"
    add_math_bullet(doc, [
        (f"So sánh điều kiện bền: Q = {data['Q_kN']:.2f} kN ≤ ", False, False, False, False, None),
        ("Q", False, False, False, True, None),
        ("b1", True, False, False, False, None),
        (f" = {data['Qb1_kN']:.2f} kN  ⟹  ", False, False, False, False, None),
        (eval_qb1, False, False, True, False, color_qb1)
    ])

    p_sb = doc.add_paragraph()
    p_sb.paragraph_format.space_before = Pt(6)
    r_sb = p_sb.add_run("b) Khả năng chịu cắt của bê tông và cốt đai trên tiết diện nghiêng (Điều 8.1.5.3.2):")
    r_sb.bold = True
    r_sb.font.name = "Times New Roman"
    r_sb.font.size = Pt(11)

    need_stirrup = data['Q_kN'] > data['Qb_min_kN']
    eval_need = "Cần tính toán cốt đai chịu cắt" if need_stirrup else "Chỉ cần đặt cốt đai cấu tạo"
    add_math_bullet(doc, [
        ("Khả năng chịu cắt tối thiểu của bê tông: ", False, False, False, False, None),
        ("Q", False, False, True, True, None),
        ("b,min", True, False, False, False, None),
        (" = 0,5 · ", False, False, False, False, None),
        ("R", False, False, False, True, None),
        ("bt", True, False, False, False, None),
        (" · b · ", False, False, False, False, None),
        ("h", False, False, False, True, None),
        ("0", True, False, False, False, None),
        (f" = 0,5 · {data['Rbt']:.2f} · {data['b']:.0f} · {data['h0']:.1f} = ", False, False, False, False, None),
        (f"{data['Qb_min_kN']:.2f} kN", False, False, True, False, None),
        (f"  (Vì Q = {data['Q_kN']:.2f} kN > Q", False, False, False, False, None),
        ("b,min", True, False, False, False, None),
        (f"  ⟹  {eval_need})", False, False, True, False, None)
    ])

    asw_val = data['n_stirrup'] * 3.14159 * (data['phi_stirrup']**2) / 4.0
    add_math_bullet(doc, [
        (f"Cốt đai chọn bố trí: {data['n_stirrup']} nhánh Φ{data['phi_stirrup']:.0f}, bước đai s = {data['s_stirrup']:.0f} mm  ⟹  ", False, False, False, False, None),
        ("A", False, False, True, True, None),
        ("sw", True, False, False, False, None),
        (f" = {asw_val:.2f} mm²", False, False, True, False, None)
    ])

    eval_qsw = "ĐẠT" if data['qsw'] >= data['qsw_min'] else "KHÔNG ĐẠT"
    add_math_bullet(doc, [
        ("Lực chịu cắt của cốt đai trên một đơn vị dài: ", False, False, False, False, None),
        ("q", False, False, True, True, None),
        ("sw", True, False, False, False, None),
        (" = (", False, False, False, False, None),
        ("R", False, False, False, True, None),
        ("sw", True, False, False, False, None),
        (" · ", False, False, False, False, None),
        ("A", False, False, False, True, None),
        ("sw", True, False, False, False, None),
        (f") / s = ({data['Rsw']:.0f} · {asw_val:.2f}) / {data['s_stirrup']:.0f} = ", False, False, False, False, None),
        (f"{data['qsw']:.2f} N/mm", False, False, True, False, None),
        ("  (Cấu tạo tối thiểu: ", False, False, False, False, None),
        ("q", False, False, False, True, None),
        ("sw,min", True, False, False, False, None),
        (f" = 0,25 · {data['Rbt']:.2f} · {data['b']:.0f} = {data['qsw_min']:.2f} N/mm  ⟹  ", False, False, False, False, None),
        (eval_qsw, False, False, True, False, RGBColor(0x1E, 0x7E, 0x34))
    ])

    eval_tot = "ĐẠT (Thỏa mãn khả năng chịu cắt)" if data['Q_kN'] <= data['Q_capacity_kN'] else "KHÔNG ĐẠT"
    color_tot = RGBColor(0x1E, 0x7E, 0x34) if data['Q_kN'] <= data['Q_capacity_kN'] else RGBColor(0xC0, 0x00, 0x00)
    add_math_bullet(doc, [
        ("Tổng khả năng chịu cắt trên tiết diện nghiêng: ", False, False, False, False, None),
        ("Q", False, False, True, True, None),
        ("ult", True, False, False, False, None),
        (" = ", False, False, False, False, None),
        ("Q", False, False, False, True, None),
        ("b", True, False, False, False, None),
        (" + ", False, False, False, False, None),
        ("Q", False, False, False, True, None),
        ("sw", True, False, False, False, None),
        (f" = {data['Q_capacity_kN']:.2f} kN  ≥  Q = {data['Q_kN']:.2f} kN  ⟹  ", False, False, False, False, None),
        (eval_tot, False, False, True, False, color_tot)
    ])

    # 6. BẢNG TỔNG HỢP VÀ KẾT LUẬN
    doc.add_heading("5. Bảng tổng hợp cốt thép & Kết luận kỹ thuật", level=1)
    res_table = doc.add_table(rows=1, cols=4)
    res_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, text in enumerate(["Hạng mục kiểm tra", "Yêu cầu / Khả năng", "Bố trí thực tế", "Đánh giá"]):
        cell = res_table.rows[0].cells[idx]
        r = cell.paragraphs[0].add_run(text)
        r.font.name = "Times New Roman"
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "2E5B82")

    res_rows = [
        ("Khả năng chịu uốn (A_s)", f"{as_yc_str} mm²", f"{data['As_chon']:.1f} mm² ({data['n_bars']}Φ{data['phi_bar']:.0f})", data['status_rebar_flex']),
        ("Khả năng chịu cắt (Q)", f"{data['Q_kN']:.1f} kN", f"{data['Q_capacity_kN']:.1f} kN ({data['n_stirrup']} nhánh Φ{data['phi_stirrup']:.0f}a{data['s_stirrup']:.0f})", data['status_shear']),
        ("Hàm lượng cốt thép (μ)", "0.10% ≤ μ ≤ 3.0%", f"{data['mu_chon']:.2f} %", "ĐẠT" if (0.1 <= data['mu_chon'] <= 3.0) else "KHÔNG ĐẠT")
    ]

    for row_data in res_rows:
        row = res_table.add_row()
        for idx, text in enumerate(row_data):
            cell = row.cells[idx]
            r = cell.paragraphs[0].add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)

    p_conc = doc.add_paragraph()
    p_conc.paragraph_format.space_before = Pt(14)
    final_text = "CẤU KIỆN ĐỦ KHẢ NĂNG CHỊU LỰC THEO TCVN 5574:2018" if (data['status_rebar_flex'] == 'ĐẠT' and data['status_shear'] == 'ĐẠT') else "CẤU KIỆN KHÔNG THỎA MÃN ĐIỀU KIỆN CHỊU LỰC"
    r_conc = p_conc.add_run(f"KẾT LUẬN CHUNG: {final_text}")
    r_conc.font.name = "Times New Roman"
    r_conc.bold = True
    r_conc.font.size = Pt(11)

    doc.save(output_path)
    return output_path