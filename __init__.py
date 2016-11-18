#!/usr/bin/env python
# coding: utf-8
"""
    __init__.py
    ~~~~~~~~~~

"""
import sys
import json
import base64
from datetime import datetime

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA

if sys.version_info[0] == 3:
    from urllib.parse import quote_plus
else:
    from urllib import quote_plus


class AliPay():
    @property
    def appid(self):
        return self.__appid

    def __init__(self, appid, notify_url, private_key_path, alipay_public_key_path):
        self.__appid = appid
        self.__notify_url = notify_url
        self.__private_key_path = private_key_path
        self.__alipay_public_key_path = alipay_public_key_path

    def __ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据单独排序
        for key in complex_keys:
            data[key] = json.dumps(data[key], sort_keys=True).replace(" ", "")

        return sorted([(k, v) for k, v in data.items()])

    def sign_data_with_private_key(self, data):
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
        key = RSA.importKey(open(self.__private_key_path).read())
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA.new(unsigned_string.encode("utf8")))
        # base64 编码，转换为unicode表示并移除回车
        sign = base64.encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def create_trade(self, out_trade_no, total_amount, subject):
        now = datetime.now()
        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.app.pay",
            "charset": "utf-8",
            "sign_type": "RSA",
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.__notify_url,
            "biz_content": {
                "subject": subject,
                "out_trade_no": out_trade_no,
                "total_amount": total_amount,
                "product_code": "QUICK_MSECURITY_PAY"
            }
        }
        sign = self.sign_data_with_private_key(data)
        ordered_items = self.__ordered_data(data)
        quoted_string = "&".join("{}={}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def verify_notify(self, data, signature):
        # 排序后的字符串
        unsigned_items = self.__ordered_data(data)
        message = "&".join("{}={}".format(k, v) for k, v in unsigned_items)

        # 开始计算签名
        key = RSA.importKey(open(self.__alipay_public_key_path).read())
        signer = PKCS1_v1_5.new(key)
        digest = SHA.new()
        digest.update(message.encode("utf8"))
        if signer.verify(digest, base64.decodestring(signature.encode("utf8"))):
            return True
        return False
