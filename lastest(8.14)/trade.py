from pyalgotrade import plotter  
from pyalgotrade.stratanalyzer import returns, sharpe, drawdown, trades  
from pyalgotrade import strategy  
from pyalgotrade.bar import Frequency  
from pyalgotrade.barfeed.csvfeed import GenericBarFeed  
from pyalgotrade.technical import ma  
# 1.构建一个策略  
class MyStrategy(strategy.BacktestingStrategy):  
    def __init__(self, feed, instrument):  
        super(MyStrategy, self).__init__(feed)  
        self.__position = None  
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 150)  
        self.__instrument = instrument  
        self.getBroker()  
    def onEnterOk(self, position):  
        execInfo = position.getEntryOrder().getExecutionInfo()  
        self.info("BUY at %.2f" % (execInfo.getPrice()))  
  
    def onEnterCanceled(self, position):  
        self.__position = None  
  
    def onExitOk(self, position):  
        execInfo = position.getExitOrder().getExecutionInfo()  
        self.info("SELL at $%.2f" % (execInfo.getPrice()))  
        self.__position = None  
  
    def onExitCanceled(self, position):  
        # If the exit was canceled, re-submit it.  
        self.__position.exitMarket()  
  
    def getSMA(self):  
        return self.__sma  
  
    def onBars(self, bars):# 每一个数据都会抵达这里，就像becktest中的next  
  
        # Wait for enough bars to be available to calculate a SMA.  
        if self.__sma[-1] is None:  
            return  
        #bar.getTyoicalPrice = (bar.getHigh() + bar.getLow() + bar.getClose())/ 3.0  
  
        bar = bars[self.__instrument]  
        # If a position was not opened, check if we should enter a long position.  
        if self.__position is None:  
            if bar.getPrice() > self.__sma[-1]:  
                # 开多头.  
                self.__position = self.enterLong(self.__instrument, 100, True)  
        # 平掉多头头寸.  
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():  
            self.__position.exitMarket()  
  
# 2.获得回测数据，官网来源于yahoo，由于墙的关系，我们用本地数据  
feed = GenericBarFeed(Frequency.DAY, None, None)  
feed.addBarsFromCSV("fd", "8-11.csv")  
  
# 3.实例化策略  
myStrategy = MyStrategy(feed, "fd")  
# 4.设置指标和绘图  
sharpe_ratio = sharpe.SharpeRatio()  
myStrategy.attachAnalyzer(sharpe_ratio)  
plt = plotter.StrategyPlotter(myStrategy)  
  
# 5.运行策略  
myStrategy.run()  
myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())  
  
# 6.输出夏普率、绘图  
print ("sharpe_ratio", sharpe_ratio.getSharpeRatio(0))  
plt.plot()