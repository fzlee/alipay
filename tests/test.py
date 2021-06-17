#!/usr/bin/env python
# coding: utf-8
"""
    test.py
    ~~~~~~~~~~
"""
import json
import subprocess
import unittest

from alipay import AliPay, DCAliPay, ISVAliPay
from alipay.exceptions import AliPayException, AliPayValidationError
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
        super().setUp()
        self._app_private_key_path, self._app_public_key_path = helper.get_app_certs()

    def get_client(self, sign_type):
        with open(self._app_private_key_path) as fp:
            app_private_key_string = fp.read()

        with open(self._app_public_key_path) as fp:
            app_public_key_string = fp.read()

        return AliPay(
            appid="appid",
            app_notify_url="http://example.com/app_notify_url",
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=app_public_key_string,
            sign_type=sign_type
        )
    
    def get_empty_notify_url_client(self, sign_type):
        with open(self._app_private_key_path) as fp:
            app_private_key_string = fp.read()

        with open(self._app_public_key_path) as fp:
            app_public_key_string = fp.read()

        return AliPay(
            appid="appid",
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=app_public_key_string,
            sign_type=sign_type
        )

    def _prepare_sync_response(self, alipay, response_type):
        """sign data with private key so we can validate with our public key later"""
        data = {
            "name": "Lily",
            "age": "12"
        }
        response = {
            response_type: data,
            "sign": alipay._sign(json.dumps(data))
        }
        print(response)
        return json.dumps(response).encode("utf-8")


class AliPaySignTestCase(AliPayTestCase):

    def test_sign_data_with_private_key_sha1(self):
        """openssl 以及aliapy分别对数据进行签名，得到同样的结果
        """
        alipay = self.get_client("RSA")
        result1 = alipay._sign("hello\n")
        result2 = subprocess.check_output(
            "echo hello | openssl dgst -sha1 -sign {} | openssl base64".format(
                self._app_private_key_path
            ), shell=True).decode("utf-8")
        result2 = result2.replace("\n", "")
        self.assertEqual(result1, result2)

    def test_sign_data_with_private_key_sha256(self):
        """openssl 以及aliapy分别对数据进行签名，得到同样的结果
        """
        alipay = self.get_client("RSA2")
        result1 = alipay._sign("hello\n")
        result2 = subprocess.check_output(
            "echo hello | openssl dgst -sha256 -sign {} | openssl base64".format(
                self._app_private_key_path
            ), shell=True).decode("utf-8")
        result2 = result2.replace("\n", "")
        self.assertEqual(result1, result2)

    def test_verify_sha1(self):
        alipay = self.get_client("RSA")
        raw_content = "hello\n"
        signature = alipay._sign(raw_content)

        # 签名验证成功
        self.assertTrue(alipay._verify(raw_content, signature))
        # 签名失败
        self.assertFalse(alipay._verify(raw_content[:-1], signature))

    def test_verify_sha256(self):
        alipay = self.get_client("RSA2")
        raw_content = "hello\n"
        signature = alipay._sign(raw_content)

        # 签名验证成功
        self.assertTrue(alipay._verify(raw_content, signature))
        # 签名失败
        self.assertFalse(alipay._verify(raw_content[:-1], signature))

    def test_empty_return_url(self):
        alipay = self.get_empty_notify_url_client(sign_type="RSA2")
        alipay.api_alipay_trade_page_pay(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject="test",
            return_url=""
        )
        alipay.api_alipay_trade_page_pay(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject="test",
        )

    def test_encodnig(self):
        """编码测试"""
        subject = "中文测试"

        alipay = self.get_client(sign_type="RSA2")
        alipay.api_alipay_trade_page_pay(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject=subject,
            return_url="http://baidu.com"
        )
        alipay.api_alipay_trade_wap_pay(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject=subject,
            return_url="http://baidu.com"
        )

        alipay = self.get_client(sign_type="RSA")
        alipay.api_alipay_trade_page_pay(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject=subject,
            return_url="http://baidu.com"
        )
        alipay.api_alipay_trade_app_pay(
            out_trade_no="out_trade_no",
            total_amount=100,
            subject=subject,
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
        alipay.verify(data, "ssss")

    def test_init_alipay_with_string(self):
        with open(self._app_private_key_path) as fp:
            private_string = fp.read()
        with open(self._app_public_key_path) as fp:
            public_string = fp.read()

        return AliPay(
            appid="appid",
            app_notify_url="http://example.com/app_notify_url",
            app_private_key_string=private_string,
            alipay_public_key_string=public_string,
        )


class AliPayAPItestCase(AliPayTestCase):
    def _prepare_precreate_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_precreate_response")

    def _prepare_query_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_query_response")

    def _prepare_cancel_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_cancel_response")

    def _prepare_create_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_pay_response")

    def _prepare_refund_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_refund_response")

    def _prepare_alipay_fund_trans_toaccount_transfer_respone(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_fund_trans_toaccount_transfer_response")

    def _prepare_alipay_fund_trans_order_query(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_fund_trans_order_query_response")

    def _prepare_alipay_trade_order_settle(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_order_settle_response")

    def _prepare_failed_trade_query_responsy(self, alipay):
        return json.dumps({
            "alipay_trade_query_response": {
                "sub_code": "isv.invalid-app-id",
                "code": "40002",
                "sub_msg": "无效的AppID参数",
                "msg": "Invalid Arguments"
            }
        }).encode("utf8")

    @mock.patch("alipay.urlopen")
    def test_alipay_trade_refund(self, mock_urlopen):
        """ 调用之后向支付宝服务器发送了申请,程序能够处理中文
        """
        alipay = self.get_client("RSA")
        # 配置urlopen返回值
        response = mock.Mock()
        response.read.return_value = self._prepare_refund_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        data = {
            "out_trade_no": "test_ouit_trade_no",
            "refund_amount": 0.01,
            "refund_reason": "中文测试"
        }

        alipay.api_alipay_trade_refund(**data)
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_alipay_trade_pay(self, mock_urlopen):
        alipay = self.get_client("RSA")

        response = mock.Mock()
        response.read.return_value = self._prepare_create_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_trade_pay(
            "out_trade_no",
            "wave_code",
            "auth_code",
            "subject"
        )

        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_handle_alipay_exception(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_failed_trade_query_responsy(alipay)
        mock_urlopen.return_value = response

        with self.assertRaises(AliPayException):
            alipay.api_alipay_trade_query(
                out_trade_no="out_trade_no",
            )
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_query(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_query_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_trade_query(
            out_trade_no="out_trade_no",
        )
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_alipay_trade_cancel(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_cancel_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_trade_cancel(
            out_trade_no="out_trade_no",
        )
        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_precreate_face_to_face_trade(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_precreate_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_trade_precreate(
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
            alipay.api_alipay_trade_precreate(
                "out_trade_no", 12, "test subject"
            )

    @mock.patch("alipay.urlopen")
    def test_alipay_fund_trans_toaccount_transfer(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = \
            self._prepare_alipay_fund_trans_toaccount_transfer_respone(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_fund_trans_toaccount_transfer(
            "out_biz_no",
            "ALIPAY_USERID",
            "alipay account",
            12.3
        )

        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_alipay_fund_trans_order_query(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_alipay_fund_trans_order_query(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_fund_trans_order_query(
            "out_biz_no",
        )

        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_alipay_trade_order_settle(self, mock_urlopen):
        alipay = self.get_client("RSA2")
        response = mock.Mock()
        response.read.return_value = self._prepare_alipay_trade_order_settle(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_trade_order_settle(
            "out_biz_no", "trade_no", [{"parameters": "paramters"}]
        )

        self.assertTrue(mock_urlopen.called)


class DCAliPayTestCase(AliPayTestCase):

    def setUp(self):
        super(DCAliPayTestCase, self).setUp()
        (
            self._app_private_key_path,
            self._app_public_key_cert_path,
            self._alipay_public_key_cert_path,
            self._alipay_root_cert_path
        ) = helper.get_dc_certs()

    def get_client(self):
        with open(self._app_private_key_path) as fp:
            app_private_key_string = fp.read()
        with open(self._app_public_key_cert_path) as fp:
            app_public_key_cert_string = fp.read()
        with open(self._alipay_public_key_cert_path) as fp:
            alipay_public_key_cert_string = fp.read()
        with open(self._alipay_root_cert_path) as fp:
            alipay_root_cert_string = fp.read()

        # 强制篡改alipay公钥为自己的公钥， 方便后面伪造签名数据
        alipay_public_key_cert_string = app_public_key_cert_string

        return DCAliPay(
            appid="appid",
            app_notify_url="http://example.com/app_notify_url",
            app_private_key_string=app_private_key_string,
            app_public_key_cert_string=app_public_key_cert_string,
            alipay_public_key_cert_string=alipay_public_key_cert_string,
            alipay_root_cert_string=alipay_root_cert_string
        )

    def _prepare_create_face_to_face_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_trade_pay_response")

    def _prepare_alipay_fund_trans_uni_transfer_response(self, alipay):
        return self._prepare_sync_response(alipay, "alipay_fund_trans_uni_transfer_response")

    def test_sign_data_with_private_key_sha256(self):
        """openssl 以及aliapy分别对数据进行签名，得到同样的结果
        """
        alipay = self.get_client()
        result1 = alipay._sign("hello\n")
        result2 = subprocess.check_output(
            "echo hello | openssl dgst -sha256 -sign {} | openssl base64".format(
                self._app_private_key_path
            ), shell=True).decode("utf-8")
        result2 = result2.replace("\n", "")
        self.assertEqual(result1, result2)

    @mock.patch("alipay.urlopen")
    def test_alipay_trade_pay(self, mock_urlopen):
        alipay = self.get_client()

        response = mock.Mock()
        response.read.return_value = self._prepare_create_face_to_face_response(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_trade_pay(
            "out_trade_no",
            "wave_code",
            "auth_code",
            "subject"
        )

        self.assertTrue(mock_urlopen.called)

    @mock.patch("alipay.urlopen")
    def test_alipay_fund_trans_uni_transfer(self, mock_urlopen):
        alipay = self.get_client()
        response = mock.Mock()
        response.read.return_value = self._prepare_alipay_fund_trans_uni_transfer_response(alipay)
        mock_urlopen.return_value = response

        alipay.api_alipay_fund_trans_uni_transfer(
            "out_biz_no",
            "ALIPAY_LOGON_ID",
            "alipay account",
            8.88,
        )
        self.assertTrue(mock_urlopen.called)


class AliPayUtilTestCase(AliPayTestCase):

    def test_isv_alipay(self):
        """
        不报错就行
        """
        with open(self._app_private_key_path) as fp:
            app_private_key_string = fp.read()
        with open(self._app_public_key_path) as fp:
            app_public_key_string = fp.read()

        return ISVAliPay(
            appid="appid",
            app_notify_url="http://example.com/app_notify_url",
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=app_public_key_string,
            app_auth_code="test"
        )

    def test_verify_and_return_sync_response(self):
        """
        test for issue#69
        """
        alipay = self.get_client("RSA2")
        response_data = {
            "should_be_true": True
        }

        sign = alipay._sign(json.dumps(response_data))
        raw_string = """
        {
            "response": {"should_be_true": true},
            "response": {"should_be_true": false},
            "sign": "sign_data"
        }
        """

        raw_string = raw_string.replace("sign_data", sign)
        result = alipay._verify_and_return_sync_response(raw_string, "response")
        self.assertTrue(result["should_be_true"])

    def test_get_string_to_be_signed(self):
        alipay = self.get_client("RSA2")

        # 简单测试
        s = """{"response_type":{"key1":"name"}}"""
        expected = """{"key1":"name"}"""
        returned = alipay._get_string_to_be_signed(s, "response_type")
        self.assertEqual(expected, returned)
        # 嵌套测试
        s = """{"response_type":{"key1":{"key2": ""}}}"""
        expected = """{"key1":{"key2": ""}}"""
        returned = alipay._get_string_to_be_signed(s, "response_type")
        self.assertEqual(expected, returned)
        # 嵌套测试
        s = """{"response_type":{"key1":{"key2": {"key3": ""}}}}"""
        expected = """{"key1":{"key2": {"key3": ""}}}"""
        returned = alipay._get_string_to_be_signed(s, "response_type")
        self.assertEqual(expected, returned)
        # 不合法测试, 不报错就好
        s = """{"response_type":{"key1":{"key2": {{"""
        alipay._get_string_to_be_signed(s, "response_type")
        # 不合法测试, 不报错就好
        s = """{"response_type":"key1":"key2":"""
        alipay._get_string_to_be_signed(s, "response_type")
