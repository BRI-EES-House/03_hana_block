import pandas as pd
import numpy as np
import common
import solar_radiation
import distance_point_shadow
import transmission_rate_base
import transmission_rate_diffused_light
import transmission_rate_total


def parametric_studies():

    # 計算モードの設定（analysis:解析法  ,mesh:メッシュ法）
    calc_mode = 'analysis'

    # 地域区分のリストを設定
    regions = [1, 6, 8]

    # 方位リストを設定
    if calc_mode == 'analysis':
        directions = common.get_direction_list()
    elif calc_mode == 'mesh':
        # メッシュ法は計算時間が長いため、検証用に4方位に絞る
        directions = {
            'N': 180.0,
            'E': -90.0,
            'S': 0.0,
            'W': 90.0
        }
    else:
        raise ValueError('計算モード「' + calc_mode + '」は対象外です')

    # 計算条件のCSVファイルを読み込む
    df_conditions = pd.read_csv('parametric_studies_triangle.csv', index_col=0, encoding="shift-jis")

    for index, row in df_conditions.iterrows():

        # ケース番号を設定
        case_name = str(index + 1)

        # if row['type'] == 'triangle':

        opening_specs = []

        # 開口部の仕様を設定
        #TODO: CSVファイルの開口部の数に応じてFor文の繰り返し回数を変更する
        for opening_count in range(4):

            # print(pd.isna(row[str(opening_count + 1) + '_type']))

            if not pd.isna(row[str(opening_count + 1) + '_type']):
            # if row[str(opening_count + 1) + '_type'] != nan:
                if row[str(opening_count + 1) + '_type'] == 'triangle':
                    opening_specs.append(
                        common.HanaBlockSpec(
                            type=row[str(opening_count + 1) + '_type'],
                            depth=row['depth'],
                            inclination_angle=90,
                            azimuth_angle=0,
                            width=row[str(opening_count + 1) + '_width'],
                            height=row[str(opening_count + 1) + '_height'],
                            radius=row[str(opening_count + 1) + '_radius'],
                            points={'peak_a': (row[str(opening_count + 1) + '_peak_a_x'],
                                               row[str(opening_count + 1) + '_peak_a_y']),
                                    'peak_b': (row[str(opening_count + 1) + '_peak_b_x'],
                                               row[str(opening_count + 1) + '_peak_b_y']),
                                    'peak_c': (row[str(opening_count + 1) + '_peak_c_x'],
                                               row[str(opening_count + 1) + '_peak_c_y'])}
                        )
                    )
                else:
                    opening_specs.append(
                        common.HanaBlockSpec(
                            type=row[str(opening_count + 1) + '_type'],
                            depth=row['depth'],
                            inclination_angle=90,
                            azimuth_angle=0,
                            width=row[str(opening_count + 1) + '_width'],
                            height=row[str(opening_count + 1) + '_height'],
                            radius=row[str(opening_count + 1) + '_radius']
                        )
                    )

        # 花ブロック全体の仕様を設定
        hana_block = common.HanaBlock(opening_specs=opening_specs, number_of_openings=row['number_of_openings'],
                                      depth=row['depth'], inclination_angle=90, azimuth_angle=0,
                                      front_width=row['front_width'], front_height=row['front_height'])

        # 透過率を計算
        calc_transmission_rate(
                case_name=case_name, calc_mode=calc_mode, regions=regions, directions=directions, hana_block=hana_block)

        calc_seasonal_transmission_rate(case_name=case_name, calc_mode=calc_mode,
                                        regions=regions, directions=directions, hana_block=hana_block)


def calc_transmission_rate(case_name: str, calc_mode: str, regions: [int], directions: dict,
                            hana_block: common.HanaBlock):
    """
    花ブロックの総合透過率を計算し、結果をCSVファイルに出力する

    :param case_name:   検討ケース名称
    :param calc_mode:   計算モード
    :param regions:     地域区分番号（リスト）
    :param directions:  方位名称と方位角のリスト
    :param hana_block:  花ブロック仕様
    :return: なし
    """

    # 各開口部の天空光の透過率、地物反射光の透過率を計算
    # tau_s = [""] * 3
    # tau_r = [""] * 3
    # TODO: CSVファイルの開口部の数に応じてFor文の繰り返し回数を変更する
    # for spec_count in range(3):
    #
    #     if spec_count < hana_block.number_of_openings - 1:
    #         # 天空光の透過率を計算
    #         tau_s[spec_count] = transmission_rate_diffused_light.diffused_light_transmission_rate(
    #             calc_target='sky', spec=hana_block.opening_specs[spec_count])
    #         tau_r[spec_count] = transmission_rate_diffused_light.diffused_light_transmission_rate(
    #         # 地物反射光の透過率を計算
    #             calc_target='reflected', spec=hana_block.opening_specs[spec_count])

    tau_s = []
    tau_r = []
    for spec_count in range(4):
    # for spec_count in range(hana_block.number_of_openings):

        if spec_count < hana_block.number_of_openings:
            # 天空光の透過率を計算
            tau_s.append(transmission_rate_diffused_light.diffused_light_transmission_rate(
                calc_target='sky', spec=hana_block.opening_specs[spec_count]))

            # 地物反射光の透過率を計算
            tau_r.append(transmission_rate_diffused_light.diffused_light_transmission_rate(
                calc_target='reflected', spec=hana_block.opening_specs[spec_count]))
        else:
            tau_s.append(np.nan)
            tau_r.append(np.nan)


    # 地域区分ループ
    for region in regions:

        # 1年間の気象データを取得
        df_climate = transmission_rate_total.get_climate_data(region=region, calc_mode=calc_mode)

        # 方位ループ
        for direction, angle in directions.items():

            # 方位角を設定
            hana_block.azimuth_angle = angle

            # 計算結果格納用配列を用意
            df = df_climate.loc[:, ['月', '日', '時', '太陽高度角_度', '太陽方位角_度']]
            total_solar_radiation = []          # 傾斜面日射量, W/m2
            direct_solar_radiation = []         # 傾斜面直達日射量, W/m2
            sky_solar_radiation = []            # 傾斜面天空日射量, W/m2
            reflected_solar_radiation = []      # 傾斜面反射日射量, W/m2
            direct_solar_radiation_transed = []     # 傾斜面透過直達日射量, W
            sky_solar_radiation_transed = []        # 傾斜面透過天空日射量, W
            reflected_solar_radiation_transed = []  # 傾斜面透過反射日射量, W
            front_total_solar_radiation = []        # 花ブロック前面の傾斜面日射量, W
            # direct_transmission_rate_1 = []     # 直達光の透過率, -
            # sky_light_transmission_rate_1 = []  # 拡散光の透過率, -
            # total_transmission_rate = []            # 総合透過率, -

            # 結果格納用の辞書型を用意
            dict_results = {'direct_transmission_rate_1': [], 'sky_light_transmission_rate_1': [], 'reflected_light_transmission_rate_1': [],
                            'direct_transmission_rate_2': [], 'sky_light_transmission_rate_2': [], 'reflected_light_transmission_rate_2': [],
                            'direct_transmission_rate_3': [], 'sky_light_transmission_rate_3': [], 'reflected_light_transmission_rate_3': [],
                            'direct_transmission_rate_4': [], 'sky_light_transmission_rate_4': [], 'reflected_light_transmission_rate_4': []
                            }

            # 気象データの行ループ
            for row in df_climate.itertuples():

                # 傾斜面直達日射量_W/m2を計算
                i_d_t = solar_radiation.get_direct_radiation(
                    normal_surface_direct_radiation=row.法線面直達日射量_W_m2,
                    solar_altitude=row.太陽高度角_度,
                    solar_azimuth=row.太陽方位角_度,
                    surface_inclination_angle=hana_block.inclination_angle,
                    surface_azimuth_angle=hana_block.azimuth_angle
                )

                # 傾斜面天空日射量_W/m2を計算
                i_s_t = solar_radiation.get_diffuse_radiation(
                    horizontal_surface_sky_radiation=row.水平面天空日射量_W_m2,
                    surface_inclination_angle=hana_block.inclination_angle
                )

                # 傾斜面反射日射量_W/m2を計算
                i_r_t = solar_radiation.get_reflected_radiation(
                    normal_surface_direct_radiation=row.法線面直達日射量_W_m2,
                    horizontal_surface_sky_radiation=row.水平面天空日射量_W_m2,
                    solar_altitude=row.太陽高度角_度,
                    surface_inclination_angle=hana_block.inclination_angle
                )

                # 傾斜面日射量を計算
                i_total = i_d_t + i_s_t + i_r_t

                # # 計算結果を配列に格納
                # total_solar_radiation.append(i_total)
                # direct_solar_radiation.append(i_d_t)
                # sky_solar_radiation.append(i_s_t)
                # reflected_solar_radiation.append(i_r_t)

                # 点の影の垂直方向、水平方向の移動距離を計算
                d_y, d_x = distance_point_shadow.distance_of_points_shadow(
                    surface_inclination_angle=hana_block.inclination_angle,
                    surface_azimuth_angle=hana_block.azimuth_angle,
                    depth=hana_block.depth,
                    sun_altitude=row.太陽高度角_度,
                    sun_azimuth_angle=row.太陽方位角_度
                )

                i_d_transed = 0.0
                i_s_transed = 0.0
                i_r_transed = 0.0

                # 開口部別のループ
                for spec_count in range(4):
                # for spec_count in range(hana_block.number_of_openings):

                    if spec_count < hana_block.number_of_openings:

                        # 花ブロックの直達光の透過率を計算
                        if hana_block.opening_specs[spec_count].type == 'square':
                            tau_d_t = transmission_rate_base.base_transmission_rate_square(
                                spec=hana_block.opening_specs[spec_count], distance_vertical=d_y, distance_horizontal=d_x
                            )
                        elif hana_block.opening_specs[spec_count].type == 'circle':
                            tau_d_t = transmission_rate_base.base_transmission_rate_circle(
                                spec=hana_block.opening_specs[spec_count], distance_vertical=d_y, distance_horizontal=d_x
                            )
                        elif hana_block.opening_specs[spec_count].type == 'triangle':
                            tau_d_t = transmission_rate_base.base_transmission_rate_triangle(
                                spec=hana_block.opening_specs[spec_count], distance_vertical=d_y, distance_horizontal=d_x
                            )
                        else:
                            raise ValueError('花ブロックのタイプ「' + hana_block.opening_specs[spec_count].type + '」は対象外です')

                        # 花ブロックの直達日射に対する透過率を計算（傾斜面直達日射量が誤差値未満の場合は計算しない）
                        if i_d_t < common.get_error_value():
                            tau_d_t = 0.0
                        else:
                            tau_d_t = (i_d_t * tau_d_t) / i_d_t

                        # 傾斜面透過直達日射量、傾斜面透過天空日射量、傾斜面透過反射日射量を計算
                        i_d_transed = i_d_transed + (
                                i_d_t * tau_d_t * hana_block.opening_specs[spec_count].area * (10 ** -6)
                        )
                        i_s_transed = i_s_transed + (
                                    i_s_t * tau_s[spec_count] * hana_block.opening_specs[spec_count].area * (10 ** -6)
                        )
                        i_r_transed = i_r_transed + (
                                    i_r_t * tau_r[spec_count] * hana_block.opening_specs[spec_count].area * (10 ** -6)
                        )

                        # 計算結果を配列に格納
                        dict_results['direct_transmission_rate_' + str(spec_count + 1)].append(tau_d_t)
                        dict_results['sky_light_transmission_rate_' + str(spec_count + 1)].append(tau_s[spec_count])
                        dict_results['reflected_light_transmission_rate_' + str(spec_count + 1)].append(
                            tau_r[spec_count])

                    else:
                        # 配列に格納
                        dict_results['direct_transmission_rate_' + str(spec_count + 1)].append(np.nan)
                        dict_results['sky_light_transmission_rate_' + str(spec_count + 1)].append(np.nan)
                        dict_results['reflected_light_transmission_rate_' + str(spec_count + 1)].append(np.nan)

                    # # 傾斜面透過直達日射量、傾斜面透過天空日射量、傾斜面透過反射日射量を計算
                    # i_d_transed = i_d_transed + (i_d_t * tau_d_t * hana_block.opening_specs[spec_count].area)
                    # i_s_transed = i_s_transed + (i_s_t * tau_s[spec_count] * hana_block.opening_specs[spec_count].area)
                    # i_r_transed = i_r_transed + (i_r_t * tau_r[spec_count] * hana_block.opening_specs[spec_count].area)

                # 花ブロック前面の傾斜面日射量を計算
                i_front_total = (i_d_t + i_s_t + i_r_t) * hana_block.front_area * (10 ** -6)

                # 計算結果を配列に格納
                total_solar_radiation.append(i_total)
                direct_solar_radiation.append(i_d_t)
                sky_solar_radiation.append(i_s_t)
                reflected_solar_radiation.append(i_r_t)
                direct_solar_radiation_transed.append(i_d_transed)
                sky_solar_radiation_transed.append(i_s_transed)
                reflected_solar_radiation_transed.append(i_r_transed)
                front_total_solar_radiation.append(i_front_total)

                # direct_solar_radiation_transed = []
                # sky_solar_radiation_transed = []  # 傾斜面透過天空日射量, W
                # reflected_solar_radiation_transed = []  # 傾斜面透過反射日射量, W
                # front_total_solar_radiation = []  # 花ブロック前面の傾斜面日射量, W

                # # 花ブロックの総合透過率を計算（傾斜面日射量が誤差値未満の場合は計算しない）
                # if i_total < common.get_error_value():
                #     tau_total = 0.0
                # else:
                #     tau_total = (i_d_t * tau_d_t + i_s_t * tau_s + i_r_t * tau_s) / i_total

                # direct_transmission_rate.append(tau_d_t)
                # diffused_light_transmission_rate.append(tau_s)
                # total_transmission_rate.append(tau_total)

            # 計算結果をDataFrameに追加
            df['total_solar_radiation'] = total_solar_radiation
            df['direct_solar_radiation'] = direct_solar_radiation
            df['sky_solar_radiation'] = sky_solar_radiation
            df['reflected_solar_radiation'] = reflected_solar_radiation

            # 辞書型をDataFrameに変換
            df_result = pd.DataFrame.from_dict(dict_results, orient="columns")

            # 透過率の計算結果を統合
            for column_name, item in df_result.iteritems():
                df[column_name] = item

            # df.merge(df_result)

            df['direct_solar_radiation_transed'] = direct_solar_radiation_transed
            df['sky_solar_radiation_transed'] = sky_solar_radiation_transed
            df['reflected_solar_radiation_transed'] = reflected_solar_radiation_transed
            df['front_total_solar_radiation'] = front_total_solar_radiation

            # df['direct_transmission_rate'] = direct_transmission_rate
            # df['diffused_light_transmission_rate'] = diffused_light_transmission_rate
            # df['total_transmission_rate'] = total_transmission_rate

            # CSVファイル出力
            df.to_csv(
                'parametric_study' + '/' + calc_mode + '_case' + case_name + '_' + 'region' + str(region)
                + '_' + direction + '.csv', encoding="shift-jis"
            )


def calc_seasonal_transmission_rate(case_name: str, calc_mode: str, regions: [int], directions: dict,
                                    hana_block: common.HanaBlock):
    """
        花ブロックの期間平均透過率を計算し、CSVファイルに出力する

        :param case_name:   検討ケース名称
        :param calc_mode:   計算モード
        :param regions:     地域区分番号（リスト）
        :param directions:  方位名称と方位角のリスト
        :param hana_block:  花ブロック仕様
        :return: なし
    """

    # 結果格納用の辞書型を用意
    dict_results = {'no': [], 'type': [], 'front_width': [], 'front_height': [], 'depth': [],
                    # '1_width': [], 	'1_height': [], '2_width': [], 	'2_height': [],
                    # '3_width': [], '3_height': [], '4_width': [], '4_height': [],
                    'partition_area_rate': [], 'opening_area_rate': [],
                    'region': [], 'direction': [], 'tau_total_c': [], 'tau_total_h': []
                    }
    # dict_results = {'no': [], 'type': [], 'width': [], 'height': [], 'front_width': [],
    #                 'front_height': [], 'radius': [], 'depth': [], 'perimeter': [],
    #                 'partition_area_rate': [], 'region': [], 'direction': [], 'tau_total_c': [], 'tau_total_h': []
    #                 }

    # 地域区分ループ
    for region in regions:

        # 方位ループ
        for direction, angle in directions.items():

            filename = 'parametric_study' + '/' + calc_mode + '_case' + case_name + '_' + 'region' + str(
                    region) + '_' + direction + '.csv'
            df_all = pd.read_csv(filename, index_col=0, encoding="shift-jis")

            # 冷房期間の総合透過率を計算
            tau_total_c = get_seasonal_transmission_rate(df_all.query('月 >= ' + str(6) + ' & 月 <= ' + str(9)))

            # 暖房期間の総合透過率を計算
            tau_total_h = get_seasonal_transmission_rate(df_all.query('月 <= ' + str(3) + ' | 月 >= ' + str(11)))

            # 計算結果を配列に格納
            dict_results['no'].append(case_name)
            dict_results['type'].append(hana_block.opening_specs[0].type)
            dict_results['front_width'].append(hana_block.front_width)
            dict_results['front_height'].append(hana_block.front_height)
            # dict_results['radius'].append(spec.radius)
            dict_results['depth'].append(hana_block.depth)
            # dict_results['1_width'].append(hana_block.opening_specs[0].width)
            # dict_results['1_height'].append(hana_block.opening_specs[0].height)
            # dict_results['2_width'].append(hana_block.opening_specs[1].width)
            # dict_results['2_height'].append(hana_block.opening_specs[1].height)
            # dict_results['3_width'].append(hana_block.opening_specs[2].width)
            # dict_results['3_height'].append(hana_block.opening_specs[2].height)
            # dict_results['4_width'].append(hana_block.opening_specs[3].width)
            # dict_results['4_height'].append(hana_block.opening_specs[3].height)
            # dict_results['perimeter_total'].append(get_perimeter_total(hana_block))
            dict_results['partition_area_rate'].append(get_partition_area_rate(hana_block))
            dict_results['opening_area_rate'].append(get_opening_area_rate(hana_block))
            dict_results['region'].append(region)
            dict_results['direction'].append(direction)
            dict_results['tau_total_c'].append(tau_total_c)
            dict_results['tau_total_h'].append(tau_total_h)

    # 辞書型をDataFrameに変換
    df_result = pd.DataFrame.from_dict(dict_results, orient="columns")

    # CSVファイル出力
    df_result.to_csv(
        'parametric_study' + '/parametric_study_result' + '_case' + case_name + '.csv', encoding="shift-jis"
    )


def get_seasonal_transmission_rate(df):
    """
        花ブロックの期間平均透過率を計算

        :param df:   時刻別の透過率の計算結果
        :return: 花ブロックの期間平均透過率, -
    """

    # df['solar_transmitted'] = df.loc[:, 'direct_solar_radiation'] * df.loc[:, 'direct_transmission_rate'] + \
    #                           df.loc[:, 'diffuse_solar_radiation'] * df.loc[:, 'diffused_light_transmission_rate'] + \
    #                           df.loc[:, 'reflected_solar_radiation'] * df.loc[:, 'diffused_light_transmission_rate']
    # df['solar_total'] = df.loc[:, 'direct_solar_radiation'] + df.loc[:, 'diffuse_solar_radiation'] + \
    #                     df.loc[:, 'reflected_solar_radiation']

    sum_solar_transmitted = df['direct_solar_radiation_transed'].sum() + \
                            df['sky_solar_radiation_transed'].sum() + df['reflected_solar_radiation_transed'].sum()
    sum_solar_total = df['front_total_solar_radiation'].sum()
    transmission_rate = sum_solar_transmitted / sum_solar_total

    return transmission_rate


# def get_perimeter_total(hana_block: common.HanaBlock):
#     """
#         花ブロックの周長を計算
#
#         :param hana_block:  花ブロック仕様
#         :return: 花ブロックの周長, mm
#     """
#
#     # 花ブロックの周長の合計を計算
#     perimeter_total = 0.0
#     for spec_count in range(4):
#         if spec_count < hana_block.number_of_openings:
#             perimeter_total = perimeter_total + hana_block.opening_specs[0].perimeter
#
#     return perimeter_total


def get_partition_area_rate(hana_block: common.HanaBlock):
    """
        花ブロック仕切り面積の比を計算

        :param hana_block:  花ブロック仕様
        :return: 花ブロック仕切り面積の比, mm
    """

    # 花ブロックの周長の合計を計算
    perimeter_total = 0.0
    for spec_count in range(4):
        if spec_count < hana_block.number_of_openings:
            perimeter_total = perimeter_total + hana_block.opening_specs[0].perimeter

    return (perimeter_total * hana_block.depth) / (hana_block.front_area * 2.0)


def get_opening_area_rate(hana_block: common.HanaBlock):
    """
        花ブロックの開口面積の比を計算

        :param hana_block:  花ブロック仕様
        :return: 花ブロック仕切り面積の比, mm
    """

    opening_area_total = 0.0
    for spec_count in range(4):
        if spec_count < hana_block.number_of_openings:
            opening_area_total = opening_area_total + hana_block.opening_specs[0].area

    return opening_area_total / hana_block.front_area


if __name__ == '__main__':

    # specs = []
    #
    # # 三角形の場合（その1）
    # specs.append(common.HanaBlockSpec(
    #     type='triangle', depth=100, inclination_angle=90, azimuth_angle=0,
    #     points={'peak_a': (0, 0), 'peak_b': (0, 130), 'peak_c': (130, 130)}
    # ))
    #
    # # 三角形の場合（その2）
    # specs.append(common.HanaBlockSpec(
    #     type='triangle', depth=150, inclination_angle=90, azimuth_angle=0,
    #     points={'peak_a': (0, 0), 'peak_b': (130, 130), 'peak_c': (0, 130)}
    # ))
    #
    # # hana_block = common.HanaBlock(opening_specs=specs, front_width=190.0, front_height=190.0)
    #
    # print(hana_block.opening_specs[0].type)

    x = np.arange(start=0.0, stop=3.1, step=0.1, dtype=float)
    print(x)

    parametric_studies()
