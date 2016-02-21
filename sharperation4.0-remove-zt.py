import pandas as pd
import numpy as np

def init(context):
    context.s1 = '000001.XSHG'
    context.max_num_stocks = 40
    context.days = 0
    context.period_days = 1
    context.relative_strength_6m = {}

def period_passed(context): 
    return context.days % context.period_days == 0
    
def before_trading(context): 
    context.days += 1
    if not period_passed(context):
        return
    
    dofilter(context)
    update_universe(context.fundamental_df.columns.values)

def dofilter(context):
    
    fundamental_df = get_fundamentals(
        query(fundamentals.eod_derivative_indicator.market_cap)
        .order_by(fundamentals.eod_derivative_indicator.market_cap.asc())
        .limit(context.max_num_stocks)
    )
   
    #Update context
    context.stocks = [stock for stock in fundamental_df]
    context.fundamental_df = fundamental_df
    
def rebalance(context, bar_dict):
   
    for stock in context.portfolio.positions:
        if stock not in context.fundamental_df:
            order_target_percent(stock, 0)
            
    context.stocks = [stock for stock in context.stocks
                      if stock in bar_dict and bar_dict[stock].is_trading and not high_enough(stock, bar_dict) and context.relative_strength_6m[stock] <-0.5]
   
    if len(context.stocks) == 0:
        return
    
    weight = 1.0/len(context.stocks)
    
    for stock in context.stocks:
        order_target_percent(stock, weight)
    
def handle_bar(context, bar_dict):
    
    his = history(10, '1d', 'close')['000001.XSHG']
    
    if period_passed(context):
        if his[9]/his[8]< 0.97:
            if len(context.portfolio.positions)>0:
                for stock in context.portfolio.positions.keys():
                    order_target_percent(stock, 0)
            return
    
    if not period_passed(context):
        return
    
    compute_relative_strength(context,bar_dict)
    rebalance(context, bar_dict)
    
def compute_relative_strength(context,bar_dict):
    
    prices = history (150, '1d', 'close')

    #过去六个月的价格变化率
    pct_change = (prices.ix[149] - prices.ix[19]) / prices.ix[19]
    #print(prices.ix[19])
    #print(pct_change)
    priceofbase = history (150, '1d', 'close')[context.s1]
    pct_changeforbase = (priceofbase.ix[149] - priceofbase.ix[19]) / priceofbase.ix[19]
    pct_change = pct_change - pct_changeforbase
    print(pct_change.index)
    print(bar_dict)
    if pct_changeforbase != 0:
        pct_change = pct_change / abs(pct_changeforbase)
    context.relative_strength_6m = pct_change
    
def high_enough(stock, bar_dict):
    
    price = history (2, '1d', 'close')[stock].ix[0]
    # logger.info("yesterday close: " + str(price) + " today close: " + str(bar_dict[stock].close))
    pricenow = bar_dict[stock].open
    pct_change = (pricenow - price) / price
    return pct_change>0.099
