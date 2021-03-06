import math
import numpy as np
import common
import distance_point_shadow


def base_transmission_rate_square(spec: common.HanaBlockSpec,
                                  distance_vertical: float, distance_horizontal: float) -> float:
    """
    四角形の花ブロックの基準透過率を計算する

    :param spec:   花ブロックの仕様
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return: 四角形の花ブロックの基準透過率[-]
    """

    if math.isnan(distance_horizontal) and math.isnan(distance_vertical):
        # 点の影の垂直方向の移動距離、水平方向の移動距離がnan値の場合は太陽光線は入射しないので透過率は0とする
        rate = 0.0
    else:
        # 点の影の移動距離を絶対値に変換
        d_x = abs(distance_horizontal)
        d_y = abs(distance_vertical)

        if d_x >= spec.width or d_y >= spec.height:
            rate = 0.0
        else:
            # 重なり部分の面積を計算
            area_transmit = (spec.width - d_x) * (spec.height - d_y)

            # 透過率を計算
            rate = area_transmit / spec.area

    return rate


def base_transmission_rate_circle(spec: common.HanaBlockSpec,
                                  distance_vertical: float, distance_horizontal: float) -> float:
    """
    円形の花ブロックの基準透過率を計算する

    :param spec:   花ブロックの仕様
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return: 円形の花ブロックの基準透過率[-]
    """

    if math.isnan(distance_horizontal) and math.isnan(distance_vertical):
        # 点の影の垂直方向の移動距離、水平方向の移動距離がnan値の場合は太陽光線は入射しないので透過率は0とする
        rate = 0.0
    else:
        # 円の中心点の移動距離[mm]を計算
        distance = math.sqrt(distance_vertical ** 2 + distance_horizontal ** 2)

        # 円の中心点の距離が半径より大きい場合は、円は重ならないので透過率=0.0とする
        if distance >= 2 * spec.radius:
            area_transmit = 0.0
        else:
            # 扇形の内角[rad]を計算
            angle = 2 * math.acos((distance ** 2) / (2 * spec.radius * distance))

            # 扇形部分の面積を計算
            area_sector = math.pi * (spec.radius ** 2) * (angle / (2 * math.pi))

            # 三角形部分の面積を計算
            area_triangle = 0.5 * (spec.radius ** 2) * math.sin(angle)

            # 重なり部分の面積を計算
            area_transmit = 2 * (area_sector - area_triangle)

        # 透過率を計算
        rate = area_transmit / spec.area

    return rate


def base_transmission_rate_triangle(spec: common.HanaBlockSpec,
                                    distance_vertical: float, distance_horizontal: float) -> float:
    """
    三角形の花ブロックの基準透過率を計算する

    :param spec:   花ブロックの仕様
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return:三角形の花ブロックの基準透過率[-]
    """

    if math.isnan(distance_horizontal) and math.isnan(distance_vertical):
        # 点の影の垂直方向の移動距離、水平方向の移動距離がnan値の場合は太陽光線は入射しないので透過率は0とする
        rate = 0.0
    else:
        # 奥側の三角形A'B'C'の各頂点の座標を設定
        spec.points['peak_a_dash'] = (spec.points['peak_a'][0] + distance_vertical,
                                      spec.points['peak_a'][1] + distance_horizontal)
        spec.points['peak_b_dash'] = (spec.points['peak_b'][0] + distance_vertical,
                                      spec.points['peak_b'][1] + distance_horizontal)
        spec.points['peak_c_dash'] = (spec.points['peak_c'][0] + distance_vertical,
                                      spec.points['peak_c'][1] + distance_horizontal)

        # 三角形の内側にある頂点を判定
        peak_check_results = get_witch_peak_inside(spec.points)

        # 透過率を計算
        if True in peak_check_results.values():
            # 基準点、内部点の高さを取得
            h, h_dash = get_point_heights(peak_check_results, spec.points)
            # 透過率を計算
            rate = (h_dash / h) ** 2
        else:
            # 内側にある頂点が一つもない場合は、三角形は重ならないので透過率=0.0とする
            rate = 0.0

    return rate


def get_witch_peak_inside(points: dict) -> dict:

    """
    三角形の内側にある頂点を判定する

    :param points: 手前側の三角形ABC、奥側の三角形ABCのの各頂点の座標(x, y)
    :return:各頂点の判定結果
    """

    # 行列の初期化
    matrix_coeff = np.zeros(shape=(2, 2))
    matrix_const = np.zeros(2)

    # 行列に値を設定（係数部分）
    matrix_coeff[0][0] = points['peak_b'][0] - points['peak_a'][0]
    matrix_coeff[0][1] = points['peak_c'][0] - points['peak_a'][0]
    matrix_coeff[1][0] = points['peak_b'][1] - points['peak_a'][1]
    matrix_coeff[1][1] = points['peak_c'][1] - points['peak_a'][1]

    # 判定結果を格納するディクショナリを用意
    results = {}

    # 頂点Aの判定
    matrix_const[0] = points['peak_a'][0] - points['peak_a_dash'][0]
    matrix_const[1] = points['peak_a'][1] - points['peak_a_dash'][1]
    results['peak_a'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点Bの判定
    matrix_const[0] = points['peak_b'][0] - points['peak_a_dash'][0]
    matrix_const[1] = points['peak_b'][1] - points['peak_a_dash'][1]
    results['peak_b'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点Cの判定
    matrix_const[0] = points['peak_c'][0] - points['peak_a_dash'][0]
    matrix_const[1] = points['peak_c'][1] - points['peak_a_dash'][1]
    results['peak_c'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点A'の判定
    matrix_const[0] = points['peak_a_dash'][0] - points['peak_a'][0]
    matrix_const[1] = points['peak_a_dash'][1] - points['peak_a'][1]
    results['peak_a_dash'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点B'の判定
    matrix_const[0] = points['peak_b_dash'][0] - points['peak_a'][0]
    matrix_const[1] = points['peak_b_dash'][1] - points['peak_a'][1]
    results['peak_b_dash'] = judge_is_peak_inside(matrix_coeff, matrix_const)

    # 頂点C'の判定
    matrix_const[0] = points['peak_c_dash'][0] - points['peak_a'][0]
    matrix_const[1] = points['peak_c_dash'][1] - points['peak_a'][1]
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


def get_point_heights(peak_check_results: dict, points: dict) -> [float, float]:
    """
    対辺からの基準点、内部点の高さを計算する

    :param peak_check_results: 各頂点が内側にあるかどうかの判定結果
    :param points: 手前側の三角形ABC、奥側の三角形ABCの各頂点の座標(x, y)
    :return:対辺からの基準点、内部点の高さ(mm)
    """

    # 内側にある頂点の座標を設定
    inside_peak_name = [key for key, value in peak_check_results.items() if value is True][0]
    inside_point = points[inside_peak_name]

    # 対象となる基準点、対辺の2点の座標を取得
    target = get_target_base_point_and_side(inside_peak_name)
    base_point = points[target['base_point']]
    side_point1 = points[target['side_point1']]
    side_point2 = points[target['side_point2']]

    # 対辺の2点を結ぶ一次方程式の係数を取得
    p, q, r = get_linear_equation(*side_point1, *side_point2)

    # 対辺からの基準点の高さを計算
    h = get_point_height_from_line(*base_point, p, q, r)
    # h = get_point_height_from_line(point_coordinate=base_point, p=p, q=q, r=r)

    # 対辺からの内部点の高さを計算
    h_dash = get_point_height_from_line(*inside_point, p, q, r)
    # h_dash = get_point_height_from_line(point_coordinate=inside_point, p=p, q=q, r=r)

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


def get_linear_equation(x_1: float, y_1: float, x_2: float, y_2: float) -> [float, float, float]:
    """
        2点を通る一次方程式（px+qy+r=0）の各係数p,q,rを計算する

        :param x_1: 1つ目の点のx座標
        :param y_1: 1つ目の点のy座標
        :param x_2: 2つ目の点のx座標
        :param y_2: 2つ目の点のy座標
        :return:一次方程式（px+qy+r=0）の各係数p,q,r
    """

    if abs(x_1 - x_2) < common.get_error_value():
        p = 1.0
        q = 0.0
        r = -x_1
    else:
        p = (y_2 - y_1) / (x_2 - x_1)
        q = -1.0
        r = (x_2 * y_1 - x_1 * y_2) / (x_2 - x_1)

    return p, q, r


def get_point_height_from_line(x: float, y: float, p: float, q: float, r: float) -> float:
    """
        直線からの点の高さを計算する

        :param x: 対象となる点のx座標
        :param y: 対象となる点のy座標
        :param p: 一次方程式（px+qy+r=0）の係数
        :param q: 一次方程式（px+qy+r=0）の係数
        :param r: 一次方程式（px+qy+r=0）の係数
        :return:一次方程式（px+qy+r=0）の各係数p,q,r
    """
    height = abs(p * x + q * y + r) / math.sqrt(p ** 2 + q ** 2)
    return height


def test():

    # 四角形の場合
    spec = common.HanaBlockSpec(
        type='square', depth=100, inclination_angle=90, azimuth_angle=0, width=136.0, height=136.0)
    dx, dy = \
        distance_point_shadow.distance_of_points_shadow(spec=spec, sun_altitude=2.0,
                                                        sun_azimuth_angle=-59)
    print(base_transmission_rate_square(spec=spec, distance_horizontal=dx, distance_vertical=dy))

    # 円形の場合
    spec = common.HanaBlockSpec(
        type='circle', depth=100, inclination_angle=90, azimuth_angle=0, radius=136.0 / 2.0)
    dx, dy = \
        distance_point_shadow.distance_of_points_shadow(spec=spec, sun_altitude=32,
                                                        sun_azimuth_angle=-1)
    print(base_transmission_rate_circle(spec=spec, distance_horizontal=dx, distance_vertical=dy))

    # 三角形01の場合
    spec = common.HanaBlockSpec(
        type='triangle', depth=100, inclination_angle=90, azimuth_angle=0,
        points={'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 130)})
    dx, dy = \
        distance_point_shadow.distance_of_points_shadow(spec=spec, sun_altitude=-30,
                                                        sun_azimuth_angle=-14)
    print(base_transmission_rate_triangle(spec=spec, distance_horizontal=dx, distance_vertical=dy))


if __name__ == '__main__':

    test()
