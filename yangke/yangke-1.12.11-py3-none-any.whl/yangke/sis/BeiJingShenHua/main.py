import copy
from yangke.performance.iapws97 import get_h_by_pt
from yangke.sis.BeiJingShenHua.tags import TagsRead, TagsWrite
from yangke.sis.dll_file import read_data, get_tag_value, init_write_sis, init_dbp_api
import pandas as pd
from yangke.base import interpolate_nd, interpolate_value_complex, execute_function_by_interval


def Q_热井出水(F_凝结水1, F_凝结水2, F_减温水至杂项, P_热井出水, T_热井出水):
    F_热井出水 = F_凝结水1 + F_凝结水2 - F_减温水至杂项 + 24
    H_热井出水 = get_h_by_pt(P_热井出水, T_热井出水)
    return F_热井出水 * H_热井出水


def load_db(db_path=r"D:\SIS_DB_20210918.xlsx"):
    _ = pd.read_excel(db_path)
    _.dropna(how="any", axis=1)
    data_total = {}
    for 循泵方式 in ["A", "B", "C", "D", "E", "F", "G", "H"]:
        for 风机数量 in [3, 4, 5, 6, 7, 8]:
            value = _[_["循泵方式"] == 循泵方式]
            value = value[value["机力塔数量"] == 风机数量]
            data_total.update({
                f"{循泵方式}{风机数量}": copy.deepcopy(value)
            })
    return data_total


init_write_sis(ip="", port=3399, user="admin", passwd_str="admin")
data = load_db()
inter_func = {}
power_cold = {
    "A": 5989.7,
    "B": 5174.7,
    "C": 4303.5,
    "D": 3450.5,
    "E": 2762.6,
    "F": 2040.5,
    "G": 1904.0,
    "H": 836.7,
    "3": 670.7,
    "4": 890.8,
    "5": 1115.8,
    "6": 1324.7,
    "7": 1525.1,
    "8": 1730.1
}
for 循泵方式 in ["A", "B", "C", "D", "E", "F", "G", "H"]:
    for 风机数量 in [3, 4, 5, 6, 7, 8]:
        state = f"{循泵方式}{风机数量}"
        df = data[state]
        inter_func = interpolate_nd(dataframe=df, df_x_titles=["凝汽器热负荷", "温度", "湿度"], df_y_title=["背压"])
        inter_func.update({state: inter_func})
        power_cold.update({state: power_cold[循泵方式] + power_cold[str(风机数量)]})

Qc_C = [  # 凝汽器热负荷-微增出力系数
    [100, 1.7712],
    [150, 1.5629],
    [200, 1.3745],
    [250, 1.2062],
    [300, 1.0578],
    [350, 0.9295],
    [400, 0.8211],
    [450, 0.7328],
    [500, 0.6644],
    [550, 0.6161],
]

power_range = []  # 负荷波动阈值
t_range = []  # 温度波动阈值
heat_range = []  # 热负荷波动阈值


def optimize():
    """
    执行一次优化任务

    :return:
    """
    snapshot = read_data(TagsRead)
    Q_瞬时供水热量 = get_tag_value(snapshot, TagsRead.供热管道出水热量, 0)
    Q_瞬时回水热量 = get_tag_value(snapshot, TagsRead.供热管道回水热量, 0)
    Q_供热 = Q_瞬时供水热量 - Q_瞬时回水热量
    P_well_out = get_tag_value(snapshot, TagsRead.热井出水压力, 1.1)
    T_well_out = get_tag_value(snapshot, TagsRead.热井出水温度, 40)
    F_condense1 = get_tag_value(snapshot, TagsRead.凝结水流量1号炉, 10)
    F_condense2 = get_tag_value(snapshot, TagsRead.凝结水流量2号炉, 10)
    F_other = get_tag_value(snapshot, TagsRead.减温水至杂项流量, 0)
    Q_wellout = Q_热井出水(F_condense1, F_condense2, F_other, P_well_out, T_well_out)
    power_steam = get_tag_value(snapshot, TagsRead.发电机有功功率_steam, 300)
    power_shaft_steam = power_steam / 0.988 * 3600000  # 1MW=1MJ/s=1000kJ/s=1000*3600kJ/h
    Q_seal = 18502790  # 轴封漏汽热量；kJ/h
    P_lms1 = get_tag_value(snapshot, TagsRead.低压蒸汽压力1)
    T_lms1 = get_tag_value(snapshot, TagsRead.低压蒸汽温度1)
    F_lms1 = get_tag_value(snapshot, TagsRead.低压蒸汽流量1)
    H_lms1 = get_h_by_pt(P_lms1, T_lms1)
    P_lms2 = get_tag_value(snapshot, TagsRead.低压蒸汽压力2)
    T_lms2 = get_tag_value(snapshot, TagsRead.低压蒸汽温度2)
    F_lms2 = get_tag_value(snapshot, TagsRead.低压蒸汽流量2)
    H_lms2 = get_h_by_pt(P_lms2, T_lms2)
    Q_lms = (H_lms1 * F_lms1 + H_lms2 * F_lms2) * 1000  # 1t/h*1kJ/kg=1000kg/h*kJ/kg=1000kJ/h
    F_ms1 = get_tag_value(snapshot, TagsRead.高压蒸汽流量1号炉)
    F_ms2 = get_tag_value(snapshot, TagsRead.高压蒸汽流量2号炉)
    F_msds1 = get_tag_value(snapshot, TagsRead.高压蒸汽减温水流量1号炉)
    F_msds2 = get_tag_value(snapshot, TagsRead.高压蒸汽减温水流量2号炉)
    F_ms = F_ms1 + F_ms2 + F_msds1 + F_msds2
    P_ms = get_tag_value(snapshot, TagsRead.主汽门前压力)
    T_ms = get_tag_value(snapshot, TagsRead.主汽门前温度)
    H_ms = get_h_by_pt(P_ms, T_ms)
    Q_ms = F_ms * H_ms * 1000  # kJ/h
    P_ho = get_tag_value(snapshot, TagsRead.高排压力)
    T_ho = get_tag_value(snapshot, TagsRead.高排温度)
    H_ho = get_h_by_pt(P_ho, T_ho)
    F_合缸漏汽 = 17.962
    F_ho = F_ms - F_合缸漏汽
    Q_ho = F_ho * H_ho * 1000
    F_fw_medium1 = get_tag_value(snapshot, TagsRead.中压给水流量1号炉)
    F_fw_medium2 = get_tag_value(snapshot, TagsRead.中压给水流量2号炉)
    F_rhds1 = get_tag_value(snapshot, TagsRead.再热减温水流量1)
    F_rhds2 = get_tag_value(snapshot, TagsRead.再热减温水流量2)
    F_FGH1 = get_tag_value(snapshot, TagsRead.FGH流量1号炉)
    F_FGH2 = get_tag_value(snapshot, TagsRead.FGH流量2号炉)
    F_mi = F_fw_medium1 + F_fw_medium2 + F_ho - F_FGH1 - F_FGH2 + F_rhds1 + F_rhds2
    P_mi = get_tag_value(snapshot, TagsRead.中压主汽门前压力)
    T_mi = get_tag_value(snapshot, TagsRead.中压主汽门前温度)
    H_mi = get_h_by_pt(P_mi, T_mi)
    Q_mi = F_mi * H_mi * 1000
    Q_c = (Q_ms - Q_ho + Q_mi + Q_lms - Q_seal - power_shaft_steam - Q_wellout - Q_供热) / 3600000  # MW
    pres_cur = get_tag_value(snapshot, TagsRead.当前背压, 6)

    c0 = interpolate_value_complex(Q_c, Qc_C)
    t0 = get_tag_value(snapshot, TagsRead.环境温度)
    p0 = get_tag_value(snapshot, TagsRead.大气压力)
    humid = get_tag_value(snapshot, TagsRead.环境湿度)

    xi = (Q_c, t0, humid)
    p_back = {}
    delta_wt = {}
    delta_wc = {}
    delta_w = {}
    for 循泵方式 in ["A", "B", "C", "D", "E", "F", "G", "H"]:
        for 风机数量 in [3, 4, 5, 6, 7, 8]:
            state = f"{循泵方式}{风机数量}"
            _ = inter_func[state](xi)
            p_back.update({state: _})

    cur_state = "A4"  # 当前运行的组合方式
    delta_power_max = 0
    delta_pres = 0
    state_max = cur_state
    for 循泵方式 in ["A", "B", "C", "D", "E", "F", "G", "H"]:
        for 风机数量 in [3, 4, 5, 6, 7, 8]:
            state = f"{循泵方式}{风机数量}"
            delta_p = p_back[state] - p_back[cur_state]  # 如果<0
            delta_wt.update({state: power_steam * delta_p * c0 * 1000})  # kW，如果组合背压小于基准背压，则微增出力>0
            delta_wc.update({state: power_cold[state] - power_cold[cur_state]})  # 如果组合背压小于基准背压，则冷端耗功差>0
            delta_w.update({state: delta_wt[state] - delta_wc[state]})
            if delta_w[state] > delta_power_max:
                delta_power_max = delta_w[state]
                state_max = state
                delta_pres = delta_p

    # -------------------------------- 校验当前优化结果是否合理 ---------------------------------

    # -------------------------------- 校验当前优化结果是否合理 ---------------------------------

    # -------------------------------- 优化结果更新阈值 ------------------------------------
    global t_range, power_range, heat_range
    if len(t_range) == 0 and power_range == 0:
        t_range = [t0 - 1, t0 + 1]
        power_range = [power_steam - 5, power_steam + 5]
        heat_range = [Q_供热 - 10, Q_供热 + 10]
        last_state = state_max
        last_delta_pres = delta_pres
    else:
        if power_range[0] < power_steam < power_range[1] and t_range[0] < t0 < t_range[1] and heat_range[0] < Q_供热 < \
                heat_range[1]:
            last_state = state_max
            last_delta_pres = delta_pres
        else:
            # 更新结果
            pass

    # -------------------------------- 优化结果更新阈值 ------------------------------------

    pres_opt = pres_cur + delta_pres

    #
    api = init_dbp_api()
    result = {
        "建议运行方式": "A8",
        "最优运行方式下背压": 8,
    }

    api.write_snapshot_by_cmd(tags=list(result.keys()), values=list(result.values()))


# points = [
#     (450, 23, 0.8, 5.9341),
#     (500, 23, 0.8, 6.3983),
#     (450, 25, 0.8, 6.3121),
#     (500, 25, 0.8, 6.7834),
#     (450, 23, 0.9, 6.1882),
#     (500, 23, 0.9, 6.6575),
#     (450, 25, 0.9, 6.6011),
#     (500, 25, 0.9, 7.0780)
# ]
#
# dataframe = pd.DataFrame(points, columns=["x1", "x2", "x3", "y"])
# _ = interpolate_nd(xi=(470, 24.2), dataframe=dataframe, df_x_titles=["x1", "x2"], df_y_title=["y"])
# print(_)

optimize()
execute_function_by_interval(optimize, minute=0, second=30)
