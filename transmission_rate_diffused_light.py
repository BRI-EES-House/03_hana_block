import numpy as np
import math
import statistics
import itertools
import common
import distance_point_shadow
import transmission_rate_base


def diffused_light_transmission_rate(spec: common.HanaBlockSpec) -> float:
    """
    四角形の花ブロックの拡散光の透過率を計算する

    :param spec:   花ブロックの仕様
    :return:四角形の花ブロックの拡散光の透過率[-]
    """

    # 各乱数の総当たりの組み合わせを設定
    random_numbers_cases = get_random_number_list()

    # 結果格納用の配列を用意
    rate_s = []

    for index, case in enumerate(random_numbers_cases):

        # 点の影の垂直方向、水平方向の移動距離を計算
        distance_vertical, distance_horizontal = distance_point_shadow.distance_of_points_shadow(
            spec=spec,
            sun_altitude=get_random_sun_altitude(case[0]),
            sun_azimuth_angle=get_random_sun_azimuth_angle(case[1])
        )

        # 透過率を計算
        if spec.type == 'square':
            buf_rate = transmission_rate_base.base_transmission_rate_square(
                spec=spec, distance_vertical=distance_vertical, distance_horizontal=distance_horizontal)
        elif spec.type == 'circle':
            buf_rate = transmission_rate_base.base_transmission_rate_circle(
                spec=spec, distance_vertical=distance_vertical, distance_horizontal=distance_horizontal)
        elif spec.type == 'triangle':
            buf_rate = transmission_rate_base.base_transmission_rate_triangle(
                spec=spec, distance_vertical=distance_vertical, distance_horizontal=distance_horizontal)
        else:
            raise ValueError('花ブロックのタイプ「' + spec.type + '」は対象外です')

        # 透過率を配列に追加
        rate_s.append(buf_rate)

    return statistics.mean(rate_s)


def get_random_number_list() -> list:
    """
    0～1の範囲の乱数の総当たりの組み合わせを設定する

    :param なし
    :return:乱数の総当たりの組み合わせ
    """

    # 乱数のステップ数を設定（総ケース数が10^4になるように設定）
    r_step = 1.0 / math.sqrt(10 ** 4)

    # 太陽高度を設定するための乱数を設定
    r_h = np.arange(0, 1 + r_step, r_step, dtype=float)

    # 太陽方位角を設定するための乱数を設定
    r_a = np.arange(0, 1 + r_step, r_step, dtype=float)

    # 各乱数の総当たりの組み合わせを設定
    random_numbers = list(itertools.product(r_h, r_a))

    return random_numbers


def get_random_sun_altitude(random_number: float) -> float:
    """
    任意の太陽高度を計算する

    :param random_number: 0～1の乱数
    :return:任意の太陽高度[degree]
    """
    return math.degrees(math.acos(math.sqrt(1-random_number)))


def get_random_sun_azimuth_angle(random_number: float) -> float:
    """
    任意の太陽方位角を計算する

    :param random_number: 0～1の乱数
    :return:任意の太陽方位角[degree]
    """
    return math.degrees(2.0 * math.pi * random_number)


def case_study():

    # 四角形の場合
    spec = common.HanaBlockSpec(
        type='square', depth=100, inclination_angle=90, azimuth_angle=0, width=130.0, height=130.0)
    print(diffused_light_transmission_rate(spec))

    # 円形の場合
    spec = common.HanaBlockSpec(
        type='circle', depth=100, inclination_angle=90, azimuth_angle=0, radius=65.0)
    print(diffused_light_transmission_rate(spec))

    # 三角形の場合
    spec = common.HanaBlockSpec(
        type='triangle', depth=100, inclination_angle=90, azimuth_angle=0,
        points={'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 0)})
    print(diffused_light_transmission_rate(spec))


if __name__ == '__main__':

    case_study()
