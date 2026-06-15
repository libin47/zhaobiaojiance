from config import city as city_cfg
import datetime
area_lib = {
    "张家口": ["宣化", "下花园", "万全", "崇礼", "张北", "康保", "沽源", "尚义", "蔚县", "阳原", "怀安", "怀来", "涿鹿", "赤城", "塞北管理区", "察北管理区"],
    "雄安": ["雄县", "容城县", "安新县"]
}
def get_area_byname(name):
    if city_cfg not in area_lib.keys():
        return ""
    area_list = area_lib[city_cfg]
    for a in area_list:
        if a in name:
            return a
    return ""

class ContinuousDupBreaker:
    # 重复检查器
    def __init__(self, max_dup=3):
        self.max_dup = max_dup
        self.count = 0

    def check(self, is_dup: bool):
        if is_dup:
            self.count += 1
            if self.count >= self.max_dup:
                return True
        else:
            self.count = 0
        return False

def clear_date(date:datetime):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)