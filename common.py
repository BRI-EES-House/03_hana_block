import math
import dataclasses


@dataclasses.dataclass
class HanaBlockSpec:

    # 花ブロックの形状（四角形：square、円形：circle、三角形：triangle）
    type: str

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

    def __post_init__(self):

        # 花ブロックの開口面積を計算
        if self.type == 'square':
            self.area = self.width * self.height
        elif self.type == 'circle':
            self.area = math.pi * (self.radius ** 2)
        elif self.type == 'triangle':
            (ax, ay) = self.points['peak_a']
            (bx, by) = self.points['peak_b']
            (cx, cy) = self.points['peak_c']
            self.area = 1/2 * abs((cx - ax) * (by - ay) - (bx - ax) * (by - ay))
        else:
            raise ValueError('花ブロックのタイプ「' + self.type + '」は対象外です')


def get_surface_albedo() -> float:
    """
    :return: 地面の日射反射率（アルベド）, -
    """
    return 0.2


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
