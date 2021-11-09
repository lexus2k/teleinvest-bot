import pygsheets
from datetime import datetime
import time

class Stocks:
    def __init__(self):
        self._stocks = {}
        self._name = "<noname>"
        self._ideas_mode = False

    def load_from_ideas(self, sheet):
        self._stocks = {}
        self._name = sheet.title
        armed = 0
        vals = sheet.get_all_values()
        if vals[4][0] != "Ticker":
            return False
        idx = 6
        self._ideas_mode = True
        while True:
            if idx >= len(vals):
                break
            ticker = vals[idx][0] # sheet.cell('A{}'.format(idx)).value
            if ticker != "" and ord(ticker[0]) in range(ord('A'),ord('Z')):
                armed = 0
                if vals[idx][2] =="":
                    start_date = datetime.now()
                else:
                    start_date = datetime.strptime( vals[idx][2], "%d.%m.%Y" )
                if vals[idx][3] == "#N/A":
                    day_change = 0
                else:
                    day_change = float(vals[idx][3].replace(',','.')[:-1])
                if vals[idx][4] == "#N/A":
                    current_price = 0
                else:
                    current_price = float(vals[idx][4].replace(',','.'))
                min_price = float(vals[idx][7].replace(',','.'))
                max_price = float(vals[idx][8].replace(',','.'))
                stop = float(vals[idx][9].replace(',','.'))
                target = float(vals[idx][10].replace(',','.'))
                if  vals[idx][11] == "":
                    target_date = datetime.now()
                else:
                    target_date = datetime.strptime( vals[idx][11], "%d.%m.%Y" )

                self._stocks[ticker] = {
                    'buy': 0,
                    'count': 0,
                    'change': 0,
                    'day_change': day_change,
                    'price': current_price,
                    'target': target,
                    'stop': stop,
                    'min': min_price,
                    'max': max_price,
                    'start_date': start_date,
                    'target_date': target_date,
                }
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
        self._ideas_mode = False
        while True:
            if idx >= len(vals):
                break
            ticker = vals[idx][0] # sheet.cell('A{}'.format(idx)).value
            if ticker != "" and ord(ticker[0]) in range(ord('A'),ord('Z')):
                armed = 0
                buy_price = float(vals[idx][1].replace(',','.'))
                count = int(vals[idx][2].replace(',','.'))
                if vals[idx][4] == "#N/A":
                    change = 0
                else:
                    change = float(vals[idx][4].replace(',','.')[:-1])
                if vals[idx][6] == "#N/A":
                    day_change = 0
                else:
                    day_change = float(vals[idx][6].replace(',','.')[:-1])
                if vals[idx][7] == "#N/A":
                    current_price = 0
                else:
                    current_price = float(vals[idx][7].replace(',','.'))
                if vals[idx][13] == "#N/A":
                    target = 0
                else:
                    target = float(vals[idx][13].replace(',','.'))
                if vals[idx][12] == "#N/A":
                    stop = 0
                else:
                    stop = float(vals[idx][12].replace(',','.'))
                self._stocks[ticker] = {
                    'buy': buy_price,
                    'count': count,
                    'change': change,
                    'day_change': day_change,
                    'price': current_price,
                    'target': target,
                    'stop': stop,
                    'min': 0,
                    'max': 0,
                    'start_date': datetime.now(),
                    'target_date': datetime.now(),
                }
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
            if self._stocks[r]['price'] > self._stocks[r]['target']:
                result += u"\n\U00002716 {} {} > {}".format( r, self._stocks[r]['price'], self._stocks[r]['target'] )
        return result

    def find_for_stop(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r]['price'] < self._stocks[r]['stop']:
                result += u"\n\U00002716{} {} < {}".format( r, self._stocks[r]['price'], self._stocks[r]['stop'] )
        return result

    def find_for_averaging(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r]['change'] < -9.0 and self._stocks[r]['price'] > self._stocks[r]['stop']:
                result += u"\n\U00002716{} {} < {} ({}%)".format( r, self._stocks[r]['price'], self._stocks[r]['buy'],
                          round(self._stocks[r]['change'],1) )
        return result

    def find_high_grow(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r]['day_change'] >= 3.0:
                result += u"\n\U00002716{} {} {} ({}%)".format( r, self._stocks[r]['price'], self._stocks[r]['buy'],
                          round(self._stocks[r]['day_change'], 1) )
        return result

    def find_high_fall(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r]['day_change'] <= -3.0:
                result += u"\n\U00002716{} {} {} ({}%)".format( r, self._stocks[r]['price'], self._stocks[r]['buy'],
                          round(self._stocks[r]['day_change'], 1) )
        return result

    def find_to_buy(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r]["price"] >= self._stocks[r]["min"] and \
               self._stocks[r]["price"] <= self._stocks[r]["max"] and \
               datetime.now() - self._stocks[r]["start_date"] < (self._stocks[r]["target_date"] - self._stocks[r]["start_date"])/2:
               result += u"\n\U00002716{} {} ({}%) in [{};{}] => {} (+{}%)".format(r, self._stocks[r]['price'],
                          self._stocks[r]["day_change"], self._stocks[r]["min"], self._stocks[r]["max"], self._stocks[r]["target"],
                          round((self._stocks[r]["target"] - self._stocks[r]['price']) / self._stocks[r]['price'] * 100 ,1))
        return result

    def find_near_to_buy(self):
        result = ""
        for r in self._stocks:
            if self._stocks[r]["price"] > self._stocks[r]["max"] and \
               self._stocks[r]["price"] <= self._stocks[r]["max"] + ( self._stocks[r]["target"] - self._stocks[r]["max"]) * 0.1 and \
               datetime.now() - self._stocks[r]["start_date"] < (self._stocks[r]["target_date"] - self._stocks[r]["start_date"])/2:
               result += u"\n\U00002716{} {} ({}%) > {} => {} (+{}%)".format(r, self._stocks[r]['price'],
                          self._stocks[r]["day_change"], self._stocks[r]["max"], self._stocks[r]["target"],
                          round((self._stocks[r]["target"] - self._stocks[r]['price']) / self._stocks[r]['price'] * 100 ,1))
        return result

    def get_report(self):
        result = u"\n=== {} ===".format(self._name)
        if self._ideas_mode:
            r = self.find_to_buy()
            if len(r) > 0:
                result += u"\n\n\U0001F31F Comfortable buy price:" + r
            r = self.find_near_to_buy()
            if len(r) > 0:
                result += u"\n\n\U0001F31F Maybe to buy:" + r
        else:
            r = self.find_for_sell()
            if len(r) > 0:
                result += u"\n\n\U0001F31F Target reached:" + r
            r = self.find_high_grow()
            if len(r) > 0:
                result += u"\n\n\U0001F4B9 High day grow:" + r
            r = self.find_high_fall()
            if len(r) > 0:
                result += u"\n\n\U0001F53B day fall:" + r
            r = self.find_for_averaging()
            if len(r) > 0:
                result += u"\n\n\U000026C8 To average:" + r
            r = self.find_for_stop()
            if len(r) > 0:
                result += u"\n\n\U0001F4DB Stop reached:" + r
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
            stocks = []

            for i in range(len(doc.worksheets())):
                s = Stocks()
                if s.load_from_sheet( doc.worksheet('index', i)):
                    stocks.append( s )
                    result += s.get_report() + "\n"
                    # print(result)
            for i in range(len(doc.worksheets())):
                s = Stocks()
                if s.load_from_ideas( doc.worksheet('index', i)):
                    result += s.get_report() + "\n"
            del gc
            success = True
        except:
            # raise
            pass
        if success:
            break
        retries += 1
        time.sleep(5)
    return result


if __name__=="__main__":
    gc = pygsheets.authorize()
    # You can open a spreadsheet by its title as it appears in Google Docs
    doc = gc.open("Test doc")
    s = Stocks()
    s.load_from_ideas( doc.worksheet('index', 5))
    print(s.get_report())
