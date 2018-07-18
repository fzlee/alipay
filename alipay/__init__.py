#!/usr/bin/env python
# coding: utf-8
"""
    __init__.py
    ~~~~~~~~~~

"""
import json
from datetime import datetime
from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA, SHA256
from Cryptodome.PublicKey import RSA

from .compat import quote_plus, urlopen, decodebytes, encodebytes, b
from .exceptions import AliPayException, AliPayValidationError


class BaseAliPay(object):
    @property
    def appid(self):
        return self._appid

    @property
    def sign_type(self):
        return self._sign_type

    @property
    def app_private_key(self):
        """
        签名用
        """
        return self._app_private_key

    @property
    def alipay_public_key(self):
        """
        验证签名用
        """
        return self._alipay_public_key

    def __init__(
        self,
        appid,
        app_notify_url,
        app_private_key_path=None,
        app_private_key_string=None,
        alipay_public_key_path=None,
        alipay_public_key_string=None,
        sign_type="RSA2",
        debug=False
    ):
        """
        初始化:
        alipay = AliPay(
          appid="",
          app_notify_url="http://example.com",
          app_private_key_path="",
          alipay_public_key_path="",
          sign_type="RSA2"
        )
        """
        self._appid = str(appid)
        self._app_notify_url = app_notify_url
        self._app_private_key_path = app_private_key_path
        self._app_private_key_string = app_private_key_string
        self._alipay_public_key_path = alipay_public_key_path
        self._alipay_public_key_string = alipay_public_key_string

        self._app_private_key = None
        self._alipay_public_key = None
        if sign_type not in ("RSA", "RSA2"):
            raise AliPayException(None, "Unsupported sign type {}".format(sign_type))
        self._sign_type = sign_type

        if debug is True:
            self._gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self._gateway = "https://openapi.alipay.com/gateway.do"

        # load key file immediately
        self._load_key()

    def _load_key(self):
        # load private key
        content = self._app_private_key_string
        if not content:
            with open(self._app_private_key_path) as fp:
                content = fp.read()
        self._app_private_key = RSA.importKey(content)

        # load public key
        content = self._alipay_public_key_string
        if not content:
            with open(self._alipay_public_key_path) as fp:
                content = fp.read()
        self._alipay_public_key = RSA.importKey(content)

    def _sign(self, unsigned_string):
        """
        通过如下方法调试签名
        方法1
            key = rsa.PrivateKey.load_pkcs1(open(self._app_private_key_path).read())
            sign = rsa.sign(unsigned_string.encode("utf8"), key, "SHA-1")
            # base64 编码，转换为unicode表示并移除回车
            sign = base64.encodebytes(sign).decode("utf8").replace("\n", "")
        方法2
            key = RSA.importKey(open(self._app_private_key_path).read())
            signer = PKCS1_v1_5.new(key)
            signature = signer.sign(SHA.new(unsigned_string.encode("utf8")))
            # base64 编码，转换为unicode表示并移除回车
            sign = base64.encodebytes(signature).decode("utf8").replace("\n", "")
        方法3
            echo "abc" | openssl sha1 -sign alipay.key | openssl base64

        """
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        if self._sign_type == "RSA":
            signature = signer.sign(SHA.new(b(unsigned_string)))
        else:
            signature = signer.sign(SHA256.new(b(unsigned_string)))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _ordered_data(self, data):
        complex_keys = [k for k, v in data.items() if isinstance(v, dict)]

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def build_body(
        self, method, biz_content, return_url=None, notify_url=None, append_auth_token=False
    ):
        data = {
            "app_id": self._appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": self._sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }
        if append_auth_token:
            data["app_auth_token"] = self.app_auth_token

        if return_url is not None:
            data["return_url"] = return_url

        if method in (
            "alipay.trade.app.pay", "alipay.trade.wap.pay", "alipay.trade.page.pay",
            "alipay.trade.pay", "alipay.trade.precreate"
        ) and (notify_url or self._app_notify_url):
            data["notify_url"] = notify_url or self._app_notify_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        ordered_items = self._ordered_data(data)
        unsigned_string = "&".join("{}={}".format(k, v) for k, v in ordered_items)
        sign = self._sign(unsigned_string)
        quoted_string = "&".join("{}={}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        if self._sign_type == "RSA":
            digest = SHA.new()
        else:
            digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
            if sign_type != self._sign_type:
                raise AliPayException(None, "Unknown sign type: {}".format(sign_type))
        # 排序后的字符串
        unsigned_items = self._ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)

    def api(self, api_name, **kwargs):
        """
        alipay.api("alipay.trade.page.pay", **kwargs) ==> alipay.api_alipay_trade_page_pay(**kwargs)
        """
        api_name = api_name.replace(".", "_")
        key = "api_" + api_name
        if hasattr(self, key):
            return getattr(self, key)
        raise AttributeError("Unknown attribute" + api_name)

    def api_alipay_trade_wap_pay(
        self, subject, out_trade_no, total_amount,
        return_url=None, notify_url=None, **kwargs
    ):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "QUICK_WAP_PAY"
        }
        biz_content.update(kwargs)
        data = self.build_body(
            "alipay.trade.wap.pay",
            biz_content,
            return_url=return_url,
            notify_url=notify_url
        )
        return self.sign_data(data)

    def api_alipay_trade_app_pay(
        self, subject, out_trade_no, total_amount, notify_url=None, **kwargs
    ):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "QUICK_MSECURITY_PAY"
        }
        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.app.pay", biz_content, notify_url=notify_url)
        return self.sign_data(data)

    def api_alipay_trade_page_pay(self, subject, out_trade_no, total_amount,
                                  return_url=None, notify_url=None, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY"
        }

        biz_content.update(kwargs)
        data = self.build_body(
            "alipay.trade.page.pay",
            biz_content,
            return_url=return_url,
            notify_url=notify_url
        )
        return self.sign_data(data)

    def api_alipay_trade_query(self, out_trade_no=None, trade_no=None):
        """
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
        assert (out_trade_no is not None) or (trade_no is not None),\
            "Both trade_no and out_trade_no are None"

        biz_content = {}
        if out_trade_no:
            biz_content["out_trade_no"] = out_trade_no
        if trade_no:
            biz_content["trade_no"] = trade_no
        data = self.build_body("alipay.trade.query", biz_content)

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(raw_string, "alipay_trade_query_response")

    def api_alipay_trade_pay(
        self, out_trade_no, scene, auth_code, subject, notify_url=None, **kwargs
    ):
        """
        eg:
            self.api_alipay_trade_pay(
                out_trade_no,
                "bar_code/wave_code",
                auth_code,
                subject,
                total_amount=12,
                discountable_amount=10
            )

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
        assert scene in ("bar_code", "wave_code"), 'scene not in ("bar_code", "wave_code")'

        biz_content = {
            "out_trade_no": out_trade_no,
            "scene": scene,
            "auth_code": auth_code,
            "subject": subject
        }
        biz_content.update(**kwargs)
        data = self.build_body("alipay.trade.pay", biz_content, notify_url=notify_url)

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(raw_string, "alipay_trade_pay_response")

    def api_alipay_trade_refund(self, refund_amount, out_trade_no=None, trade_no=None, **kwargs):
        biz_content = {
            "refund_amount": refund_amount
        }
        biz_content.update(**kwargs)
        if out_trade_no:
            biz_content["out_trade_no"] = out_trade_no
        if trade_no:
            biz_content["trade_no"] = trade_no

        data = self.build_body("alipay.trade.refund", biz_content)

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(raw_string, "alipay_trade_refund_response")

    def api_alipay_trade_cancel(self, out_trade_no=None, trade_no=None):
        """
        response = {
        "alipay_trade_cancel_response": {
            "msg": "Success",
            "out_trade_no": "out_trade_no15",
            "code": "10000",
            "retry_flag": "N"
          }
        }
        """

        assert (out_trade_no is not None) or (trade_no is not None),\
            "Both trade_no and out_trade_no are None"

        biz_content = {}
        if out_trade_no:
            biz_content["out_trade_no"] = out_trade_no
        if trade_no:
            biz_content["trade_no"] = trade_no

        data = self.build_body("alipay.trade.cancel", biz_content)

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(raw_string, "alipay_trade_cancel_response")

    def api_alipay_trade_precreate(self, subject, out_trade_no, total_amount, **kwargs):
        """
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
        biz_content = {
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "subject": subject
        }
        biz_content.update(**kwargs)
        data = self.build_body("alipay.trade.precreate", biz_content)

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(raw_string, "alipay_trade_precreate_response")

    def api_alipay_trade_fastpay_refund_query(
        self, out_request_no, trade_no=None, out_trade_no=None
    ):
        assert (out_trade_no is not None) or (trade_no is not None),\
            "Both trade_no and out_trade_no are None"

        biz_content = {"out_request_no": out_request_no}
        if trade_no:
            biz_content["trade_no"] = trade_no
        else:
            biz_content["out_trade_no"] = out_trade_no

        data = self.build_body("alipay.trade.fastpay.refund.query", biz_content)

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(
            raw_string, "alipay_trade_fastpay_refund_query_response"
        )

    def api_alipay_fund_trans_toaccount_transfer(
            self, out_biz_no, payee_type, payee_account, amount, **kwargs
    ):
        assert payee_type in ("ALIPAY_USERID", "ALIPAY_LOGONID"), "unknown payee type"
        biz_content = {
            "out_biz_no": out_biz_no,
            "payee_type": payee_type,
            "payee_account": payee_account,
            "amount": amount
        }
        biz_content.update(kwargs)
        data = self.build_body("alipay.fund.trans.toaccount.transfer", biz_content)

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(
            raw_string, "alipay_fund_trans_toaccount_transfer_response"
        )

    def api_alipay_fund_trans_order_query(self, out_biz_no=None, order_id=None):
        if out_biz_no is None and order_id is None:
            raise Exception("Both out_biz_no and order_id are None!")

        biz_content = {}
        if out_biz_no:
            biz_content["out_biz_no"] = out_biz_no
        if order_id:
            biz_content["order_id"] = order_id

        data = self.build_body("alipay.fund.trans.order.query", biz_content)

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(
            raw_string, "alipay_fund_trans_order_query_response"
        )

    def _verify_and_return_sync_response(self, raw_string, response_type):
        """
        return data if verification succeeded, else raise exception
        """

        response = json.loads(raw_string)
        result = response[response_type]
        sign = response["sign"]

        # locate string to be signed
        raw_string = self._get_string_to_be_signed(raw_string, response_type)

        if not self._verify(raw_string, sign):
            raise AliPayValidationError
        return result

    def _get_string_to_be_signed(self, raw_string, response_type):
        """
        https://doc.open.alipay.com/docs/doc.htm?docType=1&articleId=106120
        从同步返回的接口里面找到待签名的字符串
        """
        count, start = 0, raw_string.find("{", raw_string.find(response_type))
        # 从response_type之后的第一个｛的下一位开始匹配，
        # 如果是｛则count加1; 如果是｝而且count=0，就是待验签字符串的终点
        for i, c in enumerate(raw_string[start + 1 :], start + 1):
            if c == "{":
                count += 1
            elif c == "}":
                if count == 0:
                    end = i + 1
                    break
                count -= 1
        return raw_string[start:end]


class AliPay(BaseAliPay):
    pass


class ISVAliPay(BaseAliPay):

    def __init__(
        self,
        appid,
        app_notify_url,
        app_private_key_path=None,
        app_private_key_string=None,
        alipay_public_key_path=None,
        alipay_public_key_string=None,
        sign_type="RSA2",
        debug=False,
        app_auth_token=None,
        app_auth_code=None
    ):
        if not app_auth_token and not app_auth_code:
            raise Exception("Both app_auth_code and app_auth_token are None !!!")

        self._app_auth_token = app_auth_token
        self._app_auth_code = app_auth_code
        super(ISVAliPay, self).__init__(
            appid,
            app_notify_url,
            app_private_key_path=app_private_key_path,
            app_private_key_string=app_private_key_string,
            alipay_public_key_path=alipay_public_key_path,
            alipay_public_key_string=alipay_public_key_string,
            sign_type=sign_type,
            debug=debug
        )

    @property
    def app_auth_token(self):
        # 没有则换取token
        if not self._app_auth_token:
            result = self.api_alipay_open_auth_token_app(self._app_auth_code)
            self._app_auth_token = result.get("app_auth_token", None)

        if not self._app_auth_token:
            raise Exception("Get auth token by auth code failed: {}".format(self._app_auth_code))
        return self._app_auth_token

    def build_body(
        self, method, biz_content, return_url=None, notify_url=None, append_auth_token=True
    ):
        return super(ISVAliPay, self).build_body(
            method, biz_content, return_url, notify_url, append_auth_token
        )

    def api_alipay_open_auth_token_app(self, refresh_token=None):
        """
        response = {
          "code": "10000",
          "msg": "Success",
          "app_auth_token": "201708BB28623ce3d10f4f62875e9ef5cbeebX07",
          "app_refresh_token": "201708BB108a270d8bb6409890d16175a04a7X07",
          "auth_app_id": "appid",
          "expires_in": 31536000,
          "re_expires_in": 32140800,
          "user_id": "2088xxxxx
        }
        """

        if refresh_token:
            biz_content = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
        else:
            biz_content = {
                "grant_type": "authorization_code",
                "code": self._app_auth_code
            }
        data = self.build_body(
            "alipay.open.auth.token.app",
            biz_content,
            append_auth_token=False
        )

        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(
            raw_string, "alipay_open_auth_token_app_response"
        )

    def api_alipay_open_auth_token_app_query(self):
        biz_content = {
            "app_auth_token": self.app_auth_token
        }
        data = self.build_body(
            "alipay.open.auth.token.app.query",
            biz_content,
            append_auth_token=False
        )
        url = self._gateway + "?" + self.sign_data(data)
        raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        return self._verify_and_return_sync_response(
            raw_string, "alipay_open_auth_token_app_query_response"
        )
