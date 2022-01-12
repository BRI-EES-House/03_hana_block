import pandas as pd
import numpy as np
import math
import statistics
import itertools
import common
import distance_point_shadow
import transmission_rate_base


def diffused_light_transmission_rate(calc_target: str, spec: common.HanaBlockSpec) -> float:
    """
    四角形の花ブロックの拡散光の透過率を計算する
    (花ブロックの方位は南向きとする）

    :param calc_target: 計算対象（sky: 天空光、reflected: 反射光）
    :param spec:   花ブロックの仕様
    :return:四角形の花ブロックの拡散光の透過率[-]
    """

    # 太陽高度、太陽方位角の総当たりの組み合わせを設定
    random_angles = get_random_angles_list(calc_target)

    # 結果格納用の配列を用意
    rate_s = []         # 透過率
    sun_altitudes = []   # 太陽高度
    sun_azimuth_angles = []  # 太陽方位角

    for index, case in enumerate(random_angles):

        # 太陽高度、太陽方位角を計算
        sun_altitude = case[0]
        sun_azimuth_angle = case[1]
        # sun_altitude = get_random_sun_altitude(case[0])
        # sun_azimuth_angle = get_random_sun_azimuth_angle(case[1])

        # 点の影の垂直方向、水平方向の移動距離を計算
        distance_vertical, distance_horizontal = distance_point_shadow.distance_of_points_shadow(
            spec=spec,
            sun_altitude=sun_altitude,
            sun_azimuth_angle=sun_azimuth_angle
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

        # 計算結果を配列に追加
        rate_s.append(buf_rate)
        sun_altitudes.append(sun_altitude)
        sun_azimuth_angles.append(sun_azimuth_angle)

    # デバッグ用
    # 計算結果をDataFrameに追加
    df = pd.DataFrame({'sun_altitude': sun_altitudes, 'sun_azimuth_angles': sun_azimuth_angles, 'rate_s': rate_s})

    # CSVファイルに出力
    df.to_csv('result/diffused_light_' + calc_target + '_' + spec.type + '.csv')

    return statistics.mean(rate_s)


def get_random_angles_list(calc_target: str) -> list:
    """
    0～1の範囲の乱数の総当たりの組み合わせを設定し、太陽高度、太陽方位角のリストとして返す

    :param calc_target: 計算対象（sky: 天空光、reflected: 反射光）
    :return:乱数の総当たりの組み合わせ
    """

    # 乱数のステップ数を設定（総ケース数が10^6になるように設定）
    r_step = 1.0 / math.sqrt(10 ** 6)

    # 太陽高度を設定するための乱数を設定
    r_h = np.arange(0, 1 + r_step, r_step, dtype=float)

    # 太陽方位角を設定するための乱数を設定
    r_a = np.arange(0, 1 + r_step, r_step, dtype=float)

    # 太陽高度を計算
    if calc_target == 'sky':
        sun_altitudes = np.array([get_random_sun_altitude(x) for x in r_h])
    elif calc_target == 'reflected':
        sun_altitudes = np.array([-1.0 * get_random_sun_altitude(x) for x in r_h])
    else:
        raise ValueError('計算対象「' + calc_target + '」は対象外です')

    # 太陽方位角を計算
    sun_azimuth_angles_base = np.array([get_random_sun_azimuth_angle(x) for x in r_a])

    # 太陽方位角を-90度～90度の範囲に限定 values[np.where((values>2) & (values<4))]
    sun_azimuth_angles = sun_azimuth_angles_base[np.where((sun_azimuth_angles_base >= -90.0) &
                                                 (sun_azimuth_angles_base <= 90.0))]

    # 太陽高度、太陽方位角の総当たりの組み合わせを設定
    random_angles = list(itertools.product(sun_altitudes, sun_azimuth_angles))

    return random_angles


def get_random_sun_altitude(random_number: float) -> float:
    """
    任意の太陽高度を計算する

    :param random_number: 0～1の乱数
    :return:任意の太陽高度[degree]
    """

    # 仰角を太陽高度に換算
    angle = 90.0 - math.degrees(math.acos(math.sqrt(1-random_number)))

    return angle


def get_random_sun_azimuth_angle(random_number: float) -> float:
    """
    任意の太陽方位角を計算する

    :param random_number: 0～1の乱数
    :return:任意の太陽方位角[degree]
    """

    # 方位角を計算
    angle = math.degrees(2.0 * math.pi * random_number)

    # 南0度、西90度、北180度、東-90度に換算
    if angle > 180.0:
        angle = angle - 360.0

    return angle


def case_study():

    # 四角形の場合
    spec = common.HanaBlockSpec(
        type='square', depth=100, inclination_angle=90, azimuth_angle=0, width=136.0, height=136.0,
        front_width=190.0, front_height=190.0
    )
    print(spec.type + '　sky:')
    print(diffused_light_transmission_rate('sky', spec))
    print(spec.type + '　reflected:')
    print(diffused_light_transmission_rate('reflected', spec))

    # 円形の場合
    spec = common.HanaBlockSpec(
        type='circle', depth=100, inclination_angle=90, azimuth_angle=0, radius=136.0 / 2.0,
        front_width=190.0, front_height=190.0
    )
    print(spec.type + '　sky:')
    print(diffused_light_transmission_rate('sky', spec))
    print(spec.type + '　reflected:')
    print(diffused_light_transmission_rate('reflected', spec))

    # 三角形の場合（その1）
    spec = common.HanaBlockSpec(
        type='triangle', depth=100, inclination_angle=90, azimuth_angle=0,
        points={'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 130)},
        front_width=190.0, front_height=190.0
    )
    print(spec.type + '　sky:')
    print(diffused_light_transmission_rate('sky', spec))
    print(spec.type + '　reflected:')
    print(diffused_light_transmission_rate('reflected', spec))

    # 三角形の場合（その2）
    spec = common.HanaBlockSpec(
        type='triangle', depth=150, inclination_angle=90, azimuth_angle=0,
        points={'peak_a': (0, 0), 'peak_b': (130, 130), 'peak_c': (0, 130)},
        front_width=190.0, front_height=190.0
    )
    print(spec.type + '　sky:')
    print(diffused_light_transmission_rate('sky', spec))
    print(spec.type + '　reflected:')
    print(diffused_light_transmission_rate('reflected', spec))


if __name__ == '__main__':

    case_study()
