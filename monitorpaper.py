# Monitor Stop Loss/ stats while doing paper trading with Day Trade GUI
from Background.MyDatabase import DBHelper
from Background.Zeroda import Zeroda
import datetime
import time
from Background.zerodaPaper import ZerodaPaper
from Background.zerodaFake import ZerodaFake
global kws, kite

class MonitorPaper:
    userid = 'PC6587'
    api_key = "ieccnxhin3wzxew3"
    apisecret = "91ifln271qj38hbvlcof8dgbzaw2efor"
    #zeroda = Zeroda(api_key, apisecret)
    test_date = datetime.date(2021, 3, 3)
    zeroda = ZerodaPaper(api_key, apisecret)
    #zeroda = ZerodaFake(test_date)
    helper = DBHelper()
    status = False;
    def __init__(self):
        self.status = self.zeroda.Initiate()
        self.env = 'Real'
        if type(self.zeroda).__name__ == 'ZerodaPaper':
            self.env = 'Paper'
            
    def main(self):
        monitor = True
        while monitor == True:
            time.sleep(1)
            self.zeroda.advance_time('10sec')
            print('------- Paper Trade --------')            
            nw = self.zeroda.getCurrentDateTime()
            print(nw)
            #tdate = datetime.datetime.today().strftime('%Y-%m-%d')
            tdate = self.zeroda.getCurrentDate()
            to_date = datetime.datetime(nw.year, nw.month, nw.day, 1,0,0)
            edate = datetime.datetime(nw.year, nw.month, nw.day, 18,30,0)
            orderid = ''
            instrument = ''
            exchange = ''
            transaction = ''
            direction = ''
            qty = 1
            interval = 'minute'
            #Place Stop Loss orders for complete orders
            complete_orders = self.helper.GetOrdersListCompleted(to_date, edate, self.userid, 'COMPLETE','Fresh', 'None')
            for index, row in complete_orders.iterrows():
                orderid = row['zerodha_id']
                instrument = row['instrument']
                qty = int(row['qty'])
                exchange = row['exchange']
                transaction = row['transaction_type']
                triggerprice = round(row['price_executed']) 
                neworderid = 0
                original_price = triggerprice
                dfTrade = self.helper.getActiveTradeDetails(instrument, self.userid)
                trade_id = dfTrade._get_value(0, 'id')
                stop_loss = dfTrade._get_value(0, 'stop_loss_points')
                repurchase_points = dfTrade._get_value(0, 'repurchase_points')
                index_ltp = dfTrade._get_value(0, 'index_ltp')
                index = dfTrade._get_value(0, 'index_name')
                direction = dfTrade._get_value(0, 'direction')
                if direction == 'Bullish':
                    triggerprice = index_ltp - stop_loss
                    repurchase_price = index_ltp + repurchase_points
                    info = 'Index Stop Loss update: ' + str(index) + ' triggerprice:' + str(triggerprice) + ' repurchase_price:' + str(repurchase_price) + ' original_price:' + str(index_ltp)
                    self.helper.insertTradeLog(tdate,'MonitorCurrentPosition-Day Trade', 'Index Stop Loss Order initiated ', info, 1, nw)
                    self.helper.updateDailyTradeStopLoss(trade_id, triggerprice, repurchase_price)
                    self.helper.changeStopLossOrderStatus('Placed', orderid)
                elif direction == 'Bearish':
                    triggerprice= index_ltp + stop_loss
                    repurchase_price = index_ltp - repurchase_points
                    info = 'Index Stop Loss update: ' + str(index) + ' triggerprice:' + str(triggerprice) + ' repurchase_price:' + str(repurchase_price) + ' original_price:' + str(index_ltp)
                    self.helper.insertTradeLog(tdate,'MonitorCurrentPosition-Day Trade', 'Index Stop Loss Order initiated ', info, 1, nw)
                    self.helper.updateDailyTradeStopLoss(trade_id, triggerprice, repurchase_price)
                    self.helper.changeStopLossOrderStatus('Placed', orderid)
            #Trail SL & Repurchase
            active_orders = self.helper.GetOrdersListCompleted(to_date, edate, self.userid, 'COMPLETE','Fresh', 'Placed')
            if len(active_orders) == 0:
                #monitor = False
                print('No active orders')
            for index, row in active_orders.iterrows():
                orderid = row['zerodha_id']
                #print('orderid:' + str(orderid))
                instrument = row['instrument']
                qty = int(row['qty'])
                exchange = row['exchange']
                transaction = row['transaction_type']
                original_price = round(row['price_executed']) 
                dfTrade = self.helper.getActiveTradeDetails(instrument, self.userid)
                if len(dfTrade) > 0:
                    #print('len > 0')
                    trade_id = dfTrade._get_value(0, 'id')
                    stop_loss_value = dfTrade._get_value(0, 'index_stoploss')
                    repurchase_value = dfTrade._get_value(0, 'index_repurchase_target')
                    index_original_ltp = dfTrade._get_value(0, 'index_ltp')
                    index_name = dfTrade._get_value(0, 'index_name')
                    index_token = dfTrade._get_value(0, 'index_token')
                    lot_size = dfTrade._get_value(0, 'initial_qty')
                    current_qty = dfTrade._get_value(0, 'current_qty')
                    stop_loss_points = dfTrade._get_value(0, 'stop_loss_points')
                    repurchase_points = dfTrade._get_value(0, 'repurchase_points')
                    direction = dfTrade._get_value(0, 'direction')
                    index_new_ltp = self.zeroda.getCurrentLTP(index_token)
                    #print('update m2m')
                    self.zeroda.updateM2M(instrument)
                    if direction == 'Bullish':
                        print('In Bulish')
                        if index_new_ltp <= stop_loss_value:
                            print('Square off')
                            if transaction == 'BUY':
                                self.zeroda.PlaceSELLOrderMarket(instrument, current_qty)
                            else:
                                self.zeroda.PlaceBuyOrderMarket(instrument, current_qty)
                            self.helper.updateOrderStatus('Closed', orderid)
                            self.helper.updateTradeStatus(0, 'close', trade_id)
                            self.helper.insertTradeLog(nw,'DayTrade Graphic Utility', 'Squared off order on ' + instrument,' ltp: ' + str(index_new_ltp), 2, nw)
                        if index_new_ltp >= repurchase_value:
                            print('Purchase More')
                            if transaction == 'BUY':
                                self.zeroda.PlaceBuyOrderMarket(instrument, abs(lot_size))
                                new_qty = qty + lot_size
                            else:
                                self.zeroda.PlaceSELLOrderMarket(instrument, abs(lot_size))
                                new_qty = qty - lot_size
                            self.helper.updateOrderQty(new_qty, orderid)
                            index_stoploss = index_new_ltp - stop_loss_points
                            repurchase_price = index_new_ltp + repurchase_points
                            self.helper.updateTradeCurrentValues(new_qty, index_stoploss,repurchase_price, trade_id)
                            self.helper.insertTradeLog(nw,'DayTrade Graphic Utility', 'Purchase More ' + instrument,' ltp: ' + str(index_new_ltp), 2, nw)
                    elif direction == 'Bearish':
                        print('In Bearish')
                        print('index_new_ltp: ' + str(index_new_ltp))
                        print('stop_loss_value: ' + str(stop_loss_value))
                        if index_new_ltp >= stop_loss_value:
                            print('Square off')
                            if transaction == 'BUY':
                                self.zeroda.PlaceSELLOrderMarket(instrument, abs(current_qty))
                            else:
                                self.zeroda.PlaceBuyOrderMarket(instrument, abs(current_qty))
                            self.helper.updateOrderStatus('Closed', orderid)
                            self.helper.updateTradeStatus(0, 'close', trade_id)
                            self.helper.insertTradeLog(nw,'DayTrade Graphic Utility', 'Squared off order on ' + instrument,' ltp: ' + str(index_new_ltp), 2, nw)
                        if index_new_ltp <= repurchase_value:
                            print('Repurchase')
                            if transaction == 'BUY':
                                self.zeroda.PlaceBuyOrderMarket(instrument, abs(lot_size))
                                new_qty = qty + lot_size
                            else:
                                self.zeroda.PlaceSELLOrderMarket(instrument, abs(lot_size))
                                new_qty = qty - lot_size
                            print('new_qty: ' + str(new_qty))
                            self.helper.updateOrderQty(new_qty, orderid)
                            index_stoploss = index_new_ltp + stop_loss_points
                            repurchase_price = index_new_ltp - repurchase_points   
                            self.helper.updateTradeCurrentValues(new_qty, index_stoploss,repurchase_price, trade_id)
                            self.helper.insertTradeLog(nw,'DayTrade Graphic Utility', 'SELL More ' + instrument, ' ltp: ' + str(index_new_ltp) + ' Stop Loss revised: ' + str(index_stoploss), 2, nw)
                else:
                    #monitor = False
                    print('No active trades found')
            
if __name__ == '__main__':
    MonitorPaper().main()
