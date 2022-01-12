import math
import dataclasses


@dataclasses.dataclass
class HanaBlock:

    # 花ブロック開口部の仕様
    opening_specs: list = dataclasses.field(default_factory=list)

    # 花ブロックの開口部の数
    number_of_openings: int = 0

    # 花ブロックの奥行, mm
    depth: float = 0.0

    # 花ブロックの傾斜角, degree
    inclination_angle: float = 90.0

    # 花ブロックの方位角, degree
    azimuth_angle: float = 0.0

    # ブロック前面の幅, mm
    front_width: float = 0.0

    # ブロック前面の高さ, mm
    front_height: float = 0.0

    # ブロック前面の面積, mm2
    front_area: float = dataclasses.field(init=False)

    # # 花ブロック仕切り面積の比, -
    # partition_area_rate: float = dataclasses.field(init=False)

    def __post_init__(self):

        # ブロック前面の面積を計算
        self.front_area = self.front_width * self.front_height


@dataclasses.dataclass
class HanaBlockSpec:

    # 花ブロックの形状（四角形：square、円形：circle、三角形：triangle）
    type: str

    # 花ブロックの奥行, mm
    depth: float = 0.0

    # 花ブロックの傾斜角, degree
    inclination_angle: float = 90.0

    # 花ブロックの方位角, degree
    azimuth_angle: float = 0.0

    # 花ブロック開口部の幅,　mm
    width: float = 0.0

    # 花ブロック開口部の高さ,　mm
    height: float = 0.0

    # 花ブロック開口部の半径,　mm
    radius: float = 0.0

    # 花ブロック開口部の各頂点の座標
    points: dict = dataclasses.field(default_factory=dict)

    # 花ブロックの面積, mm2
    area: float = dataclasses.field(init=False)

    # 花ブロック開口部の周長, mm
    perimeter: float = dataclasses.field(init=False)

    # # ブロック前面の幅, mm
    # front_width: float = 0.0
    #
    # # ブロック前面の高さ, mm
    # front_height: float = 0.0
    #
    # # ブロック前面の面積, mm2
    # front_area: float = dataclasses.field(init=False)
    #
    # # 花ブロック仕切り面積の比, -
    # partition_area_rate: float = dataclasses.field(init=False)

    def __post_init__(self):

        # 花ブロックの開口面積、周長を計算、四角形、円形の場合は座標を設定
        if self.type == 'square':
            self.area = self.width * self.height
            self.points = {'peak_a': (0, 0), 'peak_b': (self.width, 0),
                           'peak_c': (self.width, self.height),  'peak_d': (0, self.height)}
            self.perimeter = (self.width + self.height) * 2
        elif self.type == 'circle':
            self.area = math.pi * (self.radius ** 2)
            self.points = {'peak_a': (self.radius, self.radius)}
            self.width = self.radius * 2
            self.height = self.radius * 2
            self.perimeter = math.pi * self.radius * 2
        elif self.type == 'triangle':
            (ax, ay) = self.points['peak_a']
            (bx, by) = self.points['peak_b']
            (cx, cy) = self.points['peak_c']
            self.area = 1/2 * abs((cx - ax) * (by - ay) - (bx - ax) * (by - ay))
            self.width = max(ax, bx, cx)
            self.height = max(ay, by, cy)
            self.perimeter = math.sqrt((ax - bx) ** 2 + (ay - by) ** 2) + \
                             math.sqrt((bx - cx) ** 2 + (by - cy) ** 2) + \
                             math.sqrt((cx - ax) ** 2 + (cy - ay) ** 2)
        else:
            raise ValueError('花ブロックのタイプ「' + self.type + '」は対象外です')

        # # ブロック前面の面積を計算
        # self.front_area = self.front_width * self.front_height
        #
        # # 花ブロック仕切り面積の比を計算
        # self.partition_area_rate = (self.perimeter * self.depth) / (self.front_area * 2.0)


def get_error_value() -> float:
    """
    :return: 誤差値, -
    """
    return 0.0001


def get_surface_albedo() -> float:
    """
    :return: 地面の日射反射率（アルベド）, -
    """
    return 0.2


def get_direction_list() -> dict:
    """
    :return: 方位名称と方位角のリスト
    """
    directions = {
        'N': 180.0,
        'NE': -135.0,
        'E': -90.0,
        'SE': -45.0,
        'S': 0.0,
        'SW': 45.0,
        'W': 90.0,
        'NW': 135.0
    }
    return directions


def test():

    # 四角形の場合
    spec = HanaBlockSpec(type='square', width=130.0, height=130.0)
    print(spec.area)

    # 円形の場合
    spec = HanaBlockSpec(type='circle', radius=50.0)
    print(spec.area)

    # 三角形の場合
    spec = HanaBlockSpec(type='triangle', points={'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 0)})
    print(spec.area)


if __name__ == '__main__':

    test()
