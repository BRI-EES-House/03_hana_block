import pandas as pd
import common
import solar_radiation
import distance_point_shadow
import transmission_rate_base
import transmission_rate_diffused_light
import transmission_rate_base_mesh_method


def case_study_single():
    """
    単一開口部の場合の花ブロックの総合透過率試算

    :param なし
    :return: なし
    """

    # 計算モードの設定（analysis:解析法  ,mesh:メッシュ法）
    calc_mode = 'analysis'

    # 四角形の場合
    spec = common.HanaBlockSpec(
        type='square', depth=100, inclination_angle=90, azimuth_angle=0, width=136.0, height=136.0)
    total_transmission_rate(case_name='01', calc_mode=calc_mode, spec=spec)

    # 円形の場合
    spec = common.HanaBlockSpec(
        type='circle', depth=100, inclination_angle=90, azimuth_angle=0, radius=136.0/2.0)
    total_transmission_rate(case_name='02', calc_mode=calc_mode, spec=spec)

    # 三角形の場合（その1）
    spec = common.HanaBlockSpec(
        type='triangle', depth=100, inclination_angle=90, azimuth_angle=0,
        points={'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 130)})
    total_transmission_rate(case_name='03', calc_mode=calc_mode, spec=spec)

    # 三角形の場合（その2）
    spec = common.HanaBlockSpec(
        type='triangle', depth=150, inclination_angle=90, azimuth_angle=0,
        points={'peak_a': (0, 0), 'peak_b': (130, 130), 'peak_c': (0, 130)})
    total_transmission_rate(case_name='04', calc_mode=calc_mode, spec=spec)


def total_transmission_rate(case_name: str, calc_mode: str, spec: common.HanaBlockSpec):
    """
    花ブロックの総合透過率を計算し、結果をCSVファイルに出力する

    :param case_name:   検討ケース名称
    :param calc_mode:   計算モード
    :param spec:        花ブロックの仕様
    :return: なし
    """

    # 拡散光の透過率を計算
    tau_s = transmission_rate_diffused_light.diffused_light_transmission_rate(spec=spec)

    # 地域区分のリストを設定
    regions = [1, 6, 8]

    # 地域区分ループ
    for region in regions:

        # 1年間の気象データを取得
        df_climate = get_climate_data(region)

        # 方位リストを取得
        directions = common.get_direction_list()

        # 方位ループ
        for direction, angle in directions.items():

            # 方位角を設定
            spec.azimuth_angle = angle

            # 計算結果格納用配列を用意
            df = df_climate.loc[:, ['月', '日', '時', '太陽高度角_度', '太陽方位角_度']]
            total_solar_radiation = []          # 傾斜面日射量, W/m2
            direct_solar_radiation = []         # 傾斜面直達日射量, W/m2
            diffuse_solar_radiation = []        # 傾斜面天空日射量, W/m2
            reflected_solar_radiation = []      # 傾斜面の反射日射量, W/m2
            direct_transmission_rate = []           # 直達光の透過率, -
            diffused_light_transmission_rate = []   # 拡散光の透過率, -
            total_transmission_rate = []            # 総合透過率, -

            # 気象データの行ループ
            for row in df_climate.itertuples():

                # 傾斜面直達日射量を計算
                i_d_t = solar_radiation.get_direct_radiation(
                    normal_surface_direct_radiation=row.法線面直達日射量_W_m2,
                    solar_altitude=row.太陽高度角_度,
                    solar_azimuth=row.太陽方位角_度,
                    surface_inclination_angle=spec.inclination_angle,
                    surface_azimuth_angle=spec.azimuth_angle
                )

                # 傾斜面天空日射量を計算
                i_s_t = solar_radiation.get_diffuse_radiation(
                    horizontal_surface_sky_radiation=row.水平面天空日射量_W_m2,
                    surface_inclination_angle=spec.inclination_angle
                )

                # 傾斜面反射日射量を計算
                i_r_t = solar_radiation.get_reflected_radiation(
                    normal_surface_direct_radiation=row.法線面直達日射量_W_m2,
                    horizontal_surface_sky_radiation=row.水平面天空日射量_W_m2,
                    solar_altitude=row.太陽高度角_度,
                    surface_inclination_angle=spec.inclination_angle
                )

                # 傾斜面日射量を計算
                i_total = i_d_t + i_s_t + i_r_t

                # 点の影の垂直方向、水平方向の移動距離を計算
                d_y, d_x = distance_point_shadow.distance_of_points_shadow(
                    spec=spec,
                    sun_altitude=row.太陽高度角_度,
                    sun_azimuth_angle=row.太陽方位角_度
                )

                # 花ブロックの直達光の透過率を計算
                # 計算モードが「analysis（解析法）」の場合
                if calc_mode == 'analysis':
                    if spec.type == 'square':
                        tau_d_t = transmission_rate_base.base_transmission_rate_square(
                            spec=spec, distance_vertical=d_y, distance_horizontal=d_x
                        )
                    elif spec.type == 'circle':
                        tau_d_t = transmission_rate_base.base_transmission_rate_circle(
                            spec=spec, distance_vertical=d_y, distance_horizontal=d_x
                        )
                    elif spec.type == 'triangle':
                        tau_d_t = transmission_rate_base.base_transmission_rate_triangle(
                            spec=spec, distance_vertical=d_y, distance_horizontal=d_x
                        )
                    else:
                        raise ValueError('花ブロックのタイプ「' + spec.type + '」は対象外です')
                # 計算モードが「mesh（メッシュ法）」の場合
                elif calc_mode == 'mesh':
                    tau_d_t = transmission_rate_base_mesh_method.base_transmission_rate(
                        spec=spec, distance_vertical=d_y, distance_horizontal=d_x
                    )
                else:
                    raise ValueError('計算モード「' + calc_mode + '」は対象外です')

                # 花ブロックの直達日射に対する透過率を計算（傾斜面直達日射量が誤差値未満の場合は計算しない）
                if i_d_t < common.get_error_value():
                    tau_d_t = 0.0
                else:
                    tau_d_t = (i_d_t * tau_d_t) / i_d_t

                # 花ブロックの総合透過率を計算（傾斜面日射量が誤差値未満の場合は計算しない）
                if i_total < common.get_error_value():
                    tau_total = 0.0
                else:
                    tau_total = (i_d_t * tau_d_t + i_s_t * tau_s + i_r_t * tau_s) / i_total

                # 計算結果を配列に格納
                total_solar_radiation.append(i_total)
                direct_solar_radiation.append(i_d_t)
                diffuse_solar_radiation.append(i_s_t)
                reflected_solar_radiation.append(i_r_t)
                direct_transmission_rate.append(tau_d_t)
                diffused_light_transmission_rate.append(tau_s)
                total_transmission_rate.append(tau_total)

            # 計算結果をDataFrameに追加
            df['total_solar_radiation'] = total_solar_radiation
            df['direct_solar_radiation'] = direct_solar_radiation
            df['diffuse_solar_radiation'] = diffuse_solar_radiation
            df['reflected_solar_radiation'] = reflected_solar_radiation
            df['direct_transmission_rate'] = direct_transmission_rate
            df['diffused_light_transmission_rate'] = diffused_light_transmission_rate
            df['total_transmission_rate'] = total_transmission_rate

            # CSVファイル出力
            df.to_csv(
                'result' + '/' + calc_mode + '_case' + case_name + '_' + 'region' + str(region) + '_' + direction + '.csv',
                encoding="shift-jis"
            )


def get_climate_data(region: int) -> pd.DataFrame:
    """
    地域区分別の気象データを読み込む関数

    :param region:  地域区分の番号
    :return: 指定した地域の気象データ（DataFrame）
    """

    # 地域区分別の気象データファイル名のリストを作成
    directory_name = 'climateData'
    csv_file_name = 'climateData_'

    # CSVファイルを読み込む
    df = pd.read_csv(directory_name + '/' + csv_file_name + str(region) + '.csv', encoding="shift-jis")

    # 不要な列を削除
    df = df.drop("Unnamed: 10", axis=1)

    # 列名を変更（"["や"/"があるとうまくデータを扱えないため）
    df = df.rename(
        columns={'外気温[℃]': '外気温_degree', '外気絶対湿度 [kg/kgDA]': '外気絶対湿度_kg_kgDA',
                 '法線面直達日射量 [W/m2]': '法線面直達日射量_W_m2', '水平面天空日射量 [W/m2]': '水平面天空日射量_W_m2',
                 '水平面夜間放射量 [W/m2]': '水平面夜間放射量_W_m2', '太陽高度角[度]': '太陽高度角_度',
                 '太陽方位角[度]': '太陽方位角_度'})

    return df


if __name__ == '__main__':

    case_study_single()
