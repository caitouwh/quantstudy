# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import datetime

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # context.s1 = "000001.XSHE"
    context.stocks = [('2015-06-30', '000012.XSHE'),
    ('2015-07-08', '000012.XSHE'),
    ('2015-07-11', '000002.XSHE'),
    ('2015-07-25', '000002.XSHE'),
    ('2015-07-28', '000601.XSHE'),
    ('2015-08-08', '000601.XSHE'),
    ('2015-08-08', '600872.XSHG'),
    ('2015-08-14', '000601.XSHE'),
    ('2015-08-27', '000002.XSHE'),
    ('2015-09-15', '600872.XSHG'),
    ('2015-09-18', '000417.XSHE'),
    ('2015-09-18', '600101.XSHG'),
    ('2015-09-22', '600712.XSHG'),
    ('2015-09-23', '600872.XSHG'),
    ('2015-10-01', '600872.XSHG'),
    ('2015-10-22', '600712.XSHG'),
    ('2015-11-03', '000012.XSHE'),
    ('2015-12-07', '000002.XSHE')
    ]
    # 实时打印日志
    logger.info("Interested at stock: " + str(context.stocks))
    context.to_buy_list = []

# before_trading此函数会在每天交易开始前被调用，当天只会被调用一次
def before_trading(context, bar_dict):
    pass

# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    for stock_tuple in context.stocks:
        jupai_stock_date = datetime.datetime.strptime(stock_tuple[0], "%Y-%m-%d").date()
        # 判断是否已经到了举牌日当日，如果是的话买入对应的这个股票，从tuple中拿出来股票代码
        if jupai_stock_date.day == context.now.day:
            logger.info("Jupai Trading signal triggerd: " + str(stock_tuple))
            # 判断是否停盘等无法交易
            if bar_dict[stock_tuple[1]].is_trading:
                order_target_percent(stock_tuple[1], 0.15)
            else:
                context.to_buy_list.append(stock_tuple[1])
            logger.info("context.to_buy_list: " + str(context.to_buy_list))
            logger.info('Bought: ' + stock_tuple[1] + 'for 15%')
        
        # 继续去保持每天买入之前举牌股，但是当时停牌了
        if len(context.to_buy_list) != 0:
            for stock_code in context.to_buy_list:
                if bar_dict[stock_code].is_trading:
                    order_target_percent(stock_code, 0.1)
                    logger.info("买入了之前的停牌股：" + stock_code)
                    context.to_buy_list.remove(stock_code)
                    logger.info("left list: " + str(context.to_buy_list))
