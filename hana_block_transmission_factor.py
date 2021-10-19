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


def transmission_factor_triangle(coordinates: dict, distance_vertical: float, distance_horizontal: float) -> float:
    """
    三角形の花ブロックの透過率を計算する

    :param coordinates: 手前側の三角形ABCの各頂点の座標(x, y)
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return:三角形の花ブロックの透過率[-]
    """

    if math.isnan(distance_horizontal) and math.isnan(distance_vertical):
        # 点の影の垂直方向の移動距離、水平方向の移動距離がnan値の場合は太陽光線は入射しないので透過率は0とする
        rate = 0.0
    else:
        # 奥側の三角形A'B'C'の各頂点の座標を設定
        coordinates['peak_a_dash'] = (coordinates['peak_a'][0] + distance_vertical,
                                      coordinates['peak_a'][1] + distance_horizontal)
        coordinates['peak_b_dash'] = (coordinates['peak_b'][0] + distance_vertical,
                                      coordinates['peak_b'][1] + distance_horizontal)
        coordinates['peak_c_dash'] = (coordinates['peak_c'][0] + distance_vertical,
                                      coordinates['peak_c'][1] + distance_horizontal)

        # 三角形の内側にある頂点を判定
        peak_check_results = get_witch_peak_inside(coordinates)

        # 透過率を計算
        if True in peak_check_results.values():
            # 基準点、内部点の高さを取得
            h, h_dash = get_point_heights(peak_check_results, coordinates)
            # 透過率を計算
            rate = (h_dash / h) ** 2
        else:
            # 内側にある頂点が一つもない場合は、三角形は重ならないので透過率=0.0とする
            rate = 0.0

    return rate


def get_witch_peak_inside(coordinates: dict) -> dict:

    """
    三角形の内側にある頂点を判定する

    :param coordinates: 手前側の三角形ABC、奥側の三角形ABCのの各頂点の座標(x, y)
    :return:各頂点の判定結果
    """

    # 行列の初期化
    matrix_coeff = np.zeros(shape=(2, 2))
    matrix_const = np.zeros(2)

    # 行列に値を設定（係数部分）
    matrix_coeff[0][0] = coordinates['peak_b'][0] - coordinates['peak_a'][0]
    matrix_coeff[0][1] = coordinates['peak_c'][0] - coordinates['peak_a'][0]
    matrix_coeff[1][0] = coordinates['peak_b'][1] - coordinates['peak_a'][1]
    matrix_coeff[1][1] = coordinates['peak_c'][1] - coordinates['peak_a'][1]

    # 判定結果を格納するディクショナリを用意
    results = {}

    # 頂点Aの判定
    matrix_const[0] = coordinates['peak_a'][0] - coordinates['peak_a_dash'][0]
    matrix_const[1] = coordinates['peak_a'][1] - coordinates['peak_a_dash'][1]
    results['peak_a'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点Bの判定
    matrix_const[0] = coordinates['peak_b'][0] - coordinates['peak_a_dash'][0]
    matrix_const[1] = coordinates['peak_b'][1] - coordinates['peak_a_dash'][1]
    results['peak_b'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点Cの判定
    matrix_const[0] = coordinates['peak_c'][0] - coordinates['peak_a_dash'][0]
    matrix_const[1] = coordinates['peak_c'][1] - coordinates['peak_a_dash'][1]
    results['peak_c'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点A'の判定
    matrix_const[0] = coordinates['peak_a_dash'][0] - coordinates['peak_a'][0]
    matrix_const[1] = coordinates['peak_a_dash'][1] - coordinates['peak_a'][1]
    results['peak_a_dash'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点B'の判定
    matrix_const[0] = coordinates['peak_b_dash'][0] - coordinates['peak_a'][0]
    matrix_const[1] = coordinates['peak_b_dash'][1] - coordinates['peak_a'][1]
    results['peak_b_dash'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点C'の判定
    matrix_const[0] = coordinates['peak_c_dash'][0] - coordinates['peak_a'][0]
    matrix_const[1] = coordinates['peak_c_dash'][1] - coordinates['peak_a'][1]
    results['peak_c_dash'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    return results


def judge_is_peak_inside(matrix_coeff: np.zeros(shape=(2, 2)), matrix_const: np.zeros(2)) -> bool:

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


def get_point_heights(peak_check_results: dict, coordinates: dict) -> [float, float]:
    """
    対辺からの基準点、内部点の高さを計算する

    :param peak_check_results: 各頂点が内側にあるかどうかの判定結果
    :param coordinates: 手前側の三角形ABC、奥側の三角形ABCの各頂点の座標(x, y)
    :return:対辺からの基準点、内部点の高さ(mm)
    """

    # 内側にある頂点の座標を設定
    inside_peak_name = [key for key, value in peak_check_results.items() if value is True][0]
    inside_point = coordinates[inside_peak_name]

    # 対象となる基準点、対辺の2点の座標を取得
    target = get_target_base_point_and_side(inside_peak_name)
    base_point = coordinates[target['base_point']]
    side_point1 = coordinates[target['side_point1']]
    side_point2 = coordinates[target['side_point2']]

    # 対辺の2点を結ぶ一次方程式の係数を取得
    p, q, r = get_linear_equation(side_point1, side_point2)

    # 対辺からの基準点の高さを計算
    h = get_point_height_from_line(point_coordinate=base_point, p=p, q=q, r=r)

    # 対辺からの内部点の高さを計算
    h_dash = get_point_height_from_line(point_coordinate=inside_point, p=p, q=q, r=r)

    return h, h_dash


def get_target_base_point_and_side(inside_peak_name: str) -> dict:
    """
        内部点に応じて基準点となる頂点、および対辺を結ぶ2つの頂点の名称を設定する

        :param inside_peak_name: 内側にある頂点の名称
        :return:基準点となる頂点、および対辺を結ぶ2つの頂点の名称
    """

    target = {}

    if inside_peak_name == 'peak_a':
        target = {
            'base_point': 'peak_a_dash', 'side_point1': 'peak_b_dash', 'side_point2': 'peak_c_dash'
        }
    elif inside_peak_name == 'peak_b':
        target = {
            'base_point': 'peak_b_dash', 'side_point1': 'peak_a_dash', 'side_point2': 'peak_c_dash'
        }
    elif inside_peak_name == 'peak_c':
        target = {
            'base_point': 'peak_c_dash', 'side_point1': 'peak_a_dash', 'side_point2': 'peak_b_dash'
        }
    elif inside_peak_name == 'peak_a_dash':
        target = {
            'base_point': 'peak_a', 'side_point1': 'peak_b', 'side_point2': 'peak_c'
        }
    elif inside_peak_name == 'peak_b_dash':
        target = {
            'base_point': 'peak_b', 'side_point1': 'peak_a', 'side_point2': 'peak_c'
        }
    elif inside_peak_name == 'peak_c_dash':
        target = {
            'base_point': 'peak_c', 'side_point1': 'peak_a', 'side_point2': 'peak_b'
        }

    return target


def get_linear_equation(coordinates_point1: tuple, coordinates_point2: tuple) -> [float, float, float]:
    """
        2点を通る一次方程式（px+qy+r=0）の各係数p,q,rを計算する

        :param coordinates_point1: 1つ目の点の座標(x, y)
        :param coordinates_point1: 2つ目の点の座標(x, y)
        :return:一次方程式（px+qy+r=0）の各係数p,q,r
    """
    p = (coordinates_point2[1] - coordinates_point1[1]) / (coordinates_point2[0] - coordinates_point1[0])
    q = -1.0
    r = (coordinates_point2[0] * coordinates_point1[1] - coordinates_point1[0] * coordinates_point2[1])\
        / (coordinates_point2[0] - coordinates_point1[0])

    return p, q, r


def get_point_height_from_line(point_coordinate: tuple, p: float, q: float, r: float) -> float:
    """
        直線からの点の高さを計算する

        :param point_coordinate: 対象となる点の座標(x, y)
        :param p: 一次方程式（px+qy+r=0）の係数
        :param q: 一次方程式（px+qy+r=0）の係数
        :param r: 一次方程式（px+qy+r=0）の係数
        :return:一次方程式（px+qy+r=0）の各係数p,q,r
    """
    height = abs(p * point_coordinate[0] + q * point_coordinate[1] + r) / math.sqrt(p ** 2 + q ** 2)
    return height


def case_study_triangle():

    triangle_coordinates = {'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 0)}
    print(transmission_factor_triangle(triangle_coordinates, 10, -50))


if __name__ == '__main__':

    case_study_triangle()
