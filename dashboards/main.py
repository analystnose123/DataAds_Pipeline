import streamlit as st
import sys
import os
import duckdb
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DataAds_Pipeline")
from EDA import *
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from config import DashboardConfig
from pathlib import Path
from dateutil.relativedelta import relativedelta
from queries import *
from components.metrics import render_metrics
from components.charts import *

#----------------------------------------Background and Styling------------------------#
AURORA_COLORS = ["#a855f7", "#22d3ee", "#e879f9", "#34d399", "#fbbf24"]

st.set_page_config(
    page_title="Dashboard",
    page_icon="🔐",
    layout="wide",
)

# ── Helper: load CSS dari file ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
def load_css(*paths: str) -> None:
    css = ""
    for path in paths:
        css += Path(path).read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css(os.path.join(BASE_DIR,"styles","background.css"), os.path.join(BASE_DIR,"styles","metrics.css"))
# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="jb-title">Dashboard Ads</div>
<div class="jb-subtitle">PT NOSE HERBALINDO</div>
""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════════
# DATA — ganti nilai di sini dengan data asli kamu
# ══════════════════════════════════════════════════════════════════════════════

#Connection
con = GetConnection(database_name = "campaign",
                    ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN)

@st.cache_data(ttl=60)
def GetPeriod():
    df = con.execute("""
        SELECT DISTINCT 
        month_campaign
        FROM CampaignReport
        ORDER BY month_campaign DESC
                      """).df()
    return df


#Period List
PERIOD_LIST = GetPeriod()

if "CHOICE" not in st.session_state:
    st.session_state.CHOICE = PERIOD_LIST["month_campaign"].tolist()[0]
if "selected_campaign"not in st.session_state:
    st.session_state.selected_campaign = None

MONTH_NAME= ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]
CHOICE = st.selectbox(
    "Pilih Periode",
    options=PERIOD_LIST["month_campaign"].tolist(),
    format_func=lambda x:f"{MONTH_NAME[x.month-1]} {x.year}",
    key = "CHOICE")

df_filtered = GetData(
                    db_name = 'campaign',
                    USE_MOTHERDUCK=True,
                    ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                    query= """
                           SELECT * FROM CampaignReport
                           WHERE month_campaign = ?
                           """,
                    params=[CHOICE.to_pydatetime()])

CAMPAIGN_LIST = GetData(db_name = "campaign",
                        USE_MOTHERDUCK=True,
                        ACCESS_TOKEN =DashboardConfig.ACCESS_TOKEN,
                        query = GetCampaignList(period_choice=CHOICE))

def CalculateDelta(current,before):
     delta = current - before
     delta_class = "green" if delta >=0 else "danger"
     delta_text = f"+{delta:,.0f}" if delta >= 0 else f"{delta:,.0f}"
     return delta_class, delta_text

ConvCurrent = GetData(db_name = "campaign",
                      USE_MOTHERDUCK = True,
                      ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                    query = QueryConversionPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                                    date_choice = CHOICE)).iloc[0,0]

ConvBefore = GetData(db_name = "campaign",
                                USE_MOTHERDUCK = True,
                                ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                                query = QueryConversionPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                                    date_choice = CHOICE-relativedelta(months=1))).iloc[0,0]

ClicksCurrent = GetData(db_name = "campaign",
                        USE_MOTHERDUCK = True,
                        ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                        query = QueryClickPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                        date_choice=CHOICE)).iloc[0,0]
ClicksBefore = GetData(db_name = "campaign",
                       USE_MOTHERDUCK = True,
                       ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                       query=QueryClickPerMonth(db_name = "campaign",
                                                table = DashboardConfig.CAMP_TABLE,
                                                date_choice=CHOICE-relativedelta(months=1))).iloc[0,0]
ClicksCurrent = GetData(db_name = "campaign",
                        USE_MOTHERDUCK = True,
                        ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                        query = QueryClickPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                        date_choice=CHOICE)).iloc[0,0]
ClicksBefore = GetData(db_name = "campaign",
                       USE_MOTHERDUCK = True,
                       ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                       query=QueryClickPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                             date_choice=CHOICE-relativedelta(months=1))).iloc[0,0]
ActiveCampaignCount = GetData(db_name = "campaign",
                              USE_MOTHERDUCK = True,
                              ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                              query=CountRunningCampaign(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                      date_choice=CHOICE)).iloc[0,0]

ClickDelta_class, ClickDelta_text = CalculateDelta(ClicksCurrent, ClicksBefore)
ConvDelta_class, ConvDelta_text = CalculateDelta(ConvCurrent,ConvBefore)

# ══════════════════════════════════════════════════════════════════════════════
# DATA — ganti nilai di sini dengan data asli kamu
# ══════════════════════════════════════════════════════════════════════════════
metrics_data = [
    {
        "label": "Jumlah Clicks/Pengunjung Website Bulan Ini",
        "value": ClicksCurrent,
        "value_class": "teal",   # pilihan: "" | "teal" | "green" | "amber" | "red"
        "delta": f"{ClickDelta_text} Clicks", # teks kecil di bawah angka
        "delta_class": ClickDelta_class,       # pilihan: "" | "warn" | "danger"
    },
    {
        "label": "Jumlah Conversions per Campaign",
        "value": ConvCurrent,
        "value_class": "orange",
        "delta": f"{ConvDelta_text} Conversions",
        "delta_class": ConvDelta_class,
    },
    {
        "label": "Jumlah Campaign yang Sedang Running",
        "value": f"{ActiveCampaignCount} Campaign Aktif",
        "value_class": "green"
    },
]
render_metrics(metrics_data)
# ══════════════════════════════════════════════════════════════════════════════
# Charts
# ══════════════════════════════════════════════════════════════════════════════
# 1. Grafik 1 : Whole Conversion Chart 2024-2026
ConversionTimeline = GetData(db_name="campaign",
                             USE_MOTHERDUCK=True,
                             ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                             query=QueryConversionData(db_name = "campaign",table="CampaignReport"))

st.header("Total Conversion 2025-2026")
render_line_chart(x = ConversionTimeline['month_campaign'],
                  y = ConversionTimeline['TotalConversions'])

CampaignConversionData = GetData(db_name = "campaign",
                                 USE_MOTHERDUCK=True,
                                 ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                                 query=QueryCampaignConv(db_name = "campaign",
                                                         table="CampaignReport",period_choice=CHOICE))

CampaignBudgetData = GetData(db_name="campaign",
                            USE_MOTHERDUCK=True,
                            ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                            query=QueryCostCampaign(db_name = "campaign",table="CampaignReport",period_choice=CHOICE))

FunnelDF = GetData(db_name="campaign",
                             USE_MOTHERDUCK=True,
                             ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                             query=FunnelStaging(period_choice=CHOICE))

MonthlyConversionData = GetData(db_name="campaign",
                                USE_MOTHERDUCK=True,
                                ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                                query=f"""
                                    SELECT
                                    month_campaign,
                                    SUM(conversions_campaign) AS MonthlyConv
                                    FROM CampaignReport
                                    GROUP BY month_campaign
                                    ORDER BY month_campaign""")

MonthlyImpressionsData = GetData(db_name='campaign',
                                 USE_MOTHERDUCK=True,
                                 ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                                 query=f"""
                                    SELECT
                                    month_campaign,
                                    SUM("impr._campaign") AS MonthlyImpressions
                                    FROM CampaignReport
                                    GROUP BY month_campaign
                                    ORDER BY month_campaign""")

MonthlyClicks=GetData(db_name='campaign',
                      USE_MOTHERDUCK=True,
                      ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                      query=f"""
                        SELECT
                        month_campaign,
                        SUm(clicks_campaign) as MonthlyClicks
                        FROM CampaignReport
                        GROUP BY month_campaign
                        ORDER BY month_campaign""")

AllCPCData = GetData(
    db_name='campaign',
    USE_MOTHERDUCK=True,
    ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
    query=GetCPC(table = 'CampaignReport',
                        grouping_category='month_campaign',
                        cost_columns='cost_campaign',
                        clicks_columns = 'clicks_campaign'))

AllCPLData = GetData(db_name='campaign',
                     USE_MOTHERDUCK=True,
                     ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                     query=GetCPL(table='CampaignReport',
                                  grouping_category='month_campaign',
                                  cost_columns='cost_campaign',
                                  leads_columns='other_campaign'))

AllCPMData = GetData(
    db_name='campaign',
    USE_MOTHERDUCK=True,
    ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
    query= GetCPM(table='CampaignReport',
                grouping_category='month_campaign',
                cost_columns='cost_campaign',
                impression_columns='impr._campaign'))

funneling_stage = FunnelDF.columns.tolist()

#3rd rows

st.header("Impression Amount per Month")
col1_chart = make_subplots(specs=[[{"secondary_y":True}]])

#1st chart line chart
col1_chart.add_trace(go.Scatter(
    x=MonthlyImpressionsData['month_campaign'], 
    y=AllCPMData['CPM'],
    mode="lines+markers",
    name='Cost per Mille Impressions (CPM)',
    line=dict(shape='spline',color="#1fef64", width=2),
    marker=dict(color="#000000", size=6),
    fill="tozeroy",
    fillcolor="rgba(124,58,237,0.10)",
),secondary_y=True)

#2 chart bar chart
col1_chart.add_trace(
    go.Bar(
    x=MonthlyImpressionsData['month_campaign'], 
    y=MonthlyImpressionsData['MonthlyImpressions'],
    name='Monthly Impressions',
    marker=dict(
        color="rgba(124,58,237,0.6)",
        line=dict(color="#fa8cd0", width=1),
        ))
        ,secondary_y=False)

col1_chart.update_layout(**AURORA_TEMPLATE)
st.plotly_chart(col1_chart, use_container_width=True)

#============= 2nd Row =============#
st.header("Total Website Clicks per Month")
col2_chart = make_subplots(specs=([[{"secondary_y":True}]]))
col2_chart.add_trace(go.Bar(
    x=MonthlyClicks['month_campaign'], 
    y=MonthlyClicks['MonthlyClicks'],
    name='Total Website Clicks',
    marker=dict(
        color="rgba(124,58,237,0.6)",
        line=dict(color="#a855f7", width=1),
        ))
        ,secondary_y=False)

col2_chart.add_trace(
    go.Scatter(
        x = AllCPCData['month_campaign'],
        y = AllCPCData['CPC'],
        mode="lines+markers",
        name='Cost Per Clicks (CPC)',
        line=dict(shape='spline',color="#1fef64", width=2),
        marker=dict(color="#000000", size=6),
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.10)",),secondary_y=True)

col2_chart.update_layout(**AURORA_TEMPLATE)
st.plotly_chart(col2_chart, use_container_width=True)

col3,col4,col5 = st.columns(3)
with col3:
    st.header("Kontribusi Tiap Campaign terhadap Jumlah Konversi")
    render_pie_chart(labels = CampaignConversionData['campaign'],
                       values=CampaignConversionData['TotalConversions'])
with col4:
    st.header("Persentase Cost Tiap Campaign")
    render_pie_chart(labels=CampaignBudgetData["campaign"],
                     values=CampaignBudgetData["TotalCost"])
with col5:
    @st.cache_data(ttl=60)
    def GetImpressionShare(campaign,period_choice):
        return GetData(
            db_name = "campaign",
            USE_MOTHERDUCK=True,
            ACCESS_TOKEN = DashboardConfig.ACCESS_TOKEN,
            query = QueryImpressionShare(campaign=campaign, 
                                        period_choice = period_choice))

    #4th row
    st.header(f"Impression Share per Campaign in {pd.to_datetime(CHOICE,yearfirst=True).strftime('%B, %Y')}")
    selected_campaign = st.selectbox("Pilih Campaign",
                                    CAMPAIGN_LIST['campaign'],
                                    key = "selected_campaign")
    if selected_campaign:
        ImpressionShareData = GetImpressionShare(selected_campaign, CHOICE)
        if ImpressionShareData is not None and not ImpressionShareData.empty:
            labels = ["Impression Share", "Lost IS"]
            values = [
                ImpressionShareData["Impression Share"].iloc[0] * 100,
                ImpressionShareData["Lost IS"].iloc[0] * 100
            ]
            render_pie_chart(labels=labels, values=values)
        else:
            st.warning("Tidak ditemukan data untuk campaign ini")
    else:
        st.info("Silahkan pilih nama campaign untuk divisualkan")
    
col6,col7 = st.columns(2)
with col6:
    st.header(f"Marketing Funnel in {pd.to_datetime(CHOICE,yearfirst=True).strftime('%B, %Y')}")
    MarketFunnelPlot(df = FunnelDF,stages = funneling_stage)

TopKeywords = GetData(db_name="keyword",
                      ACCESS_TOKEN = DashboardConfig.ACCESS_TOKEN,
                      USE_MOTHERDUCK= True,
                      query=QueryTopKeywords(period_choice=CHOICE))
with col7:
    st.header(f"Top Keywords in {pd.to_datetime(CHOICE,yearfirst=True).strftime('%B, %Y')}")
    render_invertedbar_chart(categories=TopKeywords["Keywords"],
                             values=TopKeywords["Total Conversions"])
