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
from alipay.exceptions import AliPayValidationError
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


class AliPayTestCase(unittest.TestCase):

    def setUp(self):
        super(AliPayTestCase, self).setUp()
        self.__ali_private_key_path, self.__ali_public_key_path = helper.get_ali_certs()
        self.__app_private_key_path, self.__app_public_key_path = helper.get_app_certs()
        self.__web_private_key_path, self.__web_public_key_path = helper.get_web_certs()

    def _prepare_sync_response(self, alipay, response_type):
        """sign data with private key so we can validate with our public key later"""
        data = {
            "name": "Lily",
            "age": "12"
        }
        response = {
            response_type: data,
            "sign": alipay._sign(json.dumps(data), self.__app_private_key_path)
        }
        return json.dumps(response).encode("utf-8")

    def _prepare_precreate_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_precreate_response")

    def _prepare_query_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_query_response")

    def _prepare_cancel_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_cancel_response")

    def _prepare_create_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_pay_response")

    def get_client(self, sign_type):
        return AliPay(
            appid="appid",
            app_notify_url="http://example.com/app_notify_url",
            app_private_key_path=self.__app_private_key_path,
            app_alipay_public_key_path=self.__app_public_key_path,
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
        alipay = self.get_client("RSA")
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
        alipay = self.get_client("RSA")
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
        alipay = self.get_client("RSA")
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

        alipay = self.get_client("RSA")
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
        alipay = self.get_client("RSA")
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
        alipay = self.get_client("RSA2")
        result1 = alipay._sign("hello\n", self.__web_private_key_path)
        result2 = subprocess.check_output(
            "echo hello | openssl sha -sha256 -sign {} | openssl base64".format(
                self.__web_private_key_path
            ), shell=True).decode("utf-8")
        result2 = result2.replace("\n", "")
        self.assertEqual(result1, result2)

    def test_verify_sha1(self):
        alipay = self.get_client("RSA")
        raw_content = "hello\n"
        signature = alipay._sign(raw_content, self.__web_private_key_path)

        # 签名验证成功
        self.assertTrue(alipay._verify(raw_content, signature, self.__web_public_key_path))
        # 签名失败
        self.assertFalse(alipay._verify(raw_content[:-1], signature, self.__web_public_key_path))

    def test_verify_sha256(self):
        alipay = self.get_client("RSA2")
        raw_content = "hello\n"
        signature = alipay._sign(raw_content, self.__web_private_key_path)

        # 签名验证成功
        self.assertTrue(alipay._verify(raw_content, signature, self.__web_public_key_path))
        # 签名失败
        self.assertFalse(alipay._verify(raw_content[:-1], signature, self.__web_public_key_path))

    @mock.patch("alipay.urlopen")
    def test_create_face_to_face_trade(self, mock_urlopen):
        alipay = self.get_client("RSA")

        response = mock.Mock()
        response.read.return_value = self._prepare_create_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.create_face_to_face_trade(
            "out_trade_no",
            "wave_code",
            "auth_code",
            "subject"
        )

        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_query_face_to_face_trade(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_query_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.query_face_to_face_trade(
            out_trade_no="out_trade_no",
        )
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_cancel_face_to_face_trade(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_cancel_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.cancel_face_to_face_trade(
            out_trade_no="out_trade_no",
        )
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_precreate_face_to_face_trade(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_precreate_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.precreate_face_to_face_trade(
            "out_trade_no", 12, "test subject"
        )
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_precreate_face_to_face_trade_with_exception(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        return_value = self._prepare_precreate_face_to_face_response(alipay)
        # 让签名失效
        return_value = return_value.replace(b"name", b"name2")
        response.read.return_value = return_value
        mock_urlopen.return_value = response

        with self.assertRaises(AliPayValidationError):
            alipay.precreate_face_to_face_trade(
                "out_trade_no", 12, "test subject"
            )

    def test_encodnig(self):
        """编码测试"""
        alipay = self.get_client(sign_type="RSA2")
        alipay.create_web_trade(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject="中文测试",
            return_url="http://baidu.com"
        )
        alipay.create_app_trade(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject="中文测试",
            return_url="http://baidu.com"
        )

        alipay = self.get_client(sign_type="RSA")
        alipay.create_web_trade(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject="中文测试",
            return_url="http://baidu.com"
        )
        alipay.create_app_trade(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject="中文测试",
            return_url="http://baidu.com"
        )

    def test_encoding_verify(self):
        data = {
          "seller_email": "olfwxa9760@sandbox.com",
          "trade_no": "2017041121001004070200183979",
          "seller_id": "2088102179075543",
          "total_amount": "12.00",
          "buyer_id": "2088102169481075",
          "buyer_logon_id": "csq***@sandbox.com",
          "charset": "utf-8",
          "app_id": "2016101100660467",
          "auth_app_id": "2016101100660467",
          "gmt_create": "2017-04-11 14:55:44",
          "version": "1.0",
          "sign_type": "RSA2",
          "out_trade_no": "20170411145511",
          "notify_time": "2017-04-11 14:55:44",
          "trade_status": "WAIT_BUYER_PAY",
          "notify_id": "4e5a35340926d9e4405f4f7b75b5d45gji",
          "notify_type": "trade_status_sync",
          "subject": u"测试"
        }
        alipay = self.get_client(sign_type="RSA2")
        alipay.verify_wap_notify(data, "ssss")

    def test__get_string_to_be_signed(self):
        alipay = self.get_client("RSA2")

        # 简单测试
        s = """{"response_type":{"key1":"name"}}"""
        expected = """{"key1":"name"}"""
        returned = alipay._AliPay__get_string_to_be_signed(s, "response_type")
        self.assertEqual(expected, returned)
        # 嵌套测试
        s = """{"response_type":{"key1":{"key2": ""}}}"""
        expected = """{"key1":{"key2": ""}}"""
        returned = alipay._AliPay__get_string_to_be_signed(s, "response_type")
        self.assertEqual(expected, returned)
        # 嵌套测试
        s = """{"response_type":{"key1":{"key2": {"key3": ""}}}}"""
        expected = """{"key1":{"key2": {"key3": ""}}}"""
        returned = alipay._AliPay__get_string_to_be_signed(s, "response_type")
        self.assertEqual(expected, returned)
        # 不合法测试, 不报错就好
        s = """{"response_type":{"key1":{"key2": {{"""
        alipay._AliPay__get_string_to_be_signed(s, "response_type")
        # 不合法测试, 不报错就好
        s = """{"response_type":"key1":"key2":"""
        alipay._AliPay__get_string_to_be_signed(s, "response_type")

