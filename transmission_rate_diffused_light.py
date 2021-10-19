import numpy as np
import math
import statistics
import itertools
import distance_point_shadow as dps
import transmission_rate_base as trb


def diffused_light_transmission_rate_square(depth: float, width: float, height: float,
                                            surface_inclination_angle: float, surface_azimuth_angle: float) -> float:
    """
    四角形の花ブロックの拡散光の透過率を計算する

    :param depth: 奥行[mm]
    :param width: 幅[mm]
    :param height: 高さ[mm]
    :param surface_inclination_angle:  面の傾斜角[degrees]
    :param surface_azimuth_angle:  面の方位角[degrees]
    :return:四角形の花ブロックの拡散光の透過率[-]
    """

    # 各乱数の総当たりの組み合わせを設定
    random_numbers = get_random_number_list()

    # 結果格納用の配列を用意
    rate_s = []

    for index, case in enumerate(random_numbers):

        # 点の影の垂直方向、水平方向の移動距離を計算
        distance_vertical, distance_horizontal = dps.distance_of_points_shadow(
            depth=depth,
            sun_altitude=get_random_sun_altitude(case[0]),
            sun_azimuth_angle=get_random_sun_azimuth_angle(case[1]),
            surface_inclination_angle=surface_inclination_angle,
            surface_azimuth_angle=surface_azimuth_angle
        )

        # 透過率を計算し、配列に追加
        rate_s.append(
            trb.base_transmission_rate_square(width=width, height=height,
                                              distance_vertical=distance_vertical,
                                              distance_horizontal=distance_horizontal
                                              )
        )

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

    print(
        diffused_light_transmission_rate_square(
            depth=100, width=130, height=130, surface_inclination_angle=90, surface_azimuth_angle=0)
    )


if __name__ == '__main__':

    case_study()
