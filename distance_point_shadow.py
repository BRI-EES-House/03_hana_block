import math
import numpy as np
import common


def distance_of_points_shadow(spec: common.HanaBlockSpec,
                              sun_altitude: float, sun_azimuth_angle: float,) -> [float, float]:

    """
    点の影の垂直方向、水平方向の移動距離を計算する

    :param spec:   花ブロックの仕様
    :param sun_altitude: 太陽高度[degrees]
    :param sun_azimuth_angle: 太陽方位角[degrees]
    :return: 点の影の垂直方向、水平方向の移動距離[mm]
    """

    # 太陽光線の方向余弦を計算
    s_h, s_w, s_s = direction_cosine_of_sunlight(sun_altitude=sun_altitude, sun_azimuth_angle=sun_azimuth_angle)

    # 傾斜面法線の方向余弦を計算
    w_z, w_w, w_s = direction_cosine_of_slope_normal_line(
        surface_inclination_angle=spec.inclination_angle,
        surface_azimuth_angle=spec.azimuth_angle)

    # 太陽光線の入射角の余弦を計算
    cos_theta = cosine_sun_incidence_angle(s_h=s_h, s_w=s_w, s_s=s_s, w_z=w_z, w_w=w_w, w_s=w_s)

    # cos_thetaが誤差値未満の場合は計算しない（太陽が対象面の裏側にある）
    if cos_theta < common.get_error_value():
        distance_vertical = np.nan
        distance_horizontal = np.nan
    else:
        # 見かけの太陽高度（プロファイル角）の正接を計算
        tan_phi = tangent_profile_angle(s_h=s_h, s_w=s_w, s_s=s_s, cos_theta=cos_theta,
                                        surface_inclination_angle=spec.inclination_angle,
                                        surface_azimuth_angle=spec.azimuth_angle)

        # 面の太陽方位角の正接を計算
        tan_gamma = tangent_sun_azimuth_angle_of_surface(s_w=s_w, s_s=s_s, cos_theta=cos_theta,
                                                         surface_azimuth_angle=spec.azimuth_angle)

        # 点の影の垂直方向、水平方向の移動距離を計算
        distance_vertical = spec.depth * tan_phi
        distance_horizontal = spec.depth * tan_gamma

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

    # cos_thetaが誤差値未満の場合は計算しない（太陽が対象面の裏側にある）
    if cos_theta < common.get_error_value():
        tan_phi = np.nan
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

    # cos_thetaが誤差値未満の場合は計算しない（太陽が対象面の裏側にある）
    if cos_theta < common.get_error_value():
        tan_gamma = np.nan
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
