"""
NASDAQ & S&P 500 历史走势 + 重大事件标注
========================================
依赖: pip install yfinance plotly pandas
运行: python market_chart.py
会在浏览器中打开一个交互式图表（支持缩放、拖拽、hover 查看细节）
"""

import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# ── 1. 下载每日数据 ──────────────────────────────────────────────
print("正在下载 NASDAQ 和 S&P 500 历史数据（1990至今）...")
nasdaq = yf.download("^IXIC", start="1990-01-01", end=datetime.today().strftime("%Y-%m-%d"), auto_adjust=True)
sp500  = yf.download("^GSPC", start="1990-01-01", end=datetime.today().strftime("%Y-%m-%d"), auto_adjust=True)

# 兼容 yfinance 新版多级列名
if isinstance(nasdaq.columns, pd.MultiIndex):
    nasdaq.columns = nasdaq.columns.get_level_values(0)
if isinstance(sp500.columns, pd.MultiIndex):
    sp500.columns = sp500.columns.get_level_values(0)

print(f"  NASDAQ: {len(nasdaq)} 个交易日")
print(f"  S&P 500: {len(sp500)} 个交易日")

# ── 2. 重大市场事件 ──────────────────────────────────────────────
# 格式: (日期, 标题, 详细说明, 影响方向)
# 影响方向: "bear" = 利空/下跌, "bull" = 利好/上涨, "neutral" = 中性
EVENTS = [
    ("1990-08-02", "海湾战争爆发", "伊拉克入侵科威特，油价飙升，市场恐慌抛售", "bear"),
    ("1994-02-04", "美联储加息周期", "美联储开始激进加息，债券市场崩盘", "bear"),
    ("1995-08-09", "Netscape IPO", "Netscape 上市首日暴涨，互联网时代开启", "bull"),
    ("1997-10-27", "亚洲金融危机蔓延", "亚洲金融风暴冲击华尔街，道指单日暴跌554点", "bear"),
    ("1998-08-17", "俄罗斯违约 / LTCM 危机", "俄罗斯债务违约，LTCM 对冲基金濒临崩溃", "bear"),
    ("1998-09-23", "美联储紧急降息", "美联储协调救助 LTCM，连续三次降息", "bull"),
    ("2000-03-10", "互联网泡沫顶峰", "纳斯达克触及5048点历史高位，随后开始崩盘", "bear"),
    ("2000-04-14", "纳指单日暴跌9.7%", "互联网泡沫破裂加速，纳指创最大单日跌幅之一", "bear"),
    ("2001-01-03", "美联储紧急降息", "美联储在非会议日紧急降息50个基点", "bull"),
    ("2001-09-11", "9/11 恐怖袭击", "纽约世贸中心遭袭，市场关闭4天，重开后暴跌", "bear"),
    ("2001-09-17", "9/11 后市场重开", "道指单日暴跌684点（-7.1%），航空/保险股崩盘", "bear"),
    ("2002-07-21", "WorldCom 丑闻", "WorldCom 会计造假破产，投资者信心崩溃", "bear"),
    ("2002-10-09", "熊市底部", "S&P 500 触及776点，互联网泡沫后的最低点", "bull"),
    ("2003-03-20", "伊拉克战争开始", "美军入侵伊拉克，市场'买入战争'反弹", "bull"),
    ("2004-06-30", "美联储开始加息", "美联储开启连续17次加息周期", "neutral"),
    ("2007-02-27", "中国股市暴跌 全球震荡", "上证指数暴跌8.8%引发全球抛售", "bear"),
    ("2007-08-09", "次贷危机爆发", "法国巴黎银行冻结基金，信贷市场冻结", "bear"),
    ("2008-03-16", "贝尔斯登被收购", "摩根大通以超低价收购贝尔斯登", "bear"),
    ("2008-09-15", "雷曼兄弟破产", "雷曼申请破产保护，全球金融危机全面爆发", "bear"),
    ("2008-09-29", "TARP 救助被否", "众议院否决7000亿救助计划，道指暴跌777点", "bear"),
    ("2008-10-13", "全球协调救市", "各国央行联合注资，道指单日暴涨936点", "bull"),
    ("2009-03-09", "大衰退底部", "S&P 500 触及676点，金融危机最低点", "bull"),
    ("2009-03-23", "PPIP 计划公布", "财政部公布公私投资计划，市场大涨", "bull"),
    ("2010-05-06", "闪电崩盘", "道指在数分钟内暴跌近1000点后迅速反弹", "bear"),
    ("2010-05-10", "欧洲救助基金", "EU 宣布万亿美元希腊救助方案", "bull"),
    ("2011-08-05", "美国信用降级", "标普将美国从AAA降级，市场重挫", "bear"),
    ("2011-08-08", "降级后的黑色星期一", "全球市场恐慌抛售，道指暴跌634点", "bear"),
    ("2012-07-26", "德拉吉：不惜一切代价", "欧央行行长表态保卫欧元，欧债危机转折点", "bull"),
    ("2013-05-22", "缩减恐慌", "伯南克暗示可能缩减QE，新兴市场暴跌", "bear"),
    ("2013-12-18", "美联储开始缩减QE", "美联储宣布开始缩减每月购债规模", "neutral"),
    ("2015-06-12", "A股开始暴跌", "中国股市泡沫破裂，三周内跌去30%", "bear"),
    ("2015-08-24", "人民币贬值冲击", "央行贬值人民币引发'黑色星期一'全球抛售", "bear"),
    ("2016-01-04", "A股熔断 全球暴跌", "中国A股两次触发熔断，全球市场开年暴跌", "bear"),
    ("2016-06-23", "英国脱欧公投", "英国投票脱离欧盟，市场剧烈震荡后快速反弹", "bear"),
    ("2016-11-08", "特朗普当选", "大选结果意外，期货暴跌后'特朗普交易'反弹", "bull"),
    ("2017-01-25", "道指首次突破20000", "特朗普减税预期推动道指创历史新高", "bull"),
    ("2018-02-05", "VIX 末日事件", "波动率飙升，XIV 产品归零，道指暴跌1175点", "bear"),
    ("2018-10-10", "科技股恐慌抛售", "加息+贸易战担忧，纳指两天暴跌5%+", "bear"),
    ("2018-12-24", "平安夜大跌", "美联储加息+贸易战，S&P 500 濒临熊市", "bear"),
    ("2019-01-04", "鲍威尔转向鸽派", "美联储主席表态灵活调整政策，市场大涨", "bull"),
    ("2019-06-04", "美联储暗示降息", "鲍威尔暗示将降息应对贸易战影响", "bull"),
    ("2019-08-05", "贸易战升级", "人民币破7，美国将中国列为汇率操纵国", "bear"),
    ("2020-02-20", "COVID 暴跌开始", "新冠疫情全球蔓延，市场开始34%的暴跌", "bear"),
    ("2020-03-09", "黑色星期一 石油战", "沙特发动价格战，油价暴跌25%，触发熔断", "bear"),
    ("2020-03-12", "黑色星期四", "特朗普宣布旅行禁令，道指暴跌2352点", "bear"),
    ("2020-03-16", "又一个黑色星期一", "美联储紧急降息至零，市场反而暴跌12%", "bear"),
    ("2020-03-23", "COVID 底部", "美联储宣布无限量QE，S&P 500 触底2237", "bull"),
    ("2020-11-09", "辉瑞疫苗利好", "辉瑞疫苗有效性达90%，道指暴涨834点", "bull"),
    ("2021-01-27", "GameStop 逼空", "Reddit散户大战华尔街，GME暴涨，做空基金巨亏", "neutral"),
    ("2021-11-19", "纳指开始下跌", "高通胀+缩减恐慌，成长股开始回调", "bear"),
    ("2022-01-03", "2022 熊市开始", "美联储鹰派转向，标志年度最差表现的开始", "bear"),
    ("2022-02-24", "俄乌战争爆发", "俄罗斯入侵乌克兰，全球市场震荡", "bear"),
    ("2022-05-05", "美联储加息50bp", "22年来首次加息50个基点", "bear"),
    ("2022-06-13", "加密货币崩盘", "Luna/Terra崩溃，加密寒冬波及股市", "bear"),
    ("2022-09-13", "通胀意外高于预期", "8月CPI超预期，道指暴跌1276点", "bear"),
    ("2023-03-10", "硅谷银行倒闭", "SVB银行挤兑破产，银行业危机恐慌", "bear"),
    ("2023-03-19", "瑞信被收购", "瑞银紧急收购瑞信，全球银行恐慌", "bear"),
    ("2023-05-24", "英伟达财报炸裂", "NVDA 指引远超预期，AI概念股全线暴涨", "bull"),
    ("2023-11-01", "美联储暗示暂停加息", "鲍威尔暗示加息周期可能结束", "bull"),
    ("2024-03-08", "纳指首次突破16000", "AI 热潮驱动科技股持续新高", "bull"),
    ("2024-07-11", "通胀降温 降息预期", "CPI 超预期降温，市场预期9月降息", "bull"),
    ("2024-08-05", "日元套息交易平仓", "日本加息触发全球性抛售，VIX飙至65", "bear"),
    ("2024-09-18", "美联储降息50bp", "美联储四年来首次降息且幅度超预期", "bull"),
    ("2024-12-18", "鹰派降息", "美联储降息25bp但2025年预期仅降两次", "bear"),
    ("2025-01-20", "特朗普就任", "特朗普第二任期开始，市场观望政策方向", "neutral"),
    ("2025-01-27", "DeepSeek 冲击", "中国AI模型DeepSeek引发美国科技股恐慌", "bear"),
    ("2025-04-02", "Liberation Day 关税", "美国宣布大规模对等关税，全球市场暴跌", "bear"),
]


# ── 3. 构建 Plotly 图表 ─────────────────────────────────────────
print("正在生成图表...")

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.75, 0.25],
    subplot_titles=("", "")
)

# ── NASDAQ 走势线 ──
fig.add_trace(go.Scatter(
    x=nasdaq.index, y=nasdaq["Close"],
    name="NASDAQ Composite",
    line=dict(color="#3266ad", width=1.2),
    hovertemplate="<b>NASDAQ</b><br>日期: %{x|%Y-%m-%d}<br>收盘: %{y:,.0f}<extra></extra>"
), row=1, col=1)

# ── S&P 500 走势线 ──
fig.add_trace(go.Scatter(
    x=sp500.index, y=sp500["Close"],
    name="S&P 500",
    line=dict(color="#d85a30", width=1.2),
    yaxis="y2",
    hovertemplate="<b>S&P 500</b><br>日期: %{x|%Y-%m-%d}<br>收盘: %{y:,.0f}<extra></extra>"
), row=1, col=1)

# ── NASDAQ 成交量 ──
if "Volume" in nasdaq.columns:
    colors = []
    closes = nasdaq["Close"].values
    for i in range(len(closes)):
        if i == 0:
            colors.append("rgba(50,102,173,0.3)")
        elif closes[i] >= closes[i-1]:
            colors.append("rgba(38,166,91,0.4)")
        else:
            colors.append("rgba(226,75,74,0.4)")
    fig.add_trace(go.Bar(
        x=nasdaq.index, y=nasdaq["Volume"],
        name="成交量",
        marker_color=colors,
        showlegend=False,
        hovertemplate="成交量: %{y:,.0f}<extra></extra>"
    ), row=2, col=1)

# ── 事件标注 ──
event_colors = {"bear": "rgba(226,75,74,0.7)", "bull": "rgba(38,166,91,0.7)", "neutral": "rgba(150,150,150,0.6)"}
event_symbols = {"bear": "triangle-down", "bull": "triangle-up", "neutral": "diamond"}

for date_str, title, desc, direction in EVENTS:
    event_date = pd.Timestamp(date_str)
    color = event_colors[direction]

    # 垂直虚线
    fig.add_vline(
        x=event_date, row=1, col=1,
        line=dict(color=color, width=0.8, dash="dot"),
        opacity=0.5
    )

    # 在 NASDAQ 线上找最近的交易日作为标注点
    try:
        nearest_idx = nasdaq.index.get_indexer([event_date], method="nearest")[0]
        y_val = nasdaq["Close"].iloc[nearest_idx]

        fig.add_trace(go.Scatter(
            x=[nasdaq.index[nearest_idx]],
            y=[y_val],
            mode="markers",
            marker=dict(
                symbol=event_symbols[direction],
                size=9,
                color=color,
                line=dict(color="white", width=1)
            ),
            name=title,
            showlegend=False,
            hovertemplate=(
                f"<b>{title}</b><br>"
                f"{desc}<br>"
                f"日期: {date_str}<br>"
                f"NASDAQ: %{{y:,.0f}}<extra></extra>"
            ),
        ), row=1, col=1)
    except Exception:
        pass

# ── 4. 图表布局 ─────────────────────────────────────────────────
fig.update_layout(
    title=dict(
        text="NASDAQ & S&P 500 历史走势（1990至今）+ 重大事件标注",
        font=dict(size=18),
        x=0.5
    ),
    template="plotly_dark",
    paper_bgcolor="#1a1a2e",
    plot_bgcolor="#16213e",
    height=800,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="center", x=0.5,
        font=dict(size=12)
    ),

    # 主 Y 轴 (NASDAQ)
    yaxis=dict(
        title="NASDAQ Composite",
        titlefont=dict(color="#3266ad"),
        tickfont=dict(color="#3266ad"),
        gridcolor="rgba(255,255,255,0.06)",
        side="left"
    ),
    # 副 Y 轴 (S&P 500)
    yaxis2=dict(
        title="S&P 500",
        titlefont=dict(color="#d85a30"),
        tickfont=dict(color="#d85a30"),
        overlaying="y",
        side="right",
        gridcolor="rgba(255,255,255,0.03)"
    ),

    # 成交量 Y 轴
    yaxis3=dict(
        gridcolor="rgba(255,255,255,0.06)",
        tickformat=".1s"
    ),

    xaxis2=dict(gridcolor="rgba(255,255,255,0.06)"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        rangeslider=dict(visible=False),
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(count=10, label="10Y", step="year", stepmode="backward"),
                dict(step="all", label="全部")
            ]),
            bgcolor="#1a1a2e",
            activecolor="#3266ad",
            font=dict(color="white"),
        ),
    ),
)

# ── 5. 添加图例说明事件标记 ──────────────────────────────────────
fig.add_annotation(
    text="▲ 利好事件  ▼ 利空事件  ◆ 中性事件（hover 查看详情）",
    xref="paper", yref="paper",
    x=0.5, y=-0.06,
    showarrow=False,
    font=dict(size=11, color="rgba(255,255,255,0.6)"),
    align="center"
)

# ── 6. 保存并打开 ────────────────────────────────────────────────
output_file = "nasdaq_sp500_events.html"
fig.write_html(output_file, include_plotlyjs="cdn")
print(f"\n✅ 图表已保存为 {output_file}")
print("   用浏览器打开即可查看，支持：")
print("   • 鼠标滚轮放大/缩小")
print("   • 拖拽选择时间范围")
print("   • 顶部按钮快速切换时间段（1M/3M/6M/YTD/1Y/5Y/10Y/全部）")
print("   • 悬停在三角标记上查看事件详情")
print("   • 双击图表恢复全景")

# 自动打开浏览器
import webbrowser, os
webbrowser.open("file://" + os.path.realpath(output_file))
