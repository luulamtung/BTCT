"""
Bảng thông số vật liệu bê tông và cốt thép.
Đơn vị cường độ và mô đun đàn hồi: MPa (N/mm²).
"""

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