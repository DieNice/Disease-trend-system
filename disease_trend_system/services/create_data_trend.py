from numpy.typing import ArrayLike
from pandas import DataFrame


class TrendDetector:
    """Класс фильтрующий тренды

    """

    def _is_desc_sorted(self, arr: ArrayLike) -> bool:
        if len(arr) == 1:
            return False
        for i in range(arr.size-1):
            if arr[i+1] > arr[i]:
                return False
        return True

    def __init__(self, trend_threshold: int) -> None:
        self.threshold = trend_threshold

    def execute(self, df: DataFrame) -> DataFrame:
        hashes = df["symptom_complex_hash"].unique()
        bad_hashes = []
        for iter_hash in hashes:
            tmp_df = df[df["symptom_complex_hash"] == iter_hash]
            tmp_df.sort_values(by=["date"], ascending=True, inplace=True)
            if len(tmp_df) < self.threshold:
                bad_hashes.append(iter_hash)
                continue
            if self._is_desc_sorted(tmp_df.total_number.to_numpy()):
                bad_hashes.append(iter_hash)
        return df[~df["symptom_complex_hash"].isin(bad_hashes)]
