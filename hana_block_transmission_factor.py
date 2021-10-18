import math
import numpy as np


def transmission_factor_square(width: float, height: float, distance_vertical: float, distance_horizontal: float) -> float:
    """
    四角形の花ブロックの透過率を計算する

    :param width: 幅[mm]
    :param height: 高さ[mm]
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return: 四角形の花ブロックの透過率[-]
    """

    if math.isnan(distance_horizontal) and math.isnan(distance_vertical):
        # 点の影の垂直方向の移動距離、水平方向の移動距離がnan値の場合は太陽光線は入射しないので透過率は0とする
        rate = 0.0
    else:
        # 点の影の移動距離を絶対値に変換
        d_x = abs(distance_horizontal)
        d_y = abs(distance_vertical)

        if d_x >= width or d_y >= height:
            rate = 0.0
        else:
            # 開口部分の面積、重なり部分の面積を計算
            area_opening = width * height
            area_transmit = (width - d_x) * (height - d_y)

            # 透過率を計算
            rate = area_transmit / area_opening

    return rate


def transmission_factor_circle(radius: float, distance_vertical: float, distance_horizontal: float) -> float:
    """
    円形の花ブロックの透過率を計算する

    :param radius: 円の半径[mm]
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return: 円形の花ブロックの透過率[-]
    """

    if math.isnan(distance_horizontal) and math.isnan(distance_vertical):
        # 点の影の垂直方向の移動距離、水平方向の移動距離がnan値の場合は太陽光線は入射しないので透過率は0とする
        rate = 0.0
    else:
        # 円の中心点の移動距離[mm]を計算
        distance = math.sqrt(distance_vertical ** 2 + distance_horizontal ** 2)

        # 円の中心点の距離が半径より大きい場合は、円は重ならないので透過率=0.0とする
        if distance >= 2 * radius:
            area_transmit = 0.0
        else:
            # 扇形の内角[degree]を計算
            angle = 2 * math.acos((distance ** 2) / (2 * radius * distance))

            # 扇形部分の面積を計算
            area_sector = math.pi * radius ** 2 * (angle / (2 * math.pi))

            # 三角形部分の面積を計算
            area_triangle = 0.5 * radius ** 2 * math.sin(math.radians(angle))

            # 重なり部分の面積を計算
            area_transmit = 2 * (area_sector - area_triangle)

        # 開口部分の面積を計算
        area_opening = math.pi * radius ** 2

        # 透過率を計算
        rate = area_transmit / area_opening

    return rate


def transmission_factor_triangle(coordinates_front: dict,
                                 distance_vertical: float, distance_horizontal: float) -> float:
    """
    三角形の花ブロックの透過率を計算する

    :param coordinates_front: 手前側の三角形ABCの各頂点の座標(x, y)
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return:三角形の花ブロックの透過率[-]
    """

    # 奥側の三角形A'B'C'の各頂点の座標を設定
    coordinates_back = {
        'peak_a_dash': (coordinates_front['peak_a'][0] + distance_vertical,
                        coordinates_front['peak_a'][1] + distance_horizontal),
        'peak_b_dash': (coordinates_front['peak_b'][0] + distance_vertical,
                        coordinates_front['peak_b'][1] + distance_horizontal),
        'peak_c_dash': (coordinates_front['peak_c'][0] + distance_vertical,
                        coordinates_front['peak_c'][1] + distance_horizontal)
    }

    results = get_witch_peak_inside(coordinates_front, coordinates_back)

    ratio = 0.0

    return ratio


def get_witch_peak_inside(coordinates_front: dict, coordinates_back: dict) -> dict:

    """
    三角形の内側にある頂点を判定する

    :param coordinates_front: 手前側の三角形ABCの各頂点の座標(x, y)
    :param coordinates_back: 奥側の三角形ABCの各頂点の座標(x, y)
    :return:三角形の花ブロックの透過率[-]
    """

    # 行列の初期化
    matrix_coeff = np.zeros(shape=(2, 2))
    matrix_const = np.zeros(2)

    # 行列に値を設定（係数部分）
    matrix_coeff[0][0] = coordinates_front['peak_b'][0] - coordinates_front['peak_a'][0]
    matrix_coeff[0][1] = coordinates_front['peak_c'][0] - coordinates_front['peak_a'][0]
    matrix_coeff[1][0] = coordinates_front['peak_b'][1] - coordinates_front['peak_a'][1]
    matrix_coeff[1][1] = coordinates_front['peak_c'][1] - coordinates_front['peak_a'][1]

    # 判定結果を格納するディクショナリを用意
    results = {}

    # 頂点Aの判定
    matrix_const[0] = coordinates_front['peak_a'][0] - coordinates_back['peak_a_dash'][0]
    matrix_const[1] = coordinates_front['peak_a'][1] - coordinates_back['peak_a_dash'][1]
    results['peak_a'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点Bの判定
    matrix_const[0] = coordinates_front['peak_b'][0] - coordinates_back['peak_a_dash'][0]
    matrix_const[1] = coordinates_front['peak_b'][1] - coordinates_back['peak_a_dash'][1]
    results['peak_b'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    return results


def judge_is_peak_inside(matrix_coeff: float, matrix_const: float) -> bool:

    """
    辺AB、辺ACに対する比率s, tを計算し、三角形の内側にある条件に合致するか判定する

    :param matrix_coeff: 係数の行列
    :param matrix_const: 定数の行列
    :return:判定結果
    """

    # 辺AB、辺ACに対する比率s, tを計算
    matrix_coeff_inv = np.linalg.inv(matrix_coeff)
    matrix_solution = np.matmul(matrix_coeff_inv, matrix_const)

    # 内側にあるかどうかの判定
    # 条件01：S >= 0、条件02：T >= 0、条件03 ：S + T <= 1
    if matrix_solution[0] >= 0.0 and matrix_solution[1] >= 0.0 and matrix_solution[0] + matrix_solution[1] <= 1.0:
        judge = True
    else:
        judge = False

    return judge


def case_study_triangle():

    front_triangle_peak_coordinates = {'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 0)}
    print(transmission_factor_triangle(front_triangle_peak_coordinates, 10, 50))


if __name__ == '__main__':

    print(case_study_triangle())


