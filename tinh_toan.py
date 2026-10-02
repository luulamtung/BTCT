"""
Module: tinh_toan.py
Mục đích: Tính toán và kiểm tra dầm BTCT tiết diện chữ nhật theo TCVN 5574:2018
Đơn vị quy ước:
  - Chiều dài: mm
  - Diện tích: mm2
  - Lực: N (nhập/xuất hiển thị: kN)
  - Mô men: Nmm (nhập/xuất hiển thị: kNm)
  - Cường độ: MPa (N/mm2)
"""

import math

class ConcreteGrade:
    # TCVN 5574:2018 - Bảng 6 & Bảng 7 (MPa = N/mm2)
    DATA = {
        'B15': {'Rb': 8.5,  'Rbt': 0.75, 'Eb': 24000},
        'B20': {'Rb': 11.5, 'Rbt': 0.90, 'Eb': 27500},
        'B25': {'Rb': 14.5, 'Rbt': 1.05, 'Eb': 30000},
        'B30': {'Rb': 17.0, 'Rbt': 1.15, 'Eb': 32500},
        'B35': {'Rb': 19.5, 'Rbt': 1.30, 'Eb': 34500},
        'B40': {'Rb': 22.0, 'Rbt': 1.40, 'Eb': 36000}
    }

class RebarGrade:
    # TCVN 5574:2018 - Bảng 13 & Bảng 14 (MPa = N/mm2)
    DATA = {
        'CB240-T': {'Rs': 210, 'Rsc': 210, 'Rsw': 170},
        'CB300-T': {'Rs': 260, 'Rsc': 260, 'Rsw': 210},
        'CB300-V': {'Rs': 260, 'Rsc': 260, 'Rsw': 210},
        'CB400-V': {'Rs': 350, 'Rsc': 350, 'Rsw': 280},
        'CB500-V': {'Rs': 435, 'Rsc': 435, 'Rsw': 300}
    }

def calculate_beam(b, h, a, B_grade, rebar_grade, stirrup_grade, M_kNm, Q_kN, 
                   n_bars, phi_bar, n_stirrup, phi_stirrup, s_stirrup):
    """
    Tính toán kiểm tra dầm chịu uốn và cắt theo TCVN 5574:2018.
    """
    # 1. Kiểm tra tính hợp lệ dữ liệu đầu vào (Input Validation)
    if b <= 0 or h <= 0 or a <= 0:
        raise ValueError("Kích thước tiết diện (b, h, a) phải lớn hơn 0.")
    if a >= h:
        raise ValueError("Chiều dày lớp bảo vệ a phải nhỏ hơn chiều cao h.")
    if M_kNm < 0 or Q_kN < 0:
        raise ValueError("Mô men M và lực cắt Q phải lớn hơn hoặc bằng 0.")
    if n_bars <= 0 or phi_bar <= 0 or n_stirrup <= 0 or phi_stirrup <= 0 or s_stirrup <= 0:
        raise ValueError("Thông số cốt thép bố trí không hợp lệ.")

    h0 = h - a
    M_Nmm = M_kNm * 1e6
    Q_N = Q_kN * 1e3

    c_props = ConcreteGrade.DATA[B_grade]
    s_props = RebarGrade.DATA[rebar_grade]
    w_props = RebarGrade.DATA[stirrup_grade]

    Rb = c_props['Rb']
    Rbt = c_props['Rbt']
    Rs = s_props['Rs']
    Rsw = w_props['Rsw']

    flex_trace = []
    shear_trace = []

    # 2. TÍNH TOÁN UỐN (Điều 8.1.5.2.2 TCVN 5574:2018)
    # Xác định giới hạn vùng nén xi_R và alpha_R
    xi_R = 0.8 / (1.0 + Rs / 700.0)
    alpha_R = xi_R * (1.0 - 0.5 * xi_R)
    
    alpha_m = M_Nmm / (Rb * b * (h0 ** 2))

    flex_trace.append("a) Xác định thông số giới hạn vùng nén:")
    flex_trace.append(f"- Chiều cao làm việc: h0 = h - a = {h:.0f} - {a:.0f} = {h0:.1f} mm")
    flex_trace.append(f"- Giới hạn vùng nén: xi_R = 0.8 / (1 + Rs/700) = 0.8 / (1 + {Rs}/700) = {xi_R:.4f}")
    flex_trace.append(f"- Hệ số alpha_R = xi_R * (1 - 0.5*xi_R) = {alpha_R:.4f}")
    flex_trace.append(f"- Hệ số alpha_m = M / (Rb * b * h0^2) = {M_Nmm:.0f} / ({Rb} * {b:.0f} * {h0:.1f}^2) = {alpha_m:.5f}")

    if alpha_m > alpha_R:
        status_flex = "KHÔNG ĐẠT (alpha_m > alpha_R: Tiết diện quá bé, cần tăng h hoặc đặt cốt kép)"
        xi = None
        As_yc = None
        mu = None
    else:
        status_flex = "ĐẠT"
        xi = 1.0 - math.sqrt(1.0 - 2.0 * alpha_m)
        x = xi * h0
        As_yc = (xi * Rb * b * h0) / Rs
        mu = (As_yc / (b * h0)) * 100.0
        flex_trace.append(f"- Hệ số chiều cao vùng nén: xi = 1 - sqrt(1 - 2*{alpha_m:.5f}) = {xi:.5f}")
        flex_trace.append(f"- Chiều cao vùng nén: x = xi * h0 = {x:.2f} mm")
        flex_trace.append(f"- Diện tích cốt thép yêu cầu: As_yc = (xi * Rb * b * h0) / Rs = {As_yc:.2f} mm²")
        flex_trace.append(f"- Hàm lượng cốt thép yêu cầu: mu = {mu:.3f}% (Quy định: mu_min = 0.10% <= mu <= mu_max = 3.0%)")

    # Kiểm tra thép chọn uốn
    As_chon = n_bars * math.pi * (phi_bar ** 2) / 4.0
    mu_chon = (As_chon / (b * h0)) * 100.0
    if As_yc is not None and As_chon >= As_yc:
        status_rebar_flex = "ĐẠT"
    else:
        status_rebar_flex = "KHÔNG ĐẠT"

    # 3. TÍNH TOÁN CẮT (Điều 8.1.5.3 TCVN 5574:2018)
    # 3.1. Kiểm tra dải bê tông nghiêng giữa các vết nứt (Điều 8.1.5.3.1 - CT 8.54)
    phi_b1 = 1.0 - 0.01 * Rb
    Qb1 = 0.3 * phi_b1 * Rb * b * h0 # N
    Qb1_kN = Qb1 / 1e3

    shear_trace.append("a) Kiểm tra dải bê tông nghiêng giữa các vết nứt (Điều 8.1.5.3.1):")
    shear_trace.append(f"- Qb1 = 0.3 * (1 - 0.01*{Rb}) * {Rb} * {b:.0f} * {h0:.1f} = {Qb1_kN:.2f} kN")
    if Q_kN > Qb1_kN:
        status_shear_b1 = "KHÔNG ĐẠT (Bê tông dải nghiêng bị phá hoại giòn ép vỡ -> Cần tăng tiết diện)"
    else:
        status_shear_b1 = "ĐẠT"

    # 3.2. Kiểm tra khả năng chịu cắt trên tiết diện nghiêng (Điều 8.1.5.3.2)
    Qb_min = 0.5 * Rbt * b * h0 # N
    Qb_min_kN = Qb_min / 1e3

    Asw = n_stirrup * math.pi * (phi_stirrup ** 2) / 4.0
    qsw = (Rsw * Asw) / s_stirrup # N/mm
    qsw_min = 0.25 * Rbt * b # Cấu tạo tối thiểu CT 8.63

    # Vết nứt nghiêng bất lợi: C = 2*h0
    C = 2.0 * h0
    Qb = (1.5 * Rbt * b * (h0 ** 2)) / C
    Qsw = 0.75 * qsw * C
    Q_capacity = (Qb + Qsw) / 1e3 # kN

    shear_trace.append("b) Khả năng chịu cắt trên tiết diện nghiêng (Điều 8.1.5.3.2):")
    shear_trace.append(f"- Qb_min = 0.5 * {Rbt} * {b:.0f} * {h0:.1f} = {Qb_min_kN:.2f} kN")
    shear_trace.append(f"- Cốt đai chọn: {n_stirrup} nhánh Φ{phi_stirrup}, s = {s_stirrup} mm -> Asw = {Asw:.2f} mm², qsw = {qsw:.2f} N/mm")
    shear_trace.append(f"- Điều kiện chống nứt đai tối thiểu: qsw = {qsw:.2f} N/mm so với qsw_min = {qsw_min:.2f} N/mm")
    shear_trace.append(f"- Khả năng chịu lực cắt: Q_ult = Qb + Qsw = {Qb/1e3:.2f} + {Qsw/1e3:.2f} = {Q_capacity:.2f} kN so với Q = {Q_kN:.2f} kN")

    if Q_kN <= Q_capacity and status_shear_b1 == "ĐẠT" and qsw >= qsw_min:
        status_shear = "ĐẠT"
    else:
        status_shear = "KHÔNG ĐẠT"

    return {
        'b': b, 'h': h, 'a': a, 'h0': h0,
        'B_grade': B_grade, 'Rb': Rb, 'Rbt': Rbt,
        'rebar_grade': rebar_grade, 'Rs': Rs,
        'stirrup_grade': stirrup_grade, 'Rsw': Rsw,
        'M_kNm': M_kNm, 'Q_kN': Q_kN,
        'n_bars': n_bars, 'phi_bar': phi_bar,
        'n_stirrup': n_stirrup, 'phi_stirrup': phi_stirrup, 's_stirrup': s_stirrup,
        'xi_R': xi_R, 'alpha_R': alpha_R, 'alpha_m': alpha_m,
        'xi': xi, 'As_yc': As_yc, 'mu': mu,
        'As_chon': As_chon, 'mu_chon': mu_chon,
        'status_flex': status_flex, 'status_rebar_flex': status_rebar_flex,
        'Qb1_kN': Qb1_kN, 'Qb_min_kN': Qb_min_kN, 'Q_capacity_kN': Q_capacity,
        'qsw': qsw, 'qsw_min': qsw_min, 'status_shear': status_shear,
        'flex_trace': flex_trace, 'shear_trace': shear_trace
    }