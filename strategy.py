from backtrader.feeds import PandasData
import backtrader as bt
import backtrader.analyzers as btanalyzers
import pandas as pd


class PandasData(PandasData):

    '''
    The ``dataname`` parameter inherited from ``feed.DataBase`` is the pandas
    DataFrame
    '''
    lines = ('state',)
    params = (
        ('datetime', 0),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', None),
        ('openinterest', None),
        ('state', 5),
    )
    datafields = PandasData.datafields + (['state'])

class MarketStatus(bt.Strategy): 


    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        #print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization

    def __init__(self):
        self.dataclose = self.datas[0].close

        # Order variable will contain ongoing order details/status
        self.order = None

        # Instantiate market status
        self.state = self.datas[0].state

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):

        # Check for open orders
        if self.order:
            return
        
        if self.state[0] == 1:
            if not self.position:
                #print('no position',self.state[0], self.position.size)
                self.log(f'BUY CREATE {self.dataclose[0]:2f} {self.state[0]:2f}')
                self.order = self.buy()
            elif self.position.size < 0: # already have a sell order
                #print('sell position',self.state[0], self.position.size)
                self.order = self.close()
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.log(f'BUY CREATE {self.dataclose[0]:2f} {self.state[0]:2f}')
                self.order = self.buy()
            elif self.position.size > 0: # already have a buy order
                # pass
                # self.log(f'BUY CREATE {self.dataclose[0]:2f} {self.state[0]:2f}')
                # self.order = self.buy()

                if len(self) == (self.bar_executed + 5):
                    #print('buy position, 5 days',self.state[0], self.position.size)
                    # self.order = self.close()
                    # self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                    self.log(f'BUY CREATE {self.dataclose[0]:2f} {self.state[0]:2f}')
                    self.order = self.buy()
                    self.log('Chase')
                elif len(self) >= (self.bar_executed + 15):
                    self.order = self.close()
                    self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                else:
                    #print('buy position, less than 5 days',self.state[0], self.position.size)
                    pass
            else:
                #print('error',self.state[0], self.position.size)
                pass
        
        elif self.state[0] == -1:
            if not self.position:
                #print('no position',self.state[0], self.position.size)                
                self.log(f'SELL CREATE {self.dataclose[0]:2f} {self.state[0]:2f}')
                self.order = self.sell()
            elif self.position.size > 0: # already have a buy order
                #print('sell position',self.state[0], self.position.size)                
                self.order = self.close()
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.log(f'SELL CREATE {self.dataclose[0]:2f} {self.state[0]:2f}')
                self.order = self.sell()
            elif self.position.size < 0: # already have a sell order
                # pass
                # Chase every order
                # self.log(f'SELL CREATE {self.dataclose[0]:2f} {self.state[0]:2f}')
                # self.order = self.sell()

                # Chase 10 
                if len(self) == (self.bar_executed + 5):
                    #print('buy position, 5 days',self.state[0], self.position.size)
                    # self.order = self.close()
                    # self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                    self.log(f'SELL CREATE {self.dataclose[0]:2f} {self.state[0]:2f}')
                    self.order = self.sell()
                    # self.log('Chase')
                elif len(self) >= (self.bar_executed + 15):
                    self.order = self.close()
                    self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                else:
                    #print('buy position, less than 5 days',self.state[0], self.position.size)
                    pass

            else:
                #print('error',self.state[0], self.position.size)
                pass
        
        else:
            if not self.position:
                #print('0, nothing',self.state[0], self.position.size)
                pass
            else:
                self.log(f'Hold {self.dataclose[0]:2f} {self.state[0]:2f}')

class TestPositions(bt.Strategy):
    def __init__(self):
        pass

    def log(self, txt, dt=None):
        """ Logging function fot this strategy"""
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print("%s, %s" % (dt, txt))

    def print_signal(self):
        self.log(
            f"o {self.datas[0].open[0]:7.2f} "
            f"h {self.datas[0].high[0]:7.2f} "
            f"l {self.datas[0].low[0]:7.2f} "
            f"c {self.datas[0].close[0]:7.2f} "
            f"v {self.datas[0].volume[0]:7.0f} "
        )

    def next(self):
        self.print_signal()
        
class BuyAndHold(bt.Strategy):

    def log(self,txt,dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') #Print date and close
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        self.order = None
    def notify_order(self,order):
        if order.status in [order.Submitted, order.Accepted]:
			# An active Buy/Sell order has been submitted/accepted - Nothing to do
            return
        
        # Check if an order has been completed
		# Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
    def next(self):
        # Check for open orders
        if self.order:
            return
        self.log(f'BUY CREATE {self.dataclose[0]:2f}')
        self.order = self.buy()

