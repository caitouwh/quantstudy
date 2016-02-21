from math import log


# set parameters
def init(context):
    context.index = "000001.XSHG"
    context.small_cap_num = 50
    context.stop_index_drop = -0.03
    context.win_length = 126
    context.rel_return = -0.5
    
    # schedule rebalance function
    scheduler.run_daily(rebalance, time_rule=market_open(0,30))

# select small-cap stocks with number of small_cap_num
def before_trading(context, bar_dict):
    fundamental_df = get_fundamentals(query().order_by(fundamentals.eod_derivative_indicator.market_cap.asc()).limit(context.small_cap_num))
    context.stocks = fundamental_df.columns.values
    update_universe(context.stocks)


# open/close orders
def rebalance(context, bar_dict):
    # close stock positions not in the current universe
    for stock in context.portfolio.positions.keys():
        if stock not in context.stocks:
            order_target_percent(stock, 0)
    
    # close all positions when index drops by stop_index_drop
    index_hist = history(2, "1d", "close")[context.index]
    index_return_1d = log(index_hist[1]/index_hist[0])
    if index_return_1d < context.stop_index_drop:
        for stock in context.stocks:
            order_target_percent(stock, 0)
        return
    
    # narrow down stock universe: not in suspension + relative strength < -0.5
    stock_hist = history(context.win_length, "1d", "close")
    stock_return = (stock_hist.ix[context.win_length-1]-stock_hist.ix[0])/stock_hist.ix[0]
    index_return = stock_return[context.index]
    rel_return = stock_return - index_return
    context.stocks = [stock for stock in context.stocks if bar_dict[stock].is_trading and bar_dict[stock].open<1.095*stock_hist[stock].iloc[-1] and bar_dict[stock].open>0.905*stock_hist[stock].iloc[-1] and rel_return[stock]<abs(index_return)*context.rel_return]
    
    # place equally weighted orders
    if len(context.stocks) == 0:
        return
    weight = 1.0/len(context.stocks)
    for stock in context.stocks:
        order_target_percent(stock, weight)
    
    
# handle data
def handle_bar(context, bar_dict):
    pass
    
    
