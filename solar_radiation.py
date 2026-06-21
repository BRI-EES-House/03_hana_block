import math
import common
import numpy as np


def get_direct_radiation(
        i_dn_ts: np.ndarray,
        h_ts: np.ndarray,
        a_ts: np.ndarray,
        p_beta: float,
        p_alpha: float
    ) -> np.ndarray:
    """傾斜面の直達日射量を求める関数

    Args:
        i_dn_ts: 法線面直達日射量, W/m2
        h_ts: 太陽高度角, rad
        a_ts: 太陽方位角, rad
        p_beta: 傾斜面傾斜角, rad
        p_alpha: 傾斜面方位角, rad
    Returns:
        傾斜面直達日射量, W/m2
    """

    # 傾斜面に対する太陽光線の入射角の余弦, degree
    cos_theta_ts = np.sin(h_ts) * np.cos(p_beta) + np.cos(h_ts) * np.sin(p_beta) * np.cos(a_ts - p_alpha)

    # 太陽光線の入射角の余弦が0より小さい場合は直達日射はない
    return np.where(
        cos_theta_ts < common.get_error_value(),
        0.0,
        i_dn_ts * cos_theta_ts
    )


def get_diffuse_radiation(horizontal_surface_sky_radiation: float, surface_inclination_angle: float) -> float:
    """傾斜面の天空日射量を求める関数

    :param horizontal_surface_sky_radiation:    水平面天空日射量, W/m2
    :param surface_inclination_angle:           傾斜面傾斜角, degree
    :return: 傾斜面天空日射量, W/m2
    """

    # 傾斜面の天空に対する形態係数
    shape_factor_of_surface = get_shape_factor_of_surface_to_sky(surface_inclination_angle)
    
    return horizontal_surface_sky_radiation * shape_factor_of_surface


def get_reflected_radiation(normal_surface_direct_radiation: float, horizontal_surface_sky_radiation: float,
                            solar_altitude: float, surface_inclination_angle: float) -> float:
    """
    傾斜面の反射日射量を求める関数

    :param normal_surface_direct_radiation:     法線面直達日射量, W/m2
    :param horizontal_surface_sky_radiation:    水平面天空日射量, W/m2
    :param solar_altitude:                      太陽高度角, degree
    :param surface_inclination_angle:           傾斜面傾斜角, degree
    :return: 傾斜面の反射日射量, W/m2
    """
    # 地面の日射に対する反射率（アルベド）
    surface_albedo = common.get_surface_albedo()
    # 傾斜面の地面に対する形態係数
    shape_factor_to_ground = 1.0 - get_shape_factor_of_surface_to_sky(surface_inclination_angle)
    # 水平面全天日射量
    horizontal_surface_global_radiation = get_horizontal_surface_global_radiation(
        normal_surface_direct_radiation, horizontal_surface_sky_radiation, solar_altitude)

    return surface_albedo * shape_factor_to_ground * horizontal_surface_global_radiation


def get_horizontal_surface_global_radiation(normal_surface_direct_radiation: float,
                                            horizontal_surface_sky_radiation: float, solar_altitude: float) -> float:
    """
    水平面全天日射量を求める関数
    :param normal_surface_direct_radiation:     法線面直達日射量, W/m2
    :param horizontal_surface_sky_radiation:    水平面天空日射量, W/m2
    :param solar_altitude:                      太陽高度角, degree
    :return: 水平面全天日射量, W/m2
    """
    return normal_surface_direct_radiation * np.sin(np.radians(solar_altitude)) + horizontal_surface_sky_radiation


def get_shape_factor_of_surface_to_sky(surface_inclination_angle: float) -> float:
    """
    傾斜面の天空に対する形態係数
    :param surface_inclination_angle: 傾斜面傾斜角, degree
    :return: 傾斜面の天空に対する形態係数
    """
    return (1.0 + math.cos(math.radians(surface_inclination_angle))) / 2.0
