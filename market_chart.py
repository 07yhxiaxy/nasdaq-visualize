"""
NASDAQ & S&P 500 历史走势 + 重大事件标注 (v3)
=============================================
依赖: pip install yfinance plotly pandas
运行: python market_chart.py
"""

import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import webbrowser, os

# ── 1. 下载数据 ──────────────────────────────────────────────────
print("正在下载数据...")
nasdaq = yf.download("^IXIC", start="1990-01-01", end=datetime.today().strftime("%Y-%m-%d"), auto_adjust=True)
sp500  = yf.download("^GSPC", start="1990-01-01", end=datetime.today().strftime("%Y-%m-%d"), auto_adjust=True)

for df in [nasdaq, sp500]:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

print(f"  NASDAQ: {len(nasdaq)} 天 | S&P 500: {len(sp500)} 天")

# ── 2. 事件列表 ──────────────────────────────────────────────────
EVENTS = [
    ("1990-08-02", "海湾战争", "伊拉克入侵科威特，油价飙升", "bear"),
    ("1994-02-04", "美联储加息周期", "激进加息，债券崩盘", "bear"),
    ("1995-08-09", "Netscape IPO", "互联网时代开启", "bull"),
    ("1997-10-27", "亚洲金融危机", "亚洲风暴冲击华尔街", "bear"),
    ("1998-08-17", "俄罗斯违约/LTCM", "LTCM崩溃，全球恐慌", "bear"),
    ("2000-03-10", "互联网泡沫顶峰", "纳指5048历史高位", "bear"),
    ("2001-09-11", "9/11袭击", "市场关闭4天，重开暴跌", "bear"),
    ("2002-10-09", "熊市底部", "泡沫后最低点", "bull"),
    ("2003-03-20", "伊拉克战争", "美军入侵，市场反弹", "bull"),
    ("2007-08-09", "次贷危机爆发", "信贷市场冻结", "bear"),
    ("2008-09-15", "雷曼破产", "全球金融危机爆发", "bear"),
    ("2009-03-09", "大衰退底部", "S&P 676，危机最低点", "bull"),
    ("2010-05-06", "闪电崩盘", "道指分钟暴跌1000点", "bear"),
    ("2011-08-05", "美国信用降级", "标普降级AAA", "bear"),
    ("2012-07-26", "德拉吉: 不惜一切", "欧债危机转折", "bull"),
    ("2013-05-22", "Taper Tantrum", "伯南克暗示缩减QE", "bear"),
    ("2015-08-24", "人民币贬值冲击", "全球黑色星期一", "bear"),
    ("2016-06-23", "英国脱欧", "脱欧公投震荡", "bear"),
    ("2016-11-08", "特朗普当选", "特朗普交易反弹", "bull"),
    ("2018-02-05", "Volmageddon", "VIX暴涨，XIV归零", "bear"),
    ("2018-12-24", "平安夜大跌", "加息+贸易战恐慌", "bear"),
    ("2020-02-20", "COVID暴跌", "疫情蔓延，暴跌34%", "bear"),
    ("2020-03-23", "COVID底部", "无限QE，触底反弹", "bull"),
    ("2020-11-09", "辉瑞疫苗", "有效率90%，暴涨", "bull"),
    ("2021-01-27", "GameStop逼空", "散户大战华尔街", "neutral"),
    ("2022-01-03", "2022熊市", "美联储鹰派转向", "bear"),
    ("2022-02-24", "俄乌战争", "俄罗斯入侵乌克兰", "bear"),
    ("2023-03-10", "硅谷银行倒闭", "SVB挤兑破产", "bear"),
    ("2023-05-24", "英伟达AI爆发", "AI概念全线暴涨", "bull"),
    ("2024-08-05", "日元套息平仓", "VIX飙至65", "bear"),
    ("2024-09-18", "美联储降息", "四年首次降息50bp", "bull"),
    ("2025-01-27", "DeepSeek冲击", "中国AI引发恐慌", "bear"),
    ("2025-04-02", "关税Liberation Day", "大规模关税，全球暴跌", "bear"),
]

# ── 3. 构建图表（单图，双Y轴，不用subplot）─────────────────────
print("正在生成图表...")
fig = go.Figure()

# NASDAQ 线
fig.add_trace(go.Scatter(
    x=nasdaq.index, y=nasdaq["Close"],
    name="NASDAQ Composite",
    line=dict(color="#7c3aed", width=2),
    hovertemplate="<b>NASDAQ</b> %{x|%Y-%m-%d}<br>%{y:,.0f}<extra></extra>",
))

# S&P 500 线（副Y轴）
fig.add_trace(go.Scatter(
    x=sp500.index, y=sp500["Close"],
    name="S&P 500",
    yaxis="y2",
    line=dict(color="#ea580c", width=2),
    hovertemplate="<b>S&P 500</b> %{x|%Y-%m-%d}<br>%{y:,.0f}<extra></extra>",
))

# ── 4. 事件标注 ──────────────────────────────────────────────────
color_map = {"bear": "#dc2626", "bull": "#16a34a", "neutral": "#6b7280"}
nasdaq_max = float(nasdaq["Close"].max())

for i, (date_str, title, desc, direction) in enumerate(EVENTS):
    event_date = pd.Timestamp(date_str)
    color = color_map[direction]

    try:
        nearest_idx = nasdaq.index.get_indexer([event_date], method="nearest")[0]
        y_val = float(nasdaq["Close"].iloc[nearest_idx])
    except Exception:
        continue

    # 竖线：从0到数据点
    fig.add_shape(
        type="line",
        x0=nasdaq.index[nearest_idx], x1=nasdaq.index[nearest_idx],
        y0=0, y1=y_val,
        line=dict(color=color, width=1.2, dash="dot"),
        opacity=0.4,
    )

    # 圆点标记在数据线上
    fig.add_trace(go.Scatter(
        x=[nasdaq.index[nearest_idx]], y=[y_val],
        mode="markers",
        marker=dict(size=8, color=color, line=dict(color="white", width=1.5)),
        showlegend=False,
        hovertemplate=f"<b>📌 {title}</b><br>{desc}<br>{date_str}<br>NASDAQ: %{{y:,.0f}}<extra></extra>",
    ))

    # 文字标签（交替高低位置防重叠）
    label_y = nasdaq_max * (1.12 if i % 2 == 0 else 1.22)
    fig.add_annotation(
        x=nasdaq.index[nearest_idx],
        y=label_y,
        text=f"<b>{title}</b>",
        showarrow=True,
        arrowhead=0,
        arrowwidth=1,
        arrowcolor=color,
        ax=0,
        ay=0,
        ayref="y",
        font=dict(size=9, color=color),
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=color,
        borderwidth=1,
        borderpad=2,
        textangle=-45,
    )

# ── 5. 布局 ─────────────────────────────────────────────────────
fig.update_layout(
    title=dict(
        text="<b>NASDAQ & S&P 500 历史走势 + 重大事件</b>",
        font=dict(size=22, color="#1e293b", family="Arial"),
        x=0.5, y=0.97,
    ),

    # 强制亮色
    template="plotly_white",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f8fafc",

    width=1600,
    height=900,
    margin=dict(l=80, r=80, t=80, b=80),
    hovermode="x unified",

    legend=dict(
        orientation="h",
        yanchor="top", y=0.99,
        xanchor="left", x=0.01,
        font=dict(size=14, color="#334155"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e2e8f0", borderwidth=1,
    ),

    # 左Y: NASDAQ
    yaxis=dict(
        title=dict(text="NASDAQ Composite", font=dict(size=14, color="#7c3aed")),
        tickfont=dict(size=13, color="#7c3aed"),
        gridcolor="rgba(0,0,0,0.06)",
        tickformat=",",
        rangemode="tozero",
        side="left",
    ),
    # 右Y: S&P 500
    yaxis2=dict(
        title=dict(text="S&P 500", font=dict(size=14, color="#ea580c")),
        tickfont=dict(size=13, color="#ea580c"),
        overlaying="y", side="right",
        gridcolor="rgba(0,0,0,0.02)",
        tickformat=",",
        rangemode="tozero",
    ),

    xaxis=dict(
        gridcolor="rgba(0,0,0,0.06)",
        tickfont=dict(size=13, color="#475569"),
        rangeslider=dict(visible=True, thickness=0.07, bgcolor="#f1f5f9"),
        rangeselector=dict(
            buttons=[
                dict(count=1,  label="1M",  step="month", stepmode="backward"),
                dict(count=6,  label="6M",  step="month", stepmode="backward"),
                dict(count=1,  label="YTD", step="year",  stepmode="todate"),
                dict(count=1,  label="1Y",  step="year",  stepmode="backward"),
                dict(count=5,  label="5Y",  step="year",  stepmode="backward"),
                dict(count=10, label="10Y", step="year",  stepmode="backward"),
                dict(step="all", label="全部"),
            ],
            bgcolor="#f1f5f9",
            activecolor="#7c3aed",
            font=dict(color="#334155", size=13),
            bordercolor="#cbd5e1", borderwidth=1,
        ),
    ),
)

# ── 6. 保存（开启 scrollZoom）────────────────────────────────────
output_file = "nasdaq_sp500_events.html"
fig.write_html(
    output_file,
    include_plotlyjs="cdn",
    config={
        "scrollZoom": True,
        "displayModeBar": True,
        "displaylogo": False,
        "responsive": True,
    },
)

print(f"\n✅ 已保存 → {output_file}")
print("   滚轮/双指缩放 | 拖拽平移 | 双击还原 | 底部滑块选范围")
webbrowser.open("file://" + os.path.realpath(output_file))
