#!/usr/bin/env python
# coding: utf-8
"""
    test.py
    ~~~~~~~~~~

"""
import unittest
import json
import subprocess

from alipay import AliPay
from tests import helper
from tests.compat import mock

valid_response = json.dumps({
    u"alipay_trade_refund_response": {
        "code": "10000"
    }
}).encode("utf-8")

invalid_response = json.dumps({
    u"alipay_trade_refund_response": {
        "code": "20001",
        "sub_msg": "错误的消息"
    }
}).encode("utf-8")


create_face_to_faapp_orderce_trade_response = json.dumps({
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
}).encode("utf-8")

query_face_to_faapp_orderce_trade_response = json.dumps({
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
}).encode("utf-8")

cancel_face_to_faapp_orderce_trade_response = json.dumps({
   "alipay_trade_cancel_response": {
       "msg": "Success",
       "out_trade_no": "out_trade_no15",
       "code": "10000",
       "retry_flag": "N"
     }
}).encode("utf-8")

precreate_face_to_faapp_orderce_trade_response = json.dumps({
     "alipay_trade_precreate_response": {
       "msg": "Success",
       "out_trade_no": "out_trade_no17",
       "code": "10000",
       "qr_code": "https://qr.alipay.com/bax03431ljhokirwl38f00a7"
     },
     "sign": ""
   }
).encode("utf-8")


class AliPayTestCase(unittest.TestCase):

    def setUp(self):
        super(AliPayTestCase, self).setUp()
        self.__ali_private_key_path, self.__ali_public_key_path = helper.get_ali_certs()
        self.__app_private_key_path, self.__app_public_key_path = helper.get_app_certs()
        self.__web_private_key_path, self.__web_public_key_path = helper.get_web_certs()

    def get_app_client(self, sign_type):
        return AliPay(
            appid="appid",
            app_notify_url="http://example.com/app_notify_url",
            app_private_key_path=self.__app_private_key_path,
            app_alipay_public_key_path=self.__app_public_key_path,
            sign_type=sign_type
        )

    def get_web_client(self, sign_type):
        return AliPay(
            partner="partner",
            web_notify_url="https://example.com/web_notify_url",
            web_private_key_path=self.__web_private_key_path,
            web_alipay_public_key_path=self.__web_public_key_path,
            sign_type=sign_type
        )

    @mock.patch.object(AliPay, "_refund")
    def test_refund_wap_order(self, mock_refund):
        """
        wap退款功能测试，调用了refund函数
        """
        alipay = self.get_app_client("RSA")
        data = {
            "out_trade_no": "test_ouit_trade_no",
            "refund_amount": 0.01
        }
        alipay.refund_wap_order(**data)
        mock_refund.assert_called_once_with(
            alipay.appid,
            self.__app_private_key_path,
            **data
        )

    @mock.patch.object(AliPay, "_refund")
    def test_refund_app_order(self, mock_refund):
        """
        app退款功能测试，调用了refund函数
        """
        alipay = self.get_app_client("RSA")
        data = {
            "out_trade_no": "test_ouit_trade_no",
            "refund_amount": 0.01
        }
        alipay.refund_app_order(**data)
        mock_refund.assert_called_once_with(
            alipay.appid,
            self.__app_private_key_path,
            **data
        )

    @mock.patch.object(AliPay, "_refund")
    def test_refund_web_order(self, mock_refund):
        """
        web退款功能测试，调用了refund函数
        """
        alipay = self.get_web_client("RSA")
        data = {
            "out_trade_no": "test_ouit_trade_no",
            "refund_amount": 0.01
        }
        alipay.refund_web_order(**data)
        mock_refund.assert_called_once_with(
            alipay.partner,
            self.__web_private_key_path,
            **data
        )

    @mock.patch("alipay.urlopen")
    def test_refund_1(self, mock_urlopen):
        """ 调用之后向支付宝服务器发送了申请,程序能够处理中文
        """
        # 配置urlopen返回值
        response = mock.Mock()
        response.read.return_value = valid_response
        mock_urlopen.return_value = response

        alipay = self.get_app_client("RSA")
        data = {
            "out_trade_no": "test_ouit_trade_no",
            "refund_amount": 0.01,
            "refund_reason": "中文测试"
        }

        alipay.refund_app_order(**data)
        self.assertTrue(mock_urlopen.called)

    def test_sign_data_with_private_key_sha1(self):
        """openssl 以及aliapy分别对数据进行签名，得到同样的结果
        """
        alipay = self.get_web_client("RSA")
        result1 = alipay._sign("hello\n", self.__web_private_key_path)
        result2 = subprocess.check_output(
            "echo hello | openssl sha -sha1 -sign {} | openssl base64".format(
                self.__web_private_key_path
            ), shell=True).decode("utf-8")
        result2 = result2.replace("\n", "")
        self.assertEqual(result1, result2)

    def test_sign_data_with_private_key_sha256(self):
        """openssl 以及aliapy分别对数据进行签名，得到同样的结果
        """
        alipay = self.get_web_client("RSA2")
        result1 = alipay._sign("hello\n", self.__web_private_key_path)
        result2 = subprocess.check_output(
            "echo hello | openssl sha -sha256 -sign {} | openssl base64".format(
                self.__web_private_key_path
            ), shell=True).decode("utf-8")
        result2 = result2.replace("\n", "")
        self.assertEqual(result1, result2)

    def test_verify_sha1(self):
        alipay = self.get_web_client("RSA")
        raw_content = "hello\n"
        signature = alipay._sign(raw_content, self.__web_private_key_path)

        # 签名验证成功
        self.assertTrue(alipay._verify(raw_content, signature, self.__web_public_key_path))
        # 签名失败
        self.assertFalse(alipay._verify(raw_content[:-1], signature, self.__web_public_key_path))

    def test_verify_sha256(self):
        alipay = self.get_web_client("RSA2")
        raw_content = "hello\n"
        signature = alipay._sign(raw_content, self.__web_private_key_path)

        # 签名验证成功
        self.assertTrue(alipay._verify(raw_content, signature, self.__web_public_key_path))
        # 签名失败
        self.assertFalse(alipay._verify(raw_content[:-1], signature, self.__web_public_key_path))

    @mock.patch("alipay.urlopen")
    def test_create_face_to_face_trade(self, mock_urlopen):
        response = mock.Mock()
        response.read.return_value = create_face_to_faapp_orderce_trade_response
        mock_urlopen.return_value = response

        alipay = self.get_app_client("RSA")
        alipay.create_face_to_face_trade(
            "out_trade_no",
            "wave_code",
            "auth_code",
            "subject"
        )

        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_query_face_to_face_trade(self, mock_urlopen):
        response = mock.Mock()
        response.read.return_value = query_face_to_faapp_orderce_trade_response
        mock_urlopen.return_value = response

        alipay = self.get_app_client("RSA")
        alipay.query_face_to_face_trade(
            out_trade_no="out_trade_no",
        )
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_cancel_face_to_face_trade(self, mock_urlopen):
        response = mock.Mock()
        response.read.return_value = cancel_face_to_faapp_orderce_trade_response
        mock_urlopen.return_value = response

        alipay = self.get_app_client("RSA")
        alipay.cancel_face_to_face_trade(
            out_trade_no="out_trade_no",
        )
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_precreate_face_to_face_trade(self, mock_urlopen):
        response = mock.Mock()
        response.read.return_value = precreate_face_to_faapp_orderce_trade_response
        mock_urlopen.return_value = response

        alipay = self.get_app_client("RSA")
        alipay.precreate_face_to_face_trade(
            "out_trade_no", 12, "test subject"
        )
        self.assertTrue(mock_urlopen.called)
