#!/usr/bin/env python
# coding: utf-8
"""
    __init__.py
    ~~~~~~~~~~

"""
import json
from datetime import datetime
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA, SHA256
from Crypto.PublicKey import RSA

from .compat import quote_plus, urlopen, decodebytes, encodebytes
from .exceptions import AliPayException


class AliPay():
    __REFUND_GATEWAY = "https://openapi.alipay.com/gateway.do"

    @property
    def appid(self):
        return self.__appid

    @property
    def partner(self):
        return self.__partner

    @property
    def sign_type(self):
        return self.__sign_type

    def __init__(self,
                 appid=None,
                 app_notify_url=None,
                 app_private_key_path=None,
                 app_alipay_public_key_path=None,
                 partner=None,
                 web_notify_url=None,
                 web_private_key_path=None,
                 web_alipay_public_key_path=None,
                 sign_type="RSA2",
                 debug=False):
        """
        # app, wap支付:
        alipay = AliPay(
          app_notify_url="", appid="", app_private_key_path="", app_alipay_public_key_path=""
        )
        # web支付:
        alipay = AliPay(
          web_notify_url=, partner=, partner_private_key_path=, partner_alipay_public_key_path=
        )
        # 如果你想要同时支持三种支付方式，将所有参数传入
        """
        self.__appid = appid
        self.__partner = partner
        self.__app_notify_url = app_notify_url
        self.__app_private_key_path = app_private_key_path
        self.__app_alipay_public_key_path = app_alipay_public_key_path
        self.__web_notify_url = web_notify_url
        self.__web_private_key_path = web_private_key_path
        self.__web_alipay_public_key_path = web_alipay_public_key_path
        if sign_type not in ("RSA", "RSA2"):
            raise AliPayException(None, "Unsupported sign type {}".format(sign_type))
        self.__sign_type = sign_type

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def __ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def __check_internal_configuration(self, paid_type):
        if paid_type in ("wap", "app"):
            assert self.__appid, "appid is not configured"
            assert self.__app_notify_url, "app_notify_url is not configured"
            assert self.__app_private_key_path, "app_private_key_path is not configured"
            assert self.__app_alipay_public_key_path, "app_alipay_public_key_path is not configured"
        else:
            assert self.__partner, "partner is not configured"
            assert self.__web_notify_url, "web_notify_url is not configured"
            assert self.__web_private_key_path, "web_private_key_path is not configured"
            assert self.__web_alipay_public_key_path, "web_alipay_public_key_path is not configured"

    def _sign(self, unsigned_string, private_key_path):
        """
        通过如下方法调试签名
        方法1
            key = rsa.PrivateKey.load_pkcs1(open(self.__private_key_path).read())
            sign = rsa.sign(unsigned_string.encode("utf8"), key, "SHA-1")
            # base64 编码，转换为unicode表示并移除回车
            sign = base64.encodebytes(sign).decode("utf8").replace("\n", "")
        方法2
            key = RSA.importKey(open(self.__private_key_path).read())
            signer = PKCS1_v1_5.new(key)
            signature = signer.sign(SHA.new(unsigned_string.encode("utf8")))
            # base64 编码，转换为unicode表示并移除回车
            sign = base64.encodebytes(signature).decode("utf8").replace("\n", "")
        方法3
            echo "abc" | openssl sha1 -sign alipay.key | openssl base64

        """
        # 开始计算签名
        with open(private_key_path) as fp:
            key = RSA.importKey(fp.read())
            signer = PKCS1_v1_5.new(key)
            if self.__sign_type == "RSA":
                signature = signer.sign(SHA.new(unsigned_string.encode("utf8")))
            else:
                signature = signer.sign(SHA256.new(unsigned_string.encode("utf8")))
            # base64 编码，转换为unicode表示并移除回车
            sign = encodebytes(signature).decode("utf8").replace("\n", "")
            return sign

    def sign_data_with_private_key(self, data, private_key_path):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.__ordered_data(data)
        unsigned_string = "&".join("{}={}".format(k, v) for k, v in unsigned_items)
        return self._sign(unsigned_string, private_key_path)

    def create_app_trade(self, out_trade_no, total_amount, subject, **kwargs):
        self.__check_internal_configuration("app")

        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "QUICK_MSECURITY_PAY"
        }
        biz_content.update(kwargs)
        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.app.pay",
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.__app_notify_url,
            "biz_content": biz_content
        }
        return self.sign_trade(data, self.__app_private_key_path)

    def create_wap_trade(self, out_trade_no, total_amount, subject, return_url, **kwargs):
        self.__check_internal_configuration("wap")

        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "QUICK_MSECURITY_PAY"
        }
        biz_content.update(kwargs)
        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.wap.pay",
            "format": "JSON",
            "return_url": return_url,
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.__app_notify_url,
            "biz_content": {
            }
        }
        return self.sign_trade(data, self.__app_private_key_path)

    def create_web_trade(self, out_trade_no, total_amount, subject, return_url, **kwargs):
        self.__check_internal_configuration("web")

        data = {
            "service": "create_direct_pay_by_user",
            "partner": self.__partner,
            "_input_charset": "UTF-8",
            "notify_url": self.__web_notify_url,
            "return_url": return_url,
            "out_trade_no": out_trade_no,
            "subject": subject,
            "payment_type": "1",
            "total_fee": str(total_amount),
            "seller_id": self.__partner
        }
        data.update(kwargs)

        # 注意web支付类型，sign_type 不参与签名
        return self.sign_trade(data, self.__web_private_key_path) +\
            "&sign_type=" + self.__sign_type

    def sign_trade(self, data, private_key_path):
        sign = self.sign_data_with_private_key(data, private_key_path)
        ordered_items = self.__ordered_data(data)
        quoted_string = "&".join("{}={}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def verify_app_notify(self, data, signature):
        return self.verify_notify(data, signature, self.__app_alipay_public_key_path)

    def verify_wap_notify(self, data, signature):
        return self.verify_app_notify(data, signature)

    def verify_web_notify(self, data, signature):
        return self.verify_notify(data, signature, self.__web_alipay_public_key_path)

    def _verify(self, raw_content, signature, publickey_path):
        # 开始计算签名
        with open(publickey_path) as fp:
            key = RSA.importKey(fp.read())
            signer = PKCS1_v1_5.new(key)
            if self.__sign_type == "RSA":
                digest = SHA.new()
            else:
                digest = SHA256.new()
            digest.update(raw_content.encode("utf8"))
            if signer.verify(digest, decodebytes(signature.encode("utf8"))):
                return True
            return False

    def verify_notify(self, data, signature, alipay_public_key_path):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
            if sign_type != self.__sign_type:
                raise AliPayException(None, "Unknown sign type: {}".format(sign_type))
        # 排序后的字符串
        unsigned_items = self.__ordered_data(data)
        message = "&".join("{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature, alipay_public_key_path)

    def refund_web_order(self, **kwargs):
        return self.refund(self.__partner, self.__web_private_key_path, **kwargs)

    def refund_app_order(self, **kwargs):
        return self.refund(self.__appid, self.__app_private_key_path, **kwargs)

    def refund_wap_order(self, **kwargs):
        return self.refund_app_order(**kwargs)

    def refund(self, appid, private_key_path, **kwargs):
        """
        Please refer to https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=759

        kwargs = {
            "out_trade_no": "",
            "trade_no": "",
            "refund_amount": "",
            "refund_reason": "",
            "out_request_no": "",
            "operator_id": "", # optional
            "store_id": "", # optional
            "terminal_id": "" # optional
        }
        """
        data = {
            "app_id": appid,
            "method": "alipay.trade.refund",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": kwargs
        }
        sign = self.sign_data_with_private_key(data, private_key_path)

        ordered_items = self.__ordered_data(data)
        quoted_string = "&".join("{}={}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)

        url = self.__REFUND_GATEWAY + "?" + signed_string
        r = urlopen(url, timeout=15)
        result = r.read().decode("utf-8")
        result = json.loads(result)["alipay_trade_refund_response"]
        if result["code"] != "10000":
            raise AliPayException(result["code"], result["sub_msg"])

        return result

    def create_face_to_face_trade(self, out_trade_no, scene, auth_code, subject, **kwargs):
        """
        Pleasse refer to https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=850

        failed response = {
            "alipay_trade_pay_response": {
                "code": "40004",
                "msg": "Business Failed",
                "sub_code": "ACQ.INVALID_PARAMETER",
                "sub_msg": "",
                "buyer_pay_amount": "0.00",
                "invoice_amount": "0.00",
                "point_amount": "0.00",
                "receipt_amount": "0.00"
            },
            "sign": ""
        }
        succeeded response =
            {
              "alipay_trade_pay_response": {
                "trade_no": "2017032121001004070200176846",
                "code": "10000",
                "invoice_amount": "20.00",
                "open_id": "20880072506750308812798160715407",
                "fund_bill_list": [
                  {
                    "amount": "20.00",
                    "fund_channel": "ALIPAYACCOUNT"
                  }
                ],
                "buyer_logon_id": "csq***@sandbox.com",
                "receipt_amount": "20.00",
                "out_trade_no": "out_trade_no18",
                "buyer_pay_amount": "20.00",
                "buyer_user_id": "2088102169481075",
                "msg": "Success",
                "point_amount": "0.00",
                "gmt_payment": "2017-03-21 15:07:29",
                "total_amount": "20.00"
              },
              "sign": ""
            }
        """
        self.__check_internal_configuration("app")
        assert scene in ("bar_code", "wave_code"), 'scene not in ("bar_code", "wave_code")'

        biz_content = {
            "out_trade_no": out_trade_no,
            "scene": scene,
            "auth_code": auth_code,
            "subject": subject
        }
        biz_content.update(**kwargs)
        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.pay",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        url = self.__gateway + "?" + self.sign_trade(data, self.__app_private_key_path)
        response = urlopen(url, timeout=15)
        result = json.loads(response.read())

        # 10000: 支付成功; 40004:支付失败; 10003:等待用户付款; 20000: 支付异常
        if result["alipay_trade_pay_response"]["code"] in ("40004", "20000"):
            result = result["alipay_trade_pay_response"]
            raise AliPayException(result["code"], result["sub_msg"])
        return result

    def query_face_to_face_trade(self, **kwargs):
        """
        Please refer to https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=757

        response = {
          "alipay_trade_query_response": {
            "trade_no": "2017032121001004070200176844",
            "code": "10000",
            "invoice_amount": "20.00",
            "open_id": "20880072506750308812798160715407",
            "fund_bill_list": [
              {
                "amount": "20.00",
                "fund_channel": "ALIPAYACCOUNT"
              }
            ],
            "buyer_logon_id": "csq***@sandbox.com",
            "send_pay_date": "2017-03-21 13:29:17",
            "receipt_amount": "20.00",
            "out_trade_no": "out_trade_no15",
            "buyer_pay_amount": "20.00",
            "buyer_user_id": "2088102169481075",
            "msg": "Success",
            "point_amount": "0.00",
            "trade_status": "TRADE_SUCCESS",
            "total_amount": "20.00"
          },
          "sign": ""
        }
        """
        biz_content = {}
        biz_content.update(**kwargs)
        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.query",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        url = self.__gateway + "?" + self.sign_trade(data, self.__app_private_key_path)
        response = urlopen(url, timeout=15)
        return json.loads(response.read())["alipay_trade_query_response"]

    def cancel_face_to_face_trade(self, **kwargs):
        """
        Please refer to https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=866

        response = {
        "alipay_trade_cancel_response": {
            "msg": "Success",
            "out_trade_no": "out_trade_no15",
            "code": "10000",
            "retry_flag": "N"
          }
        }
        """
        biz_content = {}
        biz_content.update(**kwargs)
        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.cancel",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        url = self.__gateway + "?" + self.sign_trade(data, self.__app_private_key_path)
        response = urlopen(url, timeout=15)
        return json.loads(response.read())["alipay_trade_cancel_response"]

    def precreate_face_to_face_trade(self, out_trade_no, total_amount, subject, **kwargs):
        """
        Pleasse refer to https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=850
        success response  = {
          "alipay_trade_precreate_response": {
            "msg": "Success",
            "out_trade_no": "out_trade_no17",
            "code": "10000",
            "qr_code": "https://qr.alipay.com/bax03431ljhokirwl38f00a7"
          },
          "sign": ""
        }

        failed response = {
          "alipay_trade_precreate_response": {
            "msg": "Business Failed",
            "sub_code": "ACQ.TOTAL_FEE_EXCEED",
            "code": "40004",
            "sub_msg": "订单金额超过限额"
          },
          "sign": ""
        }

        """
        self.__check_internal_configuration("app")

        biz_content = {
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "subject": subject
        }
        biz_content.update(**kwargs)
        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.precreate",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        url = self.__gateway + "?" + self.sign_trade(data, self.__app_private_key_path)
        response = urlopen(url, timeout=15)
        result = json.loads(response.read())

        # 10000: 支付成功; 40004:支付失败; 10003:等待用户付款; 20000: 支付异常
        if result["alipay_trade_precreate_response"]["code"] in ("40004", "20000"):
            result = result["alipay_trade_precreate_response"]
            raise AliPayException(result["code"], result["sub_msg"])
        return result
