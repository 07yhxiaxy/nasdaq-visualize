"""
NASDAQ & S&P 500 历史走势 + 重大事件 + 自动检测 ≥3% 涨跌日 (v4)
================================================================
依赖: pip install yfinance plotly pandas
运行: python market_chart.py
"""

import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
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

# ── 2. 自动检测 ≥3% 涨跌日 ──────────────────────────────────────
nasdaq["Pct"] = nasdaq["Close"].pct_change() * 100
big_moves = nasdaq[nasdaq["Pct"].abs() >= 3].copy()
big_up   = big_moves[big_moves["Pct"] > 0]
big_down = big_moves[big_moves["Pct"] < 0]

print(f"  ≥3% 涨跌日: {len(big_moves)} 天（涨 {len(big_up)} / 跌 {len(big_down)}）")

# ── 3. 人工标注的命名事件 ────────────────────────────────────────
NAMED_EVENTS = [
    ("1990-08-02", "海湾战争", "伊拉克入侵科威特，油价飙升"),
    ("1994-02-04", "美联储加息周期", "激进加息，债券崩盘"),
    ("1995-08-09", "Netscape IPO", "互联网时代开启"),
    ("1997-10-27", "亚洲金融危机", "亚洲风暴冲击华尔街"),
    ("1998-08-17", "俄罗斯违约/LTCM", "LTCM崩溃，全球恐慌"),
    ("2000-03-10", "互联网泡沫顶峰", "纳指5048历史高位"),
    ("2001-09-11", "9/11袭击", "市场关闭4天，重开暴跌"),
    ("2002-10-09", "熊市底部", "泡沫后最低点"),
    ("2003-03-20", "伊拉克战争", "美军入侵，市场反弹"),
    ("2007-08-09", "次贷危机爆发", "信贷市场冻结"),
    ("2008-09-15", "雷曼破产", "全球金融危机爆发"),
    ("2009-03-09", "大衰退底部", "S&P 676，危机最低点"),
    ("2010-05-06", "闪电崩盘", "道指分钟暴跌1000点"),
    ("2011-08-05", "美国信用降级", "标普降级AAA"),
    ("2012-07-26", "德拉吉: 不惜一切", "欧债危机转折"),
    ("2013-05-22", "Taper Tantrum", "伯南克暗示缩减QE"),
    ("2015-08-24", "人民币贬值冲击", "全球黑色星期一"),
    ("2016-06-23", "英国脱欧", "脱欧公投震荡"),
    ("2016-11-08", "特朗普当选", "特朗普交易反弹"),
    ("2018-02-05", "Volmageddon", "VIX暴涨，XIV归零"),
    ("2018-12-24", "平安夜大跌", "加息+贸易战恐慌"),
    ("2020-02-20", "COVID暴跌开始", "疫情蔓延，暴跌34%"),
    ("2020-03-23", "COVID底部", "无限QE，触底反弹"),
    ("2020-11-09", "辉瑞疫苗", "有效率90%，暴涨"),
    ("2021-01-27", "GameStop逼空", "散户大战华尔街"),
    ("2022-01-03", "2022熊市", "美联储鹰派转向"),
    ("2022-02-24", "俄乌战争", "俄罗斯入侵乌克兰"),
    ("2023-03-10", "硅谷银行倒闭", "SVB挤兑破产"),
    ("2023-05-24", "英伟达AI爆发", "AI概念全线暴涨"),
    ("2024-08-05", "日元套息平仓", "VIX飙至65"),
    ("2024-09-18", "美联储降息", "四年首次降息50bp"),
    ("2025-01-27", "DeepSeek冲击", "中国AI引发恐慌"),
    ("2025-04-02", "关税Liberation Day", "大规模关税，全球暴跌"),
]

# ── 4. 构建图表 ──────────────────────────────────────────────────
print("正在生成图表...")
fig = go.Figure()

# --- NASDAQ 线 ---
fig.add_trace(go.Scatter(
    x=nasdaq.index, y=nasdaq["Close"],
    name="NASDAQ",
    line=dict(color="#7c3aed", width=1.8),
    hovertemplate="%{x|%Y-%m-%d}<br>NASDAQ: %{y:,.0f}<extra></extra>",
))

# --- S&P 500 线（右Y轴） ---
fig.add_trace(go.Scatter(
    x=sp500.index, y=sp500["Close"],
    name="S&P 500",
    yaxis="y2",
    line=dict(color="#ea580c", width=1.8),
    hovertemplate="%{x|%Y-%m-%d}<br>S&P 500: %{y:,.0f}<extra></extra>",
))

# --- ≥3% 暴跌日（红色圆点，大小按幅度） ---
fig.add_trace(go.Scatter(
    x=big_down.index,
    y=big_down["Close"],
    mode="markers",
    name="单日暴跌 ≥3%",
    marker=dict(
        size=big_down["Pct"].abs().clip(3, 15) * 2,
        color=big_down["Pct"],
        colorscale=[[0, "#dc2626"], [1, "#fca5a5"]],
        cmin=-15, cmax=-3,
        line=dict(color="white", width=0.5),
        opacity=0.8,
    ),
    hovertemplate=(
        "<b>📉 单日暴跌</b><br>"
        "%{x|%Y-%m-%d}<br>"
        "收盘: %{y:,.0f}<br>"
        "跌幅: %{customdata:.2f}%<extra></extra>"
    ),
    customdata=big_down["Pct"],
))

# --- ≥3% 暴涨日（绿色圆点，大小按幅度） ---
fig.add_trace(go.Scatter(
    x=big_up.index,
    y=big_up["Close"],
    mode="markers",
    name="单日暴涨 ≥3%",
    marker=dict(
        size=big_up["Pct"].abs().clip(3, 15) * 2,
        color=big_up["Pct"],
        colorscale=[[0, "#86efac"], [1, "#16a34a"]],
        cmin=3, cmax=15,
        line=dict(color="white", width=0.5),
        opacity=0.8,
    ),
    hovertemplate=(
        "<b>📈 单日暴涨</b><br>"
        "%{x|%Y-%m-%d}<br>"
        "收盘: %{y:,.0f}<br>"
        "涨幅: +%{customdata:.2f}%<extra></extra>"
    ),
    customdata=big_up["Pct"],
))

# --- 命名事件（菱形标记 + 文字标签） ---
named_x, named_y, named_text, named_hover = [], [], [], []
for date_str, title, desc in NAMED_EVENTS:
    event_date = pd.Timestamp(date_str)
    try:
        idx = nasdaq.index.get_indexer([event_date], method="nearest")[0]
        yv = float(nasdaq["Close"].iloc[idx])
        pct = float(nasdaq["Pct"].iloc[idx]) if not pd.isna(nasdaq["Pct"].iloc[idx]) else 0
        named_x.append(nasdaq.index[idx])
        named_y.append(yv)
        named_text.append(title)
        named_hover.append(f"<b>📌 {title}</b><br>{desc}<br>{date_str}<br>NASDAQ: {yv:,.0f}<br>当日涨跌: {pct:+.2f}%")
    except Exception:
        continue

fig.add_trace(go.Scatter(
    x=named_x, y=named_y,
    mode="markers+text",
    name="命名事件",
    text=named_text,
    textposition="top center",
    textfont=dict(size=10, color="#1e293b"),
    marker=dict(
        symbol="diamond",
        size=11,
        color="#facc15",
        line=dict(color="#a16207", width=1.5),
    ),
    hovertext=named_hover,
    hoverinfo="text",
))

# --- 命名事件竖线 ---
for i, (date_str, title, desc) in enumerate(NAMED_EVENTS):
    event_date = pd.Timestamp(date_str)
    try:
        idx = nasdaq.index.get_indexer([event_date], method="nearest")[0]
        yv = float(nasdaq["Close"].iloc[idx])
    except Exception:
        continue
    fig.add_shape(
        type="line",
        x0=nasdaq.index[idx], x1=nasdaq.index[idx],
        y0=0, y1=yv,
        line=dict(color="#a16207", width=0.8, dash="dot"),
        opacity=0.3,
    )

# ── 5. 布局 ─────────────────────────────────────────────────────
fig.update_layout(
    title=dict(
        text=(
            f"<b>NASDAQ & S&P 500 历史走势</b> (1990–至今)<br>"
            f"<span style='font-size:13px;color:#64748b;'>"
            f"共检测到 {len(big_moves)} 个单日 ≥3% 涨跌日"
            f"（暴涨 {len(big_up)} 天 / 暴跌 {len(big_down)} 天）"
            f"+ {len(NAMED_EVENTS)} 个命名事件"
            f"</span>"
        ),
        font=dict(size=20, color="#0f172a"),
        x=0.5, y=0.97,
    ),

    template="plotly_white",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f8fafc",
    width=1600,
    height=900,
    margin=dict(l=80, r=80, t=100, b=60),
    hovermode="x unified",

    legend=dict(
        orientation="h",
        yanchor="top", y=0.99,
        xanchor="left", x=0.01,
        font=dict(size=13, color="#334155"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e2e8f0", borderwidth=1,
    ),

    yaxis=dict(
        title=dict(text="NASDAQ Composite", font=dict(size=14, color="#7c3aed")),
        tickfont=dict(size=13, color="#7c3aed"),
        gridcolor="rgba(0,0,0,0.06)",
        tickformat=",",
        side="left",
    ),
    yaxis2=dict(
        title=dict(text="S&P 500", font=dict(size=14, color="#ea580c")),
        tickfont=dict(size=13, color="#ea580c"),
        overlaying="y", side="right",
        gridcolor="rgba(0,0,0,0.02)",
        tickformat=",",
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

# ── 6. 添加自定义 JS 按钮：切换涨跌阈值 ─────────────────────────
# 通过 updatemenus 添加阈值筛选（plotly 原生不好做动态筛选，
# 所以我们把 3%/5%/7%/10% 的数据各做一版放进 frames 里不现实，
# 这里用 updatemenus 控制圆点的可见性）

fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="right",
            x=0.99, xanchor="right",
            y=1.12, yanchor="top",
            bgcolor="#f1f5f9",
            bordercolor="#cbd5e1",
            font=dict(size=12, color="#334155"),
            buttons=[
                dict(
                    label="显示全部",
                    method="update",
                    args=[{"visible": [True, True, True, True, True]}],
                ),
                dict(
                    label="只看命名事件",
                    method="update",
                    args=[{"visible": [True, True, False, False, True]}],
                ),
                dict(
                    label="只看 ≥3% 涨跌",
                    method="update",
                    args=[{"visible": [True, True, True, True, False]}],
                ),
                dict(
                    label="隐藏标记",
                    method="update",
                    args=[{"visible": [True, True, False, False, False]}],
                ),
            ],
        )
    ]
)

# ── 7. 保存 ─────────────────────────────────────────────────────
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
print(f"   {len(big_moves)} 个 ≥3% 涨跌日 + {len(NAMED_EVENTS)} 个命名事件")
print("   滚轮/双指缩放 | 拖拽平移 | 双击还原 | 底部滑块选范围")
print("   右上角按钮切换：显示全部 / 只看命名事件 / 只看涨跌 / 隐藏标记")
webbrowser.open("file://" + os.path.realpath(output_file))
