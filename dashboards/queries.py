from config import DashboardConfig
import streamlit as st

def QueryConversionPerMonth(db_name,table,date_choice)->str:
    return f"""
SELECT SUM(conversions_{db_name})
FROM {table}
WHERE CAST(month_{db_name} AS DATE) = CAST('{date_choice}' AS DATE)
"""

def CountRunningCampaign(db_name,table,date_choice)->str:
    return f"""
    SELECT COUNT(campaign)
    FROM {table}
    WHERE campaign_status_{db_name} = 'Enabled' AND month_{db_name} = '{date_choice}'
    """

def QueryClickPerMonth(db_name,table,date_choice) -> str:
    return f""" SELECT 
SUM("clicks_{db_name}")
FROM {table}
WHERE month_{db_name} = '{date_choice}'
"""
def QueryConversionData(db_name, table)-> str:
    return f"""SELECT 
    month_{db_name},
    SUM(conversions_{db_name}) AS TotalConversions
    FROM {table}
    WHERE campaign_status_{db_name}='Enabled'
    GROUP BY month_{db_name}
    ORDER BY month_{db_name} ASC """

def QueryCampaignConv(db_name, table,period_choice)-> str:
    return f"""SELECT
    campaign,
    SUM(conversions_{db_name}) AS TotalConversions
    FROM {table}
    WHERE campaign_status_{db_name}='Enabled' and month_{db_name} = '{period_choice}'
    GROUP BY campaign
    """
def QueryCostCampaign(db_name,table,period_choice)->str:
    return f"""SELECT
    campaign,
    SUM(cost_{db_name}) AS TotalCost
    FROM {table}
    WHERE month_{db_name} = '{period_choice}'
    GROUP BY campaign
    """

def FunnelStaging(period_choice):
    return f""" 
    SELECT 
    SUM("impr._campaign") AS "Total Impression",
    SUM(clicks_campaign) AS "Total Visitor",
    SUM(conversions_campaign) AS "Total Conversion",
    SUM(phone_call_lead_campaign + submit_lead_form_campaign + leads_from_messages_campaign) AS "Total Potential Leads"
    FROM CampaignReport
    WHERE month_campaign = '{period_choice}'
    """
def QueryTopKeywords(period_choice):
    return f"""
    SELECT 
    keyword_keyword AS "Keywords",
    SUM(conversions_keyword) AS "Total Conversions"
    FROM keyword.KeywordReport
    WHERE month_keyword = '{period_choice}'
    GROUP BY keyword_keyword
    ORDER BY "Total Conversions" DESC
    LIMIT 10
    """

def QueryImpressionShare(campaign,period_choice):
    return f"""
    SELECT
    campaign,
    CAST("search_impr._share_campaign" AS FLOAT) AS "Impression Share",
    CAST("search_lost_is_(rank)_campaign" AS FLOAT) AS "Lost IS"
    FROM CampaignReport
    WHERE month_campaign = '{period_choice}' AND campaign = '{campaign}'
    ORDER BY "Impression Share" DESC 
    """
def GetCampaignList(period_choice):
    return f"""
    SELECT 
    DISTINCT campaign
    FROM CampaignReport
    WHERE month_campaign = '{period_choice}'
    """

def GetCPL(table,
           grouping_category,
           cost_columns,
           leads_columns,
           start_period=None,
           end_period=None,
           sort='ASC'):
    """
    1.cost_columns:SQL table column, column that show cost of ads spend
    2.leads_columns:SQL table column, column that show leads gained
    3.period_choice:datetime, define the period here
    """
    where_clause=""
    if start_period and end_period:
        where_clause=f'WHERE month_{table} BETWEEN {start_period} AND {end_period}'

    return f"""
        SELECT
        DISTINCT {grouping_category},
        calculate_CPL(SUM({cost_columns}),SUM({leads_columns})) as CPL
        FROM {table}
        {where_clause}
        GROUP BY {grouping_category}
        ORDER BY {grouping_category} {sort}
        """

def GetCPM(table,
           grouping_category,
           cost_columns,
           impression_columns,
           start_period=None,
           end_period=None,
           sort = 'ASC'):
    
    where_clause=""

    if start_period and end_period:
        where_clause = f"WHERE month_{table} BETWEEN '{start_period}' AND {end_period}"

    return f"""
        SELECT
        DISTINCT {grouping_category},
        calculate_CPM(SUM({cost_columns}),SUM("{impression_columns}")) as CPM
        FROM {table}
        {where_clause}
        GROUP BY {grouping_category}
        ORDER BY {grouping_category} {sort}
        """
          
def GetCPC(table,grouping_category,
           cost_columns,clicks_columns,start_period=None,end_period=None,
           sort='ASC'):
    
    where_clause=""

    if start_period and end_period:
        where_clause=f"WHERE month_{table} BETWEEN {start_period} AND {end_period}"

    return f"""
    SELECT
    DISTINCT {grouping_category},
    calculate_CPC(SUM({cost_columns}),SUM({clicks_columns})) AS CPC
    FROM {table}
    GROUP BY {grouping_category}
    {where_clause}
    ORDER BY {grouping_category} {sort}
    """