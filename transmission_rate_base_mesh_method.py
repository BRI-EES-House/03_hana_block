import numpy as np
import math
import common


def base_transmission_rate(spec: common.HanaBlockSpec,
                           distance_vertical: float, distance_horizontal: float) -> float:
    """
    花ブロックの基準透過率を計算する

    :param spec:   花ブロックの仕様
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return: 四角形の花ブロックの基準透過率[-]
    """

    # 解像度を設定
    resolution = 350

    if math.isnan(distance_horizontal) and math.isnan(distance_vertical):
        # 点の影の垂直方向の移動距離、水平方向の移動距離がnan値の場合は太陽光線は入射しないので透過率は0とする
        rate = 0.0
    else:
        # 移動前後の図形をメッシュにプロットする
        mesh_1 = make_plot_in_mesh(spec, resolution, 0.0, 0.0)
        mesh_2 = make_plot_in_mesh(spec, resolution, distance_vertical, distance_horizontal)

        # メッシュの重なり部分を計算
        mesh_3 = np.add(mesh_1, mesh_2)

        # # csvファイルとして保存（デバッグ用）
        # np.savetxt('mesh_1.csv', mesh_1, delimiter=',')
        # np.savetxt('mesh_2.csv', mesh_2, delimiter=',')
        # np.savetxt('mesh_3.csv', mesh_3, delimiter=',')

        # 重なり部分（mesh_1とmesh_2の合計値が2になる部分）のピクセル数を計算
        overlap_pixels = np.count_nonzero(mesh_3 == 2)

        # 移動前の図形のピクセル数を計算
        all_pixels = np.sum(mesh_1)

        if all_pixels > 0:
            rate = overlap_pixels / all_pixels
        else:
            raise ValueError('図形がプロットされていません')

    return rate


def make_plot_in_mesh(spec: common.HanaBlockSpec, resolution: int,
                      distance_vertical: float, distance_horizontal: float):
    """
    図形をメッシュにプロットする

    :param spec:        花ブロックの仕様
    :param resolution:  解像度
    :param distance_vertical: 点の影の垂直方向の移動距離[mm]
    :param distance_horizontal: 点の影の水平方向の移動距離[mm]
    :return:図形がプロットされたメッシュ配列
    """

    # 1行のピクセル数を計算
    pixels = get_pixel(max(spec.width, spec.height), resolution)

    # 移動距離をピクセルに変換
    x_pixels = get_pixel(distance_vertical, resolution)
    y_pixels = get_pixel(distance_horizontal, resolution)

    # メッシュ配列を用意
    plotted_mesh = np.zeros((pixels, pixels))

    if spec.type == 'square':
        plotted_mesh = [
            [
                is_inside_square(spec, x, y, x_pixels, y_pixels, resolution)
                for x, item_x in enumerate(plotted_mesh[0])
            ]
            for y, item_y in enumerate(plotted_mesh[1])
        ]
    elif spec.type == 'circle':
        plotted_mesh = [
            [
                is_inside_circle(spec, x, y, x_pixels, y_pixels, resolution)
                for x, item_x in enumerate(plotted_mesh[0])
            ]
            for y, item_y in enumerate(plotted_mesh[1])
        ]
    elif spec.type == 'triangle':
        plotted_mesh = [
            [
                is_inside_triangle(spec, x, y, x_pixels, y_pixels, resolution)
                for x, item_x in enumerate(plotted_mesh[0])
            ]
            for y, item_y in enumerate(plotted_mesh[1])
        ]
    else:
        raise ValueError('花ブロックのタイプ「' + spec.type + '」は対象外です')

    return plotted_mesh


def get_pixel(length: float, resolution: int) -> int:
    """
    mmをピクセルに変換する（1inch=25.4mmとする）

    :param length:      長さ[mm]
    :param resolution:  解像度
    :return:長さ[px]
    """
    return int(resolution * length / 25.4)


def is_inside_square(spec: common.HanaBlockSpec, x_position: int, y_position: int,
                     x_pixels: float, y_pixels: float, resolution: int) -> int:
    """
    指定した四角形の中に任意の点Pがあるかどうかを判定する

    :param spec:        花ブロックの仕様
    :param x_position:  任意の点Pのx座標[px]
    :param y_position:  任意の点Pのy座標[px]
    :param x_pixels:    点の影の垂直方向の移動距離[px]
    :param y_pixels:    点の影の水平方向の移動距離[px]
    :param resolution:  解像度
    :return: 内側にある場合は1,ない場合は0
    """

    # 任意の点Pの座標を設定
    my_point = (x_position, y_position)

    # 各点の座標を設定
    point_a = (get_pixel(spec.points['peak_a'][0], resolution) + x_pixels,
               get_pixel(spec.points['peak_a'][1], resolution) + y_pixels)
    point_b = (get_pixel(spec.points['peak_b'][0], resolution) + x_pixels,
               get_pixel(spec.points['peak_b'][1], resolution) + y_pixels)
    point_c = (get_pixel(spec.points['peak_c'][0], resolution) + x_pixels,
               get_pixel(spec.points['peak_c'][1], resolution) + y_pixels)
    point_d = (get_pixel(spec.points['peak_d'][0], resolution) + x_pixels,
               get_pixel(spec.points['peak_d'][1], resolution) + y_pixels)

    # 辺ABと辺APの外積
    cross_product_ab = get_cross_product(point_a, point_b, my_point)

    # 辺BCと辺BPの外積
    cross_product_bc = get_cross_product(point_b, point_c, my_point)

    # 辺CDと辺CPの外積
    cross_product_cd = get_cross_product(point_c, point_d, my_point)

    # 辺DAと辺DPの外積
    cross_product_da = get_cross_product(point_d, point_a, my_point)

    # すべて辺との外積が0以上のとき、四角形の内側と判定
    if cross_product_ab >= 0 and cross_product_bc >= 0 and cross_product_cd >= 0 and cross_product_da >= 0:
        is_inside = 1
    else:
        is_inside = 0

    return is_inside


def is_inside_triangle(spec: common.HanaBlockSpec, x_position: int, y_position: int,
                       x_pixels: float, y_pixels: float, resolution: int) -> int:
    """
    指定した三角形の中に任意の点Pがあるかどうかを判定する

    :param spec:        花ブロックの仕様
    :param x_position:  任意の点Pのx座標[px]
    :param y_position:  任意の点Pのy座標[px]
    :param x_pixels:    点の影の垂直方向の移動距離[px]
    :param y_pixels:    点の影の水平方向の移動距離[px]
    :param resolution:  解像度
    :return: 内側にある場合は1,ない場合は0
    """

    # 任意の点Pの座標を設定
    my_point = (x_position, y_position)

    # 各点の座標を設定
    point_a = (get_pixel(spec.points['peak_a'][0], resolution) + x_pixels,
               get_pixel(spec.points['peak_a'][1], resolution) + y_pixels)
    point_b = (get_pixel(spec.points['peak_b'][0], resolution) + x_pixels,
               get_pixel(spec.points['peak_b'][1], resolution) + y_pixels)
    point_c = (get_pixel(spec.points['peak_c'][0], resolution) + x_pixels,
               get_pixel(spec.points['peak_c'][1], resolution) + y_pixels)

    # 辺ABと辺APの外積
    cross_product_ab = get_cross_product(point_a, point_b, my_point)

    # 辺BCと辺BPの外積
    cross_product_bc = get_cross_product(point_b, point_c, my_point)

    # 辺CAと辺CPの外積
    cross_product_ca = get_cross_product(point_c, point_a, my_point)

    # すべて辺との外積が同じ符号のとき、三角形の内側と判定
    if cross_product_ab >= 0 and cross_product_bc >= 0 and cross_product_ca >= 0:
        is_inside = 1
    elif cross_product_ab < 0 and cross_product_bc < 0 and cross_product_ca < 0:
        is_inside = 1
    else:
        is_inside = 0

    return is_inside


def get_cross_product(point1: (int, int), point2: (int, int), my_point: (int, int)) -> float:
    """
    指定した辺と任意の点Pとの辺の外積を計算する

    :param point1:   指定した辺の開始座標
    :param point2:   指定した辺の終了座標
    :param my_point: 任意の点Pの座標
    :return: 外積
    """

    # 指定した辺のベクトル
    vect_side = (point1[0] - point2[0], point1[1] - point2[1])

    # 指定した辺の開始座標と任意の点Pがなす辺のベクトル
    vect_point = (point1[0] - my_point[0], point1[1] - my_point[1])

    # ベクトルの外積を計算
    vector_cross = vect_side[0] * vect_point[1] - vect_side[1] * vect_point[0]

    return vector_cross


def is_inside_circle(spec: common.HanaBlockSpec, x_position: int, y_position: int,
                     x_pixels: float, y_pixels: float, resolution: int) -> int:
    """
    指定した円の中に任意の点Pがあるかどうかを判定する

    :param spec:        花ブロックの仕様
    :param x_position:  任意の点Pのx座標[px]
    :param y_position:  任意の点Pのy座標[px]
    :param x_pixels:    点の影の垂直方向の移動距離[px]
    :param y_pixels:    点の影の水平方向の移動距離[px]
    :param resolution:  解像度
    :return: 内側にある場合は1,ない場合は0
    """

    # 任意の点Pの座標を設定
    my_point = (x_position, y_position)

    # 円の中心点の座標を設定
    point_a = (get_pixel(spec.points['peak_a'][0], resolution) + x_pixels,
               get_pixel(spec.points['peak_a'][1], resolution) + y_pixels)

    # 任意の点Pの座標と円の中心座標の直線距離を計算
    distance = np.sqrt((my_point[0] - point_a[0]) ** 2 + (my_point[1] - point_a[1]) ** 2)

    # 任意の点Pの座標と円の中心座標の直線距離が半径以下のとき、内側と判定
    if distance <= get_pixel(spec.radius, resolution):
        is_inside = 1
    else:
        is_inside = 0

    return is_inside


if __name__ == '__main__':

    # # 四角形の場合
    # spec = common.HanaBlockSpec(
    #     type='square', depth=100, inclination_angle=90, azimuth_angle=0, width=136.0, height=136.0)

    # # 円形の場合
    # spec = common.HanaBlockSpec(
    #     type='circle', depth=100, inclination_angle=90, azimuth_angle=0, radius=136.0 / 2.0)

    # 三角形の場合（その1）
    spec = common.HanaBlockSpec(
        type='triangle', depth=100, inclination_angle=90, azimuth_angle=0,
        points={'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 130)})

    # 解像度を設定
    resolution = 350

    print(base_transmission_rate(spec, 0.0, 10.0))
