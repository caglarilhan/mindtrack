from pytrends.request import TrendReq
import pandas as pd

class GoogleTrendsService:
    def __init__(self, hl="tr-TR", tz=180):
        self.pytrends = TrendReq(hl=hl, tz=tz)

    def get_interest_over_time(self, keyword, timeframe="now 7-d", geo="TR"):
        self.pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo, gprop='')
        data = self.pytrends.interest_over_time()
        if not data.empty:
            return data[[keyword]].reset_index().to_dict(orient="records")
        else:
            return []

    def get_trend_score(self, keyword, timeframe="now 7-d", geo="TR"):
        data = self.get_interest_over_time(keyword, timeframe, geo)
        if data:
            # Son 3 günün ortalaması ile önceki 3 günün ortalamasını karşılaştır
            scores = [d[keyword] for d in data]
            if len(scores) >= 6:
                recent = sum(scores[-3:]) / 3
                prev = sum(scores[:3]) / 3
                change = (recent - prev) / prev if prev > 0 else 0
                return {"keyword": keyword, "recent_avg": recent, "prev_avg": prev, "change": change}
            else:
                return {"keyword": keyword, "trend_data": scores}
        else:
            return {"keyword": keyword, "trend_data": []} 