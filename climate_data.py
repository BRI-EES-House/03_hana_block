import pandas as pd
from dataclasses import dataclass
import numpy as np

from region import Region
import solar_radiation


@dataclass
class ClimateData:

    df: pd.DataFrame

    # 法線面直達日射量, W/m2
    i_dn_ts: np.ndarray
    # 水平面天空日射量, W/m2
    i_sky_ts: np.ndarray
    # 太陽高度角, deg.
    h_ts: np.ndarray
    # 太陽方位角, deg.
    a_ts: np.ndarray

    @classmethod
    def load(cls, calc_mode: str, region: Region):

        df = _get_climate_data(calc_mode=calc_mode, region=region)

        i_dn_ts = df['法線面直達日射量_W_m2'].to_numpy()
        i_sky_ts = df['水平面天空日射量_W_m2'].to_numpy()
        h_ts = df['太陽高度角_度'].to_numpy()
        a_ts = df['太陽方位角_度'].to_numpy()


        return ClimateData(
            df=df,
            i_dn_ts=i_dn_ts,
            i_sky_ts=i_sky_ts,
            h_ts=h_ts,
            a_ts=a_ts
        )

    def get_i_d_ts(self, p_beta: float, p_alpha) -> np.ndarray:
        """傾斜面直達日射量を計算する。

        Args:
            p_beta: 傾斜面の傾斜角, deg.
            p_alpha: 傾斜面の方位角, deg.

        Returns:
            傾斜面直達日射量, W/m2
        """

        return solar_radiation.get_direct_radiation(
            i_dn_ts=self.i_dn_ts,
            h_ts=np.radians(self.h_ts),
            a_ts=np.radians(self.a_ts),
            p_beta=np.radians(p_beta),
            p_alpha=np.radians(p_alpha)
        )
    
    def get_i_s_ts(self, p_beta: float) -> np.ndarray:
        """傾斜面天空日射量

        Args:
            p_beta: 傾斜面の傾斜角, deg.

        Returns:
            傾斜面天空日射量, W/m2
        """

        return solar_radiation.get_diffuse_radiation(
            horizontal_surface_sky_radiation=self.i_sky_ts,
            surface_inclination_angle=p_beta
        )
    
    def get_i_r_ts(self, p_beta: float) -> np.ndarray:
        """傾斜面反射日射量

        Args:
            p_beta: 傾斜面の傾斜角, deg.

        Returns:
            傾斜面反射日射量, W/m2
        """

        return solar_radiation.get_reflected_radiation(
            normal_surface_direct_radiation=self.i_dn_ts,
            horizontal_surface_sky_radiation=self.i_sky_ts,
            solar_altitude=self.h_ts,
            surface_inclination_angle=p_beta
        )


def _get_climate_data(calc_mode: str, region: Region) -> pd.DataFrame:
    """地域区分別の気象データを読み込む関数

    Args:
        calc_mode: 計算モード
        region: 地域の区分
    Returns
        指定した地域の気象データ（DataFrame）
    """

    # 地域区分別の気象データファイル名のリストを作成
    directory_name = 'climateData'
    csv_file_name = 'climateData_'

    # CSVファイルを読み込む
    df = pd.read_csv(directory_name + '/' + csv_file_name + region.value + '.csv', encoding="shift-jis")

    # 不要な列を削除
    #df = df.drop("Unnamed: 10", axis=1)

    # 列名を変更（"["や"/"があるとうまくデータを扱えないため）
    df = df.rename(
        columns={'外気温[℃]': '外気温_degree', '外気絶対湿度 [kg/kgDA]': '外気絶対湿度_kg_kgDA',
                 '法線面直達日射量 [W/m2]': '法線面直達日射量_W_m2', '水平面天空日射量 [W/m2]': '水平面天空日射量_W_m2',
                 '水平面夜間放射量 [W/m2]': '水平面夜間放射量_W_m2', '太陽高度角[度]': '太陽高度角_度',
                 '太陽方位角[度]': '太陽方位角_度'})

    df_target = pd.DataFrame()
    if calc_mode == 'analysis':
        df_target = df
    elif calc_mode == 'mesh':
        # メッシュ法の場合、計算時間が長いため、ここでは春分、夏至、秋分、冬至のみに絞る

        # データ抽出日の設定
        target_dates = {
            'spring': {'月': 3, '日': 23, 'color': 'g'},
            'summer': {'月': 6, '日': 22, 'color': 'r'},
            'autumn': {'月': 9, '日': 21, 'color': 'y'},
            'winter': {'月': 12, '日': 22, 'color': 'b'}
        }

        # 抽出データを用意
        for key, value in target_dates.items():
            df_abstract = df.query('月 == ' + str(value['月']) + ' & 日 == ' + str(value['日']))
            df_target = pd.concat([df_target, df_abstract])

    return df_target
