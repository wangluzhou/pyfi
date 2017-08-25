# encoding: utf-8
# thd
from WindPy import w
import pandas as pd
from datetime import timedelta, datetime


class WindHelper(object):
    """
    常用字段：
    close
    settle
    volume
    """

    @staticmethod
    def getWindMultiTimeSeriesDataFrame(codeList, beginDate, endDate, para, tradingCalendar="", priceAdj="",
                                        credibility=0):
        df_dict = dict()
        for code in codeList:
            df_dict["code"] = WindHelper.getWindTimeSeriesDataFrame(code, beginDate, endDate, para, tradingCalendar="",
                                                                    priceAdj="", credibility=0)
        return df_dict

    @staticmethod
    def getWindTimeSeriesDataFrame(code, beginDate, endDate, paraList,
                                   tradingCalendar="", priceAdj="", credibility=0):
        """
        get time series from windPy, each code represents one capture
         月度合约: trade_hiscode
           :param credibility: (int)
           :param code: (string)
           :param beginDate: (date or datetime)
           :param endDate: (date or datetime)
           :param paraList: (list)
           :param tradingCalendar: (string)   交易日历
           :param priceAdj: (string) 价格是否调整
           :return: (DataFrame)
        """
        try:
            w.start()
            para = ",".join(paraList)
            tradingCalendar = ("TradingCalendar=" + tradingCalendar) if tradingCalendar == "" else ""
            priceAdj = ("priceAdj=" + priceAdj) if priceAdj != "" else ""
            credibility = ("credibility=" + str(credibility)) if credibility != 0 else ""
            windData = w.wsd(code,
                             para,
                             beginDate.strftime("%Y-%m-%d"),
                             endDate.strftime("%Y-%m-%d"),
                             tradingCalendar,
                             priceAdj, credibility)
            if len(windData.Data) == 0:
                raise BaseException
            if len(windData.Data[0]) == 0:
                raise BaseException
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Fields[i].lower()] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            if df.index[0].to_pydatetime().microsecond != 0:
                df.index -= timedelta(microseconds=df.index[0].to_pydatetime().microsecond)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(e.message)
            raise

    @staticmethod
    def getWindMinTimeSeriesDataFrame(code, beginDate, endDate, paraList):
        """
        获取分钟级别数据
        get time series from windPy, each code represents one capture
         月度合约: trade_hiscode
           :param code: string
           :param beginDate: date or datetime
           :param endDate: date or datetime
           :param paraList: list
           :return: DataFrame
        """
        try:
            w.start()
            para = ",".join(paraList)
            windData = w.wsi(code,
                             para,
                             beginDate.strftime("%Y-%m-%d %H:%M:%S"),
                             endDate.strftime("%Y-%m-%d %H:%M:%S"), "")
            if len(windData.Data) == 0:
                raise BaseException
            if len(windData.Data[0]) == 0:
                raise BaseException
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Fields[i].lower()] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            if df.index[0].to_pydatetime().microsecond != 0:
                df.index -= timedelta(microseconds=df.index[0].to_pydatetime().microsecond)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(e.message)
            raise

    @staticmethod
    def getWindInfoDataFrame(code, paraList):
        """
        get info of one product by code
        :return: DataFrame
        :param code:
        :param paraList:
        :return:  DataFrame;
        """
        try:
            w.start()
            para = ",".join(paraList)
            windData = w.wss(code,
                             para)
            if len(windData.Data) == 0:
                return None
            if len(windData.Data[0]) == 0:
                return None
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Fields[i].lower()] = windData.Data[i]
            df = pd.DataFrame(dataDict)
            df = df[paraList]
            return df
        except BaseException as e:
            print(e.message)
            raise

    @staticmethod
    def getWindEDBTimeSeriesDataFrame(codeList, beginDate, endDate, fillChoice="Previous"):
        """
        宏观数据提取
        get edb time series from windPy, each code represents one capture
        : Param fillChoice: (string) previous或者None，空值数据是否需要被前一日的数据取代
        """
        codeListStr = ",".join(codeList)
        try:
            w.start()
            if fillChoice == "Previous":
                windData = w.edb(codeListStr,
                                 beginDate.strftime("%Y-%m-%d"),
                                 endDate.strftime("%Y-%m-%d"),
                                 "Fill=" + fillChoice)
            else:
                windData = w.edb(codeListStr,
                                 beginDate.strftime("%Y-%m-%d"),
                                 endDate.strftime("%Y-%m-%d"))
            if len(windData.Data) == 0:
                return None
            if len(windData.Data[0]) == 0:
                return None
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Codes[i]] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            if df.index[0].to_pydatetime().microsecond != 0:
                df.index -= timedelta(microseconds=df.index[0].to_pydatetime().microsecond)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(e.message)
            raise

    @staticmethod
    def getOffsetDays(offset=0, curDate=datetime.now()):
        try:
            w.start()
            result = w.tdaysoffset(offset, curDate.strftime("%Y-%m-%d"), "").Data[0][0]
            return result
        except IndexError as e:
            print(e.message)
            raise

    @staticmethod
    def adjustDatetimeindex(df):
        if df.index[0].to_pydatetime().microsecond != 0:
            df.index -= timedelta(microseconds=df.index[0].to_pydatetime().microsecond)
        return df

    @staticmethod
    def daysCount(firstDate, secondDate):
        w.start()
        result = w.tdayscount(firstDate.strftime("%Y-%m-%d"), secondDate.strftime("%Y-%m-%d"), "").Data[0][0]
        return result

    @staticmethod
    def getAllTrsFtCodes(beginDate, endDate):
        w.start()
        pass


def test():
    beginDate = datetime(2008, 12, 1)
    endDate = datetime(2017, 8, 22)
    WindHelper.getWindEDBTimeSeriesDataFrame(["M0327992","M0062650","M0000612"], beginDate=beginDate, endDate=endDate)
    # code = "T1612.CFE"
    # paraList = ["settle",
    #             "volume"]
    # df = WindHelper.getWindTimeSeriesDataFrame(code=code, beginDate=datetime(2016,5,1),endDate=datetime(2016,12,11), paraList=paraList)
    # print(df)


if __name__ == "__main__":
    test()
