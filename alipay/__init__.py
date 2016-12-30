#!/usr/bin/env python
# coding: utf-8
"""
    __init__.py
    ~~~~~~~~~~

"""
import json
import base64
from datetime import datetime
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA

from .compat import quote_plus


class AliPay():
    @property
    def appid(self):
        return self.__appid

    def __init__(self,
                 appid=None,
                 app_notify_url=None,
                 app_private_key_path=None,
                 app_alipay_public_key_path=None,
                 partner=None,
                 web_notify_url=None,
                 web_private_key_path=None,
                 web_alipay_public_key_path=None):
        """
        # app, wap支付:
        alipay = AliPay(
          notify_url="", appid="", app_private_key_path="", app_alipay_public_key_path=""
        )
        # web支付:
        alipay = AliPay(
          notify_url="", partner="", partner_private_key_path="", partner_alipay_public_key_path=""
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

    def __ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign_data_with_private_key(self, data, private_key_path):
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
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.__ordered_data(data)
        unsigned_string = "&".join("{}={}".format(k, v) for k, v in unsigned_items)

        # 开始计算签名
        key = RSA.importKey(open(private_key_path).read())
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA.new(unsigned_string.encode("utf8")))
        # base64 编码，转换为unicode表示并移除回车
        sign = base64.encodestring(signature).decode("utf8").replace("\n", "")
        return sign

    def create_app_trade(self, out_trade_no, total_amount, subject):
        assert self.__appid, "appid为空"
        assert self.__app_notify_url, "app_notify_url为空"
        assert self.__app_private_key_path, "app_private_key_path为空"
        assert self.__app_alipay_public_key_path, "app_alipay_public_key_path为空"

        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.app.pay",
            "charset": "utf-8",
            "sign_type": "RSA",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.__app_notify_url,
            "biz_content": {
                "subject": subject,
                "out_trade_no": out_trade_no,
                "total_amount": total_amount,
                "product_code": "QUICK_MSECURITY_PAY"
            }
        }
        return self.create_trade(data, self.__app_private_key_path)

    def create_wap_trade(self, out_trade_no, total_amount, subject, return_url):
        assert self.__appid, "appid为空"
        assert self.__app_notify_url, "app_notify_url为空"
        assert self.__app_private_key_path, "app_private_key_path为空"
        assert self.__app_alipay_public_key_path, "app_alipay_public_key_path为空"

        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.wap.pay",
            "format": "JSON",
            "return_url": return_url,
            "charset": "utf-8",
            "sign_type": "RSA",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.__app_notify_url,
            "biz_content": {
                "subject": subject,
                "out_trade_no": out_trade_no,
                "total_amount": total_amount,
                "product_code": "QUICK_MSECURITY_PAY"
            }
        }
        return self.create_trade(data, self.__app_private_key_path)

    def create_web_trade(self, out_trade_no, total_amount, subject, return_url):
        assert self.__partner, "partner为空"
        assert self.__web_notify_url, "web_notify_url为空"
        assert self.__web_private_key_path, "web_private_key_path为空"
        assert self.__web_alipay_public_key_path, "web_alipay_public_key_path为空"

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
        # 注意web支付类型，sign_type 不参与签名
        return self.create_trade(data, self.__web_private_key_path) + "&sign_type=RSA"

    def create_trade(self, data, private_key_path):
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

    def verify_notify(self, data, signature, alipay_public_key_path):
        # 排序后的字符串
        unsigned_items = self.__ordered_data(data)
        message = "&".join("{}={}".format(k, v) for k, v in unsigned_items)

        # 开始计算签名
        key = RSA.importKey(open(alipay_public_key_path).read())
        signer = PKCS1_v1_5.new(key)
        digest = SHA.new()
        digest.update(message.encode("utf8"))
        if signer.verify(digest, base64.decodestring(signature.encode("utf8"))):
            return True
        return False
