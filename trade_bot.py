#!/usr/bin/python3
import pygsheets
from datetime import datetime, timedelta
import time
# import yfinance as yf
import time
import configparser
import requests

def request_yahoo_info(tickers):
    pass

def request_yahoo_history(tickers, begin, end, period = "1d"):
    hist = {}
    host = "https://query2.finance.yahoo.com/v8/finance/chart/"
    ux_begin = int(time.mktime(begin.timetuple()))
    ux_end = int(time.mktime(end.timetuple()))
    n = 0
    while n < len(tickers):
        # Yahoo API limits max 10 tickers for comparision, or single for request
        # Documentation https://www.yahoofinanceapi.com/
        tickers_list = tickers[n:n + min( len(tickers) - n, 1 )]
        # print(tickers_list)
        n += 1
        for retries in range(3):
            try:
                # result = requests.post(host, data = {"period1": ux_begin, "period2": ux_end, "interval": period, "includePrePost": "False", "events": "div,splits"}, timeout=2)
                url = host + tickers_list[0] + "?period1={}&period2={}&interval={}&includePrePost=False&events=div%2Csplits".format( ux_begin, ux_end, period)
                # print(url)
                result = requests.get(url, timeout=2, headers={'User-agent': 'Mozilla/5.0'})
                result = result.json()
                break
            except:
                result = None
        if result is not None:
            for rec in result['chart']['result']:
                hist[rec['meta']['symbol']] = {
                    "Size": len(list(filter(lambda x: x is not None, rec['indicators']['quote'][0]['close']))),
                    "Close": [float(x) for x in filter(lambda x: x is not None, rec['indicators']['quote'][0]['close'])],
                    "Open": [float(x) for x in filter(lambda x: x is not None, rec['indicators']['quote'][0]['open'])],
                    "High": [float(x) for x in filter(lambda x: x is not None, rec['indicators']['quote'][0]['high'])],
                    "Low": [float(x) for x in filter(lambda x: x is not None, rec['indicators']['quote'][0]['low'])],
                    "Volume": [float(x) for x in filter(lambda x: x is not None, rec['indicators']['quote'][0]['volume'])],
                }
    # print(hist)
    return hist


def google_ticker_to_yahoo( t ):
    ticker = t
    if ticker[0:4] == "MCX:":
        ticker = ticker[4:] + ".ME"
    if ticker[0:4] == "FRA:":
        ticker = ticker[4:] + ".DE"
    if ticker[0:5] == "NYSE:":
        ticker = ticker[5:]
    return ticker

#def get_ticker_info( tickers ):
#    updated_tickers = []
#    for t in tickers.split(' '):
#        updated_tickers.append( google_ticker_to_yahoo( t ) )
#    info = None
#    for i in range(3):
#        try:
#            if len( updated_tickers ) > 1:
#                stock = yf.Tickers(updated_tickers)
#            else:
#                stock = yf.Ticker(updated_tickers[0])
#            # stock.tickers[ticker].info
#            break
#        except Exception as e:
#            # raise
#            hist = []
#            pass
#        time.sleep(1.0)
#    return info


def get_history_prices( tickers, period="1da" ):
    updated_tickers = []
    for t in tickers.split(' '):
        updated_tickers.append( google_ticker_to_yahoo( t ) )
    start = datetime.now() + timedelta(days=-14)
    end = datetime.now()
    hist = request_yahoo_history(updated_tickers, start, end)
    return hist


class Stock:
    def __init__(self, ticker):
        self._ticker = ticker
        self._count = 0
        self._bid = 0
        self._day_change = 0
        self._change = 0
        self._target = 0
        self._stop = 0
        self._min_price = 0
        self._max_price = 0
        self._buy_price = 0 # Average price of buys
        self._target_date = datetime.now()
        self._start_date = datetime.now()
        self._end_date = datetime.now()
        self._history = []

    def load_as_asset(self, record):
        try:
            self._buy_price = float(record[1].replace(',','.'))
            self._count = int(record[2].replace(',','.'))
            if record[4] == "#N/A":
                self._change = 0
            else:
                self._change = float(record[4].replace(',','.')[:-1])
            if record[6] == "#N/A":
                self._day_change = 0
            else:
                self._day_change = float(record[6].replace(',','.')[:-1])
            if record[7] == "#N/A":
                self._bid = 0
            else:
                self._bid = float(record[7].replace(',','.'))
            if record[13] == "#N/A":
                self._target = 0
            else:
                self._target = float(record[13].replace(',','.'))
            if record[12] == "#N/A":
                self._stop = 0
            else:
                self._stop = float(record[12].replace(',','.'))
            hist = get_history_prices( self._ticker )
            if google_ticker_to_yahoo(self._ticker) in hist:
                self._history = hist[google_ticker_to_yahoo(self._ticker)]
        except:
            raise
            return False
        return True

    def load_as_idea(self, record):
        try:
            if record[2] =="":
                self._start_date = datetime.now()
            else:
                self._start_date = datetime.strptime( record[2], "%d.%m.%Y" )
            if record[3] == "#N/A":
                self._day_change = 0
            else:
                self._day_change = float(record[3].replace(',','.')[:-1])
            if record[4] == "#N/A":
                self._bid = 0
            else:
                self._bid = float(record[4].replace(',','.'))
            self._min_price = float(record[7].replace(',','.'))
            self._max_price = float(record[8].replace(',','.'))
            self._stop = float(record[9].replace(',','.'))
            self._target = float(record[10].replace(',','.'))
            if  record[11] == "":
                self._target_date = datetime.now()
            else:
                self._target_date = datetime.strptime( record[11], "%d.%m.%Y" )
            self._history = []
        except:
            raise
            return False
        return True

    def get_ticker_presentation(self):
        if self._bid < self._stop:
            return u"\U0001F534" + self._ticker
        if self._bid > self._target:
            return u"\U0001F7E2" + self._ticker
        if self._bid < self._buy_price * 0.96:
            return u"\U0001F7E1" + self._ticker
        if self._bid > self._buy_price * 1.04:
            return u"\U0001F535" + self._ticker
        return u"\U000026AA" + self._ticker

    def is_profit(self):
        return self._bid > self._target

    def get_profit_report(self):
        return u"\n{} {} > {}".format( self.get_ticker_presentation(), self._bid, self._target )

    def is_loss(self):
        return self._bid < self._stop

    def get_loss_report(self):
        return u"\n{} {} < {}".format( self.get_ticker_presentation(), self._bid, self._stop )

    def is_averaging_required(self):
        return self._change < -9.0 and self._bid > self._stop

    def get_averaging_report(self):
        return u"\n{} {} < {} ({}%)".format( self.get_ticker_presentation(), self._bid, self._buy_price, round(self._change,1) )

    def is_high_grow(self):
        if self._day_change >= 3.0:
            return True
        if self._day_change > 0:
            # Looking for the history data
            hist = self._history
            if hist is not None and hist["Size"] > 3:
                rise_change = 0
                rise_days = 1
                for i in range(hist["Size"]):
                    perc = round((self._bid - hist["Close"][-i-1]) * 100/self._bid,1 )
                    if rise_change < perc:
                        rise_change = max([rise_change,perc])
                        rise_days = i + 1
                if rise_change/rise_days > 1.0 and rise_days >= 3:
                    return True
        return False

    def get_grow_report(self):
        # Looking for the history data
        hist = self._history
        if hist is not None and hist["Size"] > 3:
            rise_change = 0
            rise_days = 1
            for i in range(hist["Size"]):
                perc = round((self._bid - hist["Close"][-i-1]) * 100/self._bid,1 )
                if rise_change < perc:
                    rise_change = max([rise_change,perc])
                    rise_days = i + 1
            return u"\n{} {} {} ({}% today, {}% in {} days)".format( self.get_ticker_presentation(), self._bid, self._buy_price,
                       round(self._day_change, 1), rise_change, rise_days)
        return u"\n{} {} {} ({}% today)".format( self.get_ticker_presentation(), self._bid, self._buy_price,
                 round(self._day_change, 1))

    def is_high_fall(self):
        if self._day_change <= -3.0:
            return True
        if self._day_change < 0:
            hist = self._history
            if hist is not None and hist["Size"] > 3:
                fall_change = 0
                fall_days = 1
                for i in range(hist["Size"]):
                    perc = round((self._bid - hist["Close"][-i-1]) * 100/self._bid,1 )
                    if fall_change > perc:
                        fall_change = min([fall_change,perc])
                        fall_days = i + 1
                if fall_change/fall_days < -0.8:
                    return True
        return False

    def get_fall_report(self):
        hist = self._history
        if hist is not None and hist["Size"] > 3:
            fall_change = 0
            fall_days = 1
            for i in range(hist["Size"]):
                perc = round((self._bid - hist["Close"][-i-1]) * 100/self._bid,1 )
                if fall_change > perc:
                    fall_change = min([fall_change,perc])
                    fall_days = i + 1
            return u"\n{} {} {} ({}% today, {}% in {} days)".format( self.get_ticker_presentation(), self._bid, self._buy_price,
                              round(self._day_change, 1), fall_change, fall_days)
        return u"\n{} {} {} ({}% today)".format( self.get_ticker_presentation(), self._bid, self._buy_price, round(self._day_change, 1) )


    def is_worth_buying(self):
        return self._bid >= self._min_price and \
            self._bid <= self._max_price and \
            self._bid <= self._target * 0.98 and \
            datetime.now() - self._start_date < (self._target_date - self._start_date)/2

    def get_buying_report(self):
        target_perc = round( (self._target - self._bid) / self._bid * 100, 1)
        return ( target_perc,
                 u"\n\U0001F4A1{} {} ({}%) in [{};{}] => {} (+{}%)".format( self._ticker, self._bid,
                          self._day_change, self._min_price, self._max_price, self._target, target_perc) )

    def is_almost_worth_buying(self):
        return self._bid > self._max_price and \
               self._bid <= self._target * 0.98 and \
               self._bid <= self._max_price + ( self._target - self._max_price) * 0.1 and \
               datetime.now() - self._start_date < (self._target_date - self._start_date)/2

    def get_almost_buying_report(self):
        target_perc = round( (self._target - self._bid) / self._bid * 100, 1)
        return ( target_perc, u"\n\U00002754{} {} ({}%) > {} => {} (+{}%)".format(self._ticker, self._bid,
                 self._day_change, self._max_price, self._target, target_perc) )



class Stocks:
    def __init__(self):
        self._stocks = {}
        self._name = "<noname>"
        self._mode = "stock"

    def load_from_summary(self, sheet):
        vals = sheet.get_all_values()
        self._mode = "summary"
        self._name = "Summary"
        if vals[7][4] == "#N/A":
            self._total = 0
        else:
            self._total = float(vals[7][4].replace(',','.'))
        if vals[7][3] == "#N/A":
            self._investments = 1
        else:
            self._investments = float(vals[7][3].replace(',','.'))
        return True

    def load_from_ideas(self, sheet):
        self._stocks = {}
        self._name = sheet.title
        armed = 0
        vals = sheet.get_all_values()
        if vals[4][0] != "Ticker":
            return False
        self._mode = "ideas"
        armed = 0
        idx = 6
        tickers = []
        while True:
            if idx >= len(vals):
                break
            ticker = vals[idx][0] # sheet.cell('A{}'.format(idx)).value
            if ticker != "" and ord(ticker[0]) in range(ord('A'),ord('Z')):
                armed = 0
                stock = Stock(ticker)
                if stock.load_as_idea(vals[idx]):
                    self._stocks[ticker] = stock
            else:
                armed += 1
                if armed > 5:
                    break
            idx = idx + 1
        return True if len(self._stocks)>0 else False

    def load_from_sheet(self, sheet):
        self._stocks = {}
        self._name = sheet.title
        armed = 0
        vals = sheet.get_all_values()
        if vals[10][0] != "Ticker":
            return False
        idx = 12
        self._mode = "stock"
        tickers = []
        while True:
            if idx >= len(vals):
                break
            ticker = vals[idx][0] # sheet.cell('A{}'.format(idx)).value
            if ticker != "" and ord(ticker[0]) in range(ord('A'),ord('Z')):
                armed = 0
                stock = Stock(ticker)
                if stock.load_as_asset(vals[idx]):
                    self._stocks[ticker] = stock
            else:
                armed += 1
                if armed > 5:
                    break
            idx = idx + 1
        return True if len(self._stocks)>0 else False

    def to_string(self):
        return "{}".format(self._stocks)

    def find_for_sell(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r].is_profit():
                result += self._stocks[r].get_profit_report()
        return result

    def find_for_stop(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r].is_loss():
                result += self._stocks[r].get_loss_report()
        return result

    def find_for_averaging(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r].is_averaging_required():
                result += self._stocks[r].get_averaging_report()
        return result

    def find_high_grow(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r].is_high_grow():
                result += self._stocks[r].get_grow_report()
        return result

    def find_high_fall(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r].is_high_fall():
                result += self._stocks[r].get_fall_report()
        return result

    def find_to_buy(self):
        l = []
        result = ""
        for r in self._stocks:
            if self._stocks[r].is_worth_buying():
                l.append( self._stocks[r].get_buying_report() )
        l.sort(key=lambda rec: rec[0], reverse=True)
        for a in l:
            result += a[1]
        return result

    def find_near_to_buy(self):
        l = []
        result = ""
        for r in self._stocks:
            if self._stocks[r].is_almost_worth_buying():
                l.append( self._stocks[r].get_almost_buying_report() )
        l.sort(key=lambda rec: rec[0], reverse=True)
        for a in l:
            result += a[1]
        return result

    def get_summary(self):
        result = ""
        delta = round(self._total - self._investments,2)
        result += u"\n\U00002716Portfolio: {} = {} {} {} ({}%)".format(
            self._total, self._investments,
            "\U00002796" if delta < 0 else u"\U00002795",
            abs(delta),
            round(abs(delta) / self._investments * 100,2))
        return result

    def get_report(self):
        result = u"\n==== {} ====".format(self._name)
        if self._mode == "ideas":
            r = self.find_to_buy()
            if len(r) > 0:
                result += u"\n\n\U0001F31F Comfortable buy price:" + r
            r = self.find_near_to_buy()
            if len(r) > 0:
                result += u"\n\n\U0001F31F Maybe to buy:" + r
        elif self._mode == "stock":
            r = self.find_for_sell()
            if len(r) > 0:
                result += u"\n\n\U0001F31F Target reached:" + r
            r = self.find_high_grow()
            if len(r) > 0:
                result += u"\n\n\U0001F4B9 Rise:" + r
            r = self.find_high_fall()
            if len(r) > 0:
                result += u"\n\n\U0001F53B Fall:" + r
            r = self.find_for_averaging()
            if len(r) > 0:
                result += u"\n\n\U000026C8 To average:" + r
            r = self.find_for_stop()
            if len(r) > 0:
                result += u"\n\n\U0001F4DB Stop reached:" + r
        elif self._mode == "summary":
            result += u"\n\n\U0001F4B0" + self.get_summary()
        return result


def generate_stats_message( doc_name ):
    result = ""
    retries = 0
    while retries < 3:
        success = False
        try:
            gc = pygsheets.authorize()
            # You can open a spreadsheet by its title as it appears in Google Docs
            doc = gc.open( doc_name )
            s = Stocks()
            if s.load_from_summary( doc.worksheet('index', 0) ):
                result += s.get_report() + "\n"
            stocks = []
            for i in range(1, len(doc.worksheets())):
                s = Stocks()
                if s.load_from_sheet( doc.worksheet('index', i)):
                    stocks.append( s )
                    result += s.get_report() + "\n"
                    # print(result)
            for i in range(1, len(doc.worksheets())):
                s = Stocks()
                if s.load_from_ideas( doc.worksheet('index', i)):
                    result += s.get_report() + "\n"
            del gc
            success = True
        except:
            result = ""
            raise
            pass
        if success:
            break
        retries += 1
        time.sleep(5)
    return result


if __name__=="__main__":
    main_doc = None

    config = configparser.ConfigParser()
    if len( config.read( 'config.ini')) > 0:
        if config.has_option('main', 'sheets'):
            main_doc = config.get('main', 'sheets')
    print(generate_stats_message(main_doc))
