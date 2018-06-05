# encoding: utf-8
"""
提供WindPy接口的pandas封装
"""
from math import isnan
# thd
import pandas as pd
from datetime import timedelta, datetime
# app
from WindPy import w
from pyfi.mapper import mapper


class WindHelper(object):
    """
    WindPy20170904更新
    在本次修改后, 下面函数结果中的时间Times将只包含日期date: 
    wsd, tdays, tdayscount, tdaysoffset, wset, weqs, wpd, htocode, edb
    常用字段：
    close
    settle
    volume
    """

    # 常见edb代码映射表
    """
    ip=工业增加值：当月同比
    cpi=CPI:当月同比(月）
    cpif=CPI食品：当月同比
    cpinf=CPI非食品：当月同比
    """
    mapper = mapper

    @classmethod
    def translate(cls, code):
        if type(code) == list:
            return [cls.mapper[x] if x in cls.mapper else x for x in code]
        else:
            if code in cls.mapper:
                return cls.mapper[code]
            else:
                return code

    @classmethod
    def wsd(cls, code, paras, begin_date, end_date, options="credibility=1"):
        """单代码多维日期序列
        或者多代码单维日期序列
        注意：wind并不支持多代码多维的数据提取
        :param code: (list) 一次只能一个品种
        :param paras: (list) fields
        :param begin_date: (datetime or str)如 '20150101'
        :param end_date: （datetime or str) 如 '20150101'
        :param options: （string） xx=xx;yy=yy 不支持大小写
        :return: pandas.DataFrame
        """
        if begin_date > end_date:
            return None
        code = cls.mapper[code] if code in cls.mapper else code
        try:
            if not w.isconnected():
                w.start()
            # 校验，防止codes和paras同时为长度大于1的list
            if type(code) == list and type(paras) == list:
                if len(code) > 1 and len(paras) > 1:
                    raise Exception(u"wsd不能提取多代码多维度数据")
            if type(code) == list and len(code) == 1:
                code = code[0]
            code = cls.translate(code=code)
            options = options
            wind_data = w.wsd(code, paras, begin_date, end_date, options)
            if wind_data is None:
                raise Exception(u"wsd调用wind服务端异常，数据为空")
            if len(wind_data.Data) == 0:
                raise Exception(u"wsd调用wind服务端异常，数据为空")
            if len(wind_data.Data[0]) == 0:
                raise Exception(u"wsd调用wind服务端异常，数据为空")
            if "CWSDService: invalid windcodes." in wind_data.Data[0]:
                raise Exception(wind_data.Data[0])
            if "CWSDService: No data." in wind_data.Data[0]:
                return None
            dataDict = {}
            for i in range(len(wind_data.Data)):
                dataDict[wind_data.Fields[i].lower()] = wind_data.Data[i]
            df = pd.DataFrame(dataDict, index=wind_data.Times)
            # 将date类型转换为datetime类型
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"
            return df
        except Exception as e:
            print(format(e))
            raise

    @classmethod
    def wss(cls, codes, paras):
        """多代码多维信息序列
        :param codes:(list) or (str)
        :param paras:(list) or (str)
        :return:(DataFrame);
        """

        try:
            if not w.isconnected():
                w.start()
            if type(codes) is not list:
                codes = codes.split(",")  # 全部转换为list格式
            codes = [cls.mapper[x] if x in cls.mapper else x for x in codes]
            if type(paras) is not list:
                paras = paras.split(",")
            paras.insert(0, "windcode")
            windData = w.wss(codes,
                             paras, options=None)
            if len(windData.Data) == 0:
                return None
            if len(windData.Data[0]) == 0:
                return None
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Fields[i].lower()] = windData.Data[i]
            df = pd.DataFrame(dataDict)
            df = df[paras]
            df.rename(columns={"windcode": "code"}, inplace=True)
            return df
        except BaseException as e:
            print(format(e))
            raise

    @classmethod
    def edb(cls, codes, begin_date, end_date, options="fill=perious"):
        """多代码单维时间序列
        :param codes: 
        :param begin_date: 
        :param end_date: 
        :param options: 
        :return: 
        """
        if begin_date > end_date:
            return None
        if not w.isconnected():
            w.start()
        if type(codes) is not list:
            codes = codes.split(",")  # 全部转换为list格式
        codes = [cls.mapper[x] if x in cls.mapper else x for x in codes]
        try:
            if not w.isconnected:
                w.start()
            windData = w.edb(codes, begin_date, end_date, options)
            if len(windData.Data) == 0:
                return None
            if len(windData.Data[0]) == 0:
                return None
            dataDict = {}
            for i in range(len(windData.Data)):
                col = windData.Codes[i]
                if col in cls.mapper.values():
                    col = list(cls.mapper.keys())[list(cls.mapper.values()).index(col)]
                dataDict[col] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(format(e))
            raise

    @classmethod
    def wsi(cls, code, fields, trade_date, num_retries=2):
        """单代码多维"""
        try:
            if type(trade_date) in (datetime, pd._libs.tslib.Timestamp):
                trade_date = trade_date.strftime("%Y%m%d")
            if type(fields) is list:
                fields = ",".join(fields)
            if type(code) is list:
                code = ",".join(code)
            w.start()
            result = w.wss(code, fields, "tradeDate=" + trade_date + ";credibility=1").Data[0]
            if result[0] == u'CWSSService: invalid indicators.' and len(result) == 0:
                raise Exception("CWSSService: invalid indicators.")
            result = [0.0 if isnan(x) else x for x in result]
            return tuple(result) if len(result) > 1 else result[0]
        except Exception as e:
            if num_retries > 0:
                num_retries -= 1
                cls.wsi(code, fields, trade_date, num_retries=num_retries)

    @staticmethod
    def getMultiTimeSeriesDataFrame(codeList, beginDate, endDate, para, period="",
                                    tradingCalendar="", priceAdj="", credibility=0):
        """
        para只能是一个参数
        get time series from windPy, each code represents one capture
         月度合约: trade_hiscode
           :param credibility: (int)
           :param codeList: (list)
           :param beginDate: (date or datetime)
           :param endDate: (date or datetime)
           :param para: (string)只能是一个字符参数
           :param period: (int) 频率
           :param tradingCalendar: (string)   交易日历，选择可以选择银行间:NIB,不选择，则默认交易所日历
           :param priceAdj: (string) 价格是否调整,F:前复权，B:后复权
           :return: (DataFrame)
        """
        try:
            w.start()
            codeListStr = ",".join(codeList)
            period = ("Period=" + period) if period == "W" else ""
            tradingCalendar = ("TradingCalendar=" + tradingCalendar) if tradingCalendar != "" else ""
            priceAdj = ("priceAdj=" + priceAdj) if priceAdj != "" else ""
            credibility = ("credibility=" + str(credibility)) if credibility != 0 else ""
            windData = w.wsd(codeListStr,
                             para,
                             beginDate.strftime("%Y-%m-%d"),
                             endDate.strftime("%Y-%m-%d"),
                             period,
                             tradingCalendar,
                             priceAdj, credibility)
            if len(windData.Data) == 0:
                raise BaseException
            if len(windData.Data[0]) == 0:
                raise BaseException
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Codes[i].lower() + "_" + para] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(format(e))
            raise

    @staticmethod
    def getTimeSeriesDataFrame(code, beginDate, endDate, paraList, period="",
                               tradingCalendar="", priceAdj="", credibility=0):
        """
        get time series from windPy, each code represents one capture
         月度合约: trade_hiscode
           :param credibility: (int)
           :param code: (string)
           :param beginDate: (date or datetime)
           :param endDate: (date or datetime)
           :param paraList: (list)
           :param period: (str) W or D 频率
           :param tradingCalendar: (string)   交易日历，选择可以选择银行间:NIB,不选择，则默认交易所日历
           :param priceAdj: (string) 价格是否调整,F:前复权，B:后复权
           :return: (DataFrame)
        """
        try:
            w.start()
            para = ",".join(paraList)
            period = ("Period=" + period) if period == "W" else ""
            tradingCalendar = ("TradingCalendar=" + tradingCalendar) if tradingCalendar != "" else ""
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
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(format(e))
            raise

    @staticmethod
    def getMinTimeSeriesDataFrame(code, beginDate, endDate, paraList, bar_size=1):
        """
        获取分钟级别数据
        get time series from windPy, each code represents one capture
         月度合约: trade_hiscode
           :param bar_size: (int)  The frequency of the data
           :param code: string
           :param beginDate: date or datetime
           :param endDate: date or datetime
           :param paraList: list
           :return: DataFrame
        """
        try:
            w.start()
            para = ",".join(paraList)
            bar_size = "" + str(bar_size) if bar_size is not None else ""
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
            print(format(e))
            raise

    @staticmethod
    def getInfoDataFrame(code, paraList):
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
            print(format(e))
            raise

    @staticmethod
    def getEDBTimeSeriesDataFrame(codeList, beginDate, endDate, fillChoice="Previous"):
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
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(format(e))
            raise

    @staticmethod
    def t_days_offset(offset=0, cur_date=datetime.now()):
        try:
            w.start()
            result = w.tdaysoffset(offset, cur_date, "").Data[0][0]
            return result
        except IndexError as e:
            print(format(e))
            raise

    @staticmethod
    def tdays_count(begin_date, end_date):
        w.start()
        result = w.tdayscount(begin_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "").Data[0][0]
        return result

    @classmethod
    def all_tf_codes(cls, begin_date=None, end_date=None, contract_type="T"):
        """
        获取指定时间段内所有国债期货的合约
        :return type: list
        """
        if begin_date is None and contract_type == "T":
            begin_date = datetime(2015, 3, 20)
        elif begin_date is None and contract_type == "TF":
            begin_date = datetime(2013, 9, 6)
        if end_date is None:
            end_date = datetime.now()
        w.start()
        near_code = contract_type.upper() + "00.CFE"
        far_code = contract_type.upper() + "01.CFE"
        farfar_code = contract_type.upper() + "02.CFE"
        para = "trade_hiscode"
        near_df = cls.wsd(code=near_code, paras=para, begin_date=begin_date, end_date=end_date).dropna()
        # 国债期货下季列表
        far_df = cls.wsd(code=far_code, paras=para, begin_date=begin_date, end_date=end_date).dropna()
        # 国债期货隔季合约
        farfar_df = cls.wsd(code=farfar_code, paras=para, begin_date=begin_date, end_date=end_date).dropna()
        # 获取国债期货时间序列基础表：
        # 日期，当季合约，当季结算价，持仓量，下季合约，下季结算价，持仓量，隔季合约，隔季结算价，持仓量
        base_df = pd.DataFrame(near_df).append(far_df).append(farfar_df)
        if len(base_df) == 0:
            return None
        contract_code_list = base_df["trade_hiscode"].unique().tolist()
        return list(sorted(contract_code_list))

    @classmethod
    def tdays(cls, begin_date, end_date):
        """生成时间序列List"""
        w.start()
        return w.tdays(begin_date, end_date, "").Data[0]

    @classmethod
    def tf_dbs(cls, code, market="IB"):
        w.start()
        para = "windcode=" + code
        data = w.wset("conversionfactor", para).Data
        bondCodeList = data[0]
        cfList = data[1]
        dlvBdCodeDict = {}
        for i in range(len(bondCodeList)):
            bondCode = bondCodeList[i]
            if market in bondCode:
                dlvBdCodeDict[bondCode] = cfList[i]
        return dlvBdCodeDict

    @classmethod
    def get_end_date(cls):
        """确定开始时间，计算最新的已经结算的交易日"""
        # 确定结束时间
        # 结束时间为该合约的最后交易日和当前日期的最小值
        last_trade_date = cls.t_days_offset(offset=0, cur_date=datetime.now())
        # 确定结束时间
        if datetime.now().hour >= 19:  # 以晚上19点为界限
            end_date = last_trade_date
        elif datetime.now().date() > last_trade_date.date():  # 当天不是交易日
            end_date = last_trade_date
        else:  # 既非节假日，且当然的数据也没有生成
            end_date = cls.t_days_offset(offset=-1, cur_date=datetime.now())  # datetime类型
        return end_date

    @classmethod
    def get_dv01(cls, codes):
        """获取个券或者组合的dv01"""
        pass
