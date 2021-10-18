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


def distance_of_points_shadow(depth: float, tan_phi: float, tan_gamma: float) -> [float, float]:
    """
    点の影の垂直方向、水平方向の移動距離を計算する

    :param depth: 奥行[mm]
    :param tan_phi: 見かけの太陽高度（プロファイル角）の正接[-]
    :param tan_gamma: 面の太陽方位角の正接[-]
    # :param sun_altitude: 太陽高度[degrees]
    # :param sun_azimuth_angle: 太陽方位角[degrees]
    # :param surface_inclination_angle:  面の傾斜角[degrees]
    # :param surface_azimuth_angle:  面の方位角[degrees]
    :return: 点の影の垂直方向、水平方向の移動距離[mm]
    """

    # # 太陽光線の方向余弦を計算
    # s_h, s_w, s_s = direction_cosine_of_sunlight(sun_altitude=sun_altitude, sun_azimuth_angle=sun_azimuth_angle)
    #
    # # 傾斜面法線の方向余弦を計算
    # w_z, w_w, w_s = direction_cosine_of_slope_normal_line(
    #     surface_inclination_angle=surface_inclination_angle, surface_azimuth_angle=surface_azimuth_angle)
    #
    # # 太陽光線の入射角の余弦を計算
    # cos_theta = cosine_sun_incidence_angle(s_h=s_h, s_w=s_w, s_s=s_s, w_z=w_z, w_w=w_w, w_s=w_s)

    # # 誤差値を規定
    # error_value = 0.0001
    #
    # # cos_thetaが誤差値未満の場合は計算しない（太陽が対象面の裏側にある）
    # if cos_theta < error_value:
    #     tan_phi = 0.0
    #     tan_gamma = 0.0
    #
    # else:
    #     # 見かけの太陽高度（プロファイル角）の正接を計算
    #     tan_phi = tangent_profile_angle(s_h=s_h, s_w=s_w, s_s=s_s, cos_theta=cos_theta,
    #                                     surface_inclination_angle=surface_inclination_angle,
    #                                     surface_azimuth_angle=surface_azimuth_angle)
    #
    #     # 面の太陽方位角の正接を計算
    #     tan_gamma = tangent_sun_azimuth_angle_of_surface(s_w=s_w, s_s=s_s, cos_theta=cos_theta,
    #                                                      surface_azimuth_angle=surface_azimuth_angle)

    # 点の影の垂直方向、水平方向の移動距離を計算
    distance_vertical = depth * tan_phi
    distance_horizontal = depth * tan_gamma

    return distance_vertical, distance_horizontal


def tangent_profile_angle(s_h: float, s_w: float, s_s: float, cos_theta: float,
                          surface_inclination_angle: float, surface_azimuth_angle: float) -> float:
    """
    見かけの太陽高度（プロファイル角）の正接を計算する

    :param s_h: 太陽光線の方向余弦[-]
    :param s_w: 太陽光線の方向余弦[-]
    :param s_s: 太陽光線の方向余弦[-]
    :param cos_theta: 太陽光線の入射角の余弦[-]
    :param surface_inclination_angle:  面の傾斜角[degrees]
    :param surface_azimuth_angle:  面の方位角[degrees]
    :return: 太陽光線の入射角[degrees]
    """

    # 誤差値を規定
    error_value = 0.0001

    # cos_thetaが誤差値未満の場合は計算しない（太陽が対象面の裏側にある）
    if cos_theta < error_value:
        tan_phi = 0
    else:
        tan_phi = (s_h * math.sin(math.radians(surface_inclination_angle))
                   - s_w * (math.cos(math.radians(surface_inclination_angle)) * math.sin(math.radians(surface_azimuth_angle)))
                   - s_s * (math.cos(math.radians(surface_inclination_angle)) * math.cos(math.radians(surface_azimuth_angle)))
                   ) / cos_theta

    return tan_phi


def tangent_sun_azimuth_angle_of_surface(s_w: float, s_s: float, cos_theta: float,
                                         surface_azimuth_angle: float) -> float:
    """
    面の太陽方位角の正接を計算する

    :param s_w: 太陽光線の方向余弦[-]
    :param s_s: 太陽光線の方向余弦[-]
    :param cos_theta: 太陽光線の入射角の余弦[-]
    :param surface_azimuth_angle:  面の方位角[degrees]
    :return: 面の太陽方位角の正接[-]
    """

    # 誤差値を規定
    error_value = 0.0001

    # cos_thetaが誤差値未満の場合は計算しない（太陽が対象面の裏側にある）
    if cos_theta < error_value:
        tan_gamma = 0
    else:
        tan_gamma = (s_w * math.cos(math.radians(surface_azimuth_angle))
                     - s_s * math.sin(math.radians(surface_azimuth_angle))
                     ) / cos_theta

    return tan_gamma


def cosine_sun_incidence_angle(s_h: float, s_w: float, s_s: float, w_z: float, w_w: float, w_s: float) -> float:
    """
    太陽光線の入射角の余弦を計算する

    :param s_h: 太陽光線の方向余弦[-]
    :param s_w: 太陽光線の方向余弦[-]
    :param s_s: 太陽光線の方向余弦[-]
    :param w_z: 傾斜面法線の方向余弦[-]
    :param w_w: 傾斜面法線の方向余弦[-]
    :param w_s: 傾斜面法線の方向余弦[-]
    :return: 太陽光線の入射角の余弦[-]
    """

    cos_theta = s_h * w_z + s_w * w_w + s_s * w_s

    return cos_theta


def direction_cosine_of_sunlight(sun_altitude: float, sun_azimuth_angle: float) -> [float, float, float]:
    """
    太陽光線の方向余弦を計算する

    :param sun_altitude: 太陽高度[degrees]
    :param sun_azimuth_angle: 太陽方位角[degrees]
    :return: 太陽光線の方向余弦s_h, s_w, s_s[-]
    """

    # 太陽光線の方向余弦
    s_h = math.sin(math.radians(sun_altitude))
    s_w = math.cos(math.radians(sun_altitude)) * math.sin(math.radians(sun_azimuth_angle))
    s_s = math.cos(math.radians(sun_altitude)) * math.cos(math.radians(sun_azimuth_angle))

    return s_h, s_w, s_s


def direction_cosine_of_slope_normal_line(surface_inclination_angle: float,
                                          surface_azimuth_angle: float) -> [float, float, float]:
    """
    傾斜面法線の方向余弦を計算する

    :param surface_inclination_angle:  面の傾斜角[degrees]
    :param surface_azimuth_angle:  面の方位角[degrees]
    :return: 傾斜面法線の方向余弦w_z, w_w, w_s[-]
    """

    # 傾斜面法線の方向余弦
    w_z = math.cos(math.radians(surface_inclination_angle))
    w_w = math.sin(math.radians(surface_inclination_angle)) * math.sin(math.radians(surface_azimuth_angle))
    w_s = math.sin(math.radians(surface_inclination_angle)) * math.cos(math.radians(surface_azimuth_angle))

    return w_z, w_w, w_s


def case_study():
    sun_altitude = 50
    sun_azimuth_angle = 20
    surface_inclination_angle = 90
    surface_azimuth_angle = 0
    width = 130
    height = 130
    depth = 100

    # 太陽光線の方向余弦を計算
    s_h, s_w, s_s = direction_cosine_of_sunlight(sun_altitude=sun_altitude, sun_azimuth_angle=sun_azimuth_angle)

    # 傾斜面法線の方向余弦を計算
    w_z, w_w, w_s = direction_cosine_of_slope_normal_line(
        surface_inclination_angle=surface_inclination_angle, surface_azimuth_angle=surface_azimuth_angle)

    # 太陽光線の入射角の余弦を計算
    cos_theta = cosine_sun_incidence_angle(s_h=s_h, s_w=s_w, s_s=s_s, w_z=w_z, w_w=w_w, w_s=w_s)

    # 見かけの太陽高度（プロファイル角）の正接を計算
    tan_phi = tangent_profile_angle(s_h=s_h, s_w=s_w, s_s=s_s, cos_theta=cos_theta,
                                    surface_inclination_angle=surface_inclination_angle,
                                    surface_azimuth_angle=surface_azimuth_angle)

    # 面の太陽方位角の正接を計算
    tan_gamma = tangent_sun_azimuth_angle_of_surface(s_w=s_w, s_s=s_s, cos_theta=cos_theta,
                                                     surface_azimuth_angle=surface_azimuth_angle)

    distance_vertical, distance_horizontal = distance_of_points_shadow(depth, tan_phi, tan_gamma)

    ratio = transmission_factor_circle(cos_theta, width, distance_vertical, distance_horizontal)
    # ratio = transmission_factor_square(cos_theta, width, height, distance_vertical, distance_horizontal)

    return ratio


if __name__ == '__main__':

    print(case_study())


