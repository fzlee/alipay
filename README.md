## python-alipay-sdk
[![PyPI version](https://badge.fury.io/py/python-alipay-sdk.svg)](https://badge.fury.io/py/python-alipay-sdk) [![codecov](https://codecov.io/gh/fzlee/alipay/branch/master/graph/badge.svg)](https://codecov.io/gh/fzlee/alipay) ![travis-ci](https://travis-ci.org/fzlee/alipay.svg?branch=master)
## [中文文档](https://github.com/fzlee/alipay/blob/master/README.zh-hans.md)

##  AliPay Python SDK
I can't find any official python alipay sdks so far, and it really pains a lot dealing with those sign methods. Hoping this library could do some help :).

So far, the following functions are supported:
* [Pay via Web](#alipay.trade.page.pay)
* [Pay via WAP](#alipay.trade.wap.pay)
* [Pay via App](#alipay.trade.app.pay)
* [Verification](#verification)
* [Face to face trade](#alipay.trade.pay)
* [Precreate trade](#alipay.trade.precreate)
* [Query trade](#alipay.trade.precreate)
* [Cancel trade](#alipay.trade.precreate)
* [Refund](#alipay.trade.refund)
* [Query refund result](#alipay.trade.fastpay.refund.query)
* [Transfer money to alipay account](#alipay.fund.trans.toaccount.transfer)
* [Query money transfer result](#alipay.fund.trans.order.query)
* [ISV integration/Get app_auth_code by app_auth_token](#alipay.open.auth.token.app)
* [ISV integration/Query authorized apps](#alipay.open.auth.token.app.query)

Taking a look at [this guide](https://ifconfiger.com/page/python-alipay-sdk) if you are interested at the details on signing your order requests.
Or you may just follow this manual if not.

## GUIDE
#### Installation

```
# installation
pip install python-alipay-sdk --upgrade
```

#### cert generation
```bash
# openssl
OpenSSL> genrsa -out app_private_key.pem 2048  # the private key file
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem # export public key
OpenSSL> exit
```

The public key we download from open.alipay.com is a string, which cannot be recognied by this lib directly, making sure it's surrounded with `-----BEGIN PUBLIC KEY-----` and `-----END PUBLIC KEY-----`
There is also an [example](https://github.com/fzlee/alipay/blob/master/tests/certs/ali/ali_public_key.pem) for your reference

#### Intialization
```python
    from alipay import AliPay, ISVAliPay

    # Making sure your key file is adhered to standards.
    # you may find examples at tests/certs/ali/ali_private_key.pem
    app_private_key_string = open("/path/to/your/private/key.pem").read()
    alipay_public_key_string = open("/path/to/alipay/public/key.pem").read()

    app_private_key_string = """
        -----BEGIN RSA PRIVATE KEY-----
        base64 encoded content
        -----END RSA PRIVATE KEY-----
        """

    alipay_public_key_string = """
        -----BEGIN PUBLIC KEY-----
        base64 encoded content
        -----END PUBLIC KEY-----
    """
   
    alipay = AliPay(
      appid="",
      app_notify_url=None,  # the default notify path
      app_private_key_string=app_private_key_string, 
      alipay_public_key_string=alipay_public_key_string  # alipay public key, do not use your public key!
      sign_type="RSA" # RSA or RSA2
      debug=False  # False by default
    )

    
    # If you don't know what ISV is, then forget about what I mentioned below
    # either app_auth_code or app_auth_token should not be None
    isv_alipay = ISVAliPay(
      appid="",
      app_notify_url=None,  # the default notify path
      app_private_key_string="", 
      alipay_public_key_string=alipay_public_key_string  # alipay public key, do not use your public key!
      sign_type="RSA" # RSA or RSA2
      debug=False  # False by default,
      app_auth_code=None, 
      app_auth_token=None
    )
```


#### Naming convention
Given an alipay function, say `alipay.trade.page.pay`, we will defind a corresponding function `alipay.api_alipay_trade_page_pay()`
Generally we will do such a translation:

    function_name = "alipay_" + alipay_function_name.replace(".", "_")

according to alipay document, some paremeters in `biz_content` are optional and some are not. 
we defind functions in this way so that you can put those optional parameters in `kwargs`:
```
def api_alipay_xxx(self, out_trade, total_amount, **kwargs):
    ...
    biz_content.update(kwargs)
```

#### <a name="alipay.trade.page.pay"></a>[alipay.trade.page.pay](https://docs.open.alipay.com/270/105900/)

```python
    # For Python 2 users(you should really think about Python 3), making sure non-ascii strings are utf-8 encoded
    subject = u"测试订单".encode("utf8")
    # For Python 3 users, just use the default string
    subject = "测试订单"

    # Pay via Web，open this url in your browser: https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay    (
        out_trade_no="20161112",
        total_amount=0.01,
        subject=subject,
        return_url="https://example.com",
        notify_url="https://example.com/notify" # this is optional 
    )
```

#### <a name="alipay.trade.wap.pay"></a>[alipay.trade.wap.pay](https://docs.open.alipay.com/60/104790)

```python
    # Pay via WAP, open this url in your browser: https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no="20161112",
        total_amount=0.01,
        subject=subject,
        return_url="http://example.com",
        notify_url="https://example.com/notify" # this is optional 
    )
```

#### <a name="alipay.trade.app.pay"></a>[alipay.trade.app.pay](https://docs.open.alipay.com/204/105465)
```python
    # Pay via App，just pass order_string to your Android or iOS client
    order_string = alipay.api_alipay_trade_app_pay(
        out_trade_no="20161112",
        total_amount=0.01,
        subject=subject,
        notify_url="https://example.com/notify" # this is optional 
    )
```

#### <a name="verification"></a>[Notification Validation](https://docs.open.alipay.com/58/103596/)
Once an order is paid, you will get a POST request from alipay servers which informs you that the order is paid 

Here is a simple example for flask web server:

```python
import json
from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def hello_world():
    data = request.form.to_dict()
    print(json.dumps(data))

    # verify 
    success = alipay.verify(data)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
        print("trade succeed")
    return 'Hello, World!'

```

Here is a more general example for verification
```python
    # gathering all parameters sent from alipay server, and put them in a dictionary called data
    data = {
          "subject": "testing order",
          "gmt_payment": "2016-11-16 11:42:19",
          "charset": "utf-8",
          "seller_id": "xxxx",
          "trade_status": "TRADE_SUCCESS",
          "buyer_id": "xxxx",
          "auth_app_id": "xxxx",
          "buyer_pay_amount": "0.01",
          "version": "1.0",
          "gmt_create": "2016-11-16 11:42:18",
          "trade_no": "xxxx",
          "fund_bill_list": "[{\"amount\":\"0.01\",\"fundChannel\":\"ALIPAYACCOUNT\"}]",
          "app_id": "xxxx",
          "notify_time": "2016-11-16 11:42:19",
          "point_amount": "0.00",
          "total_amount": "0.01",
          "notify_type": "trade_status_sync",
          "out_trade_no": "xxxx",
          "buyer_logon_id": "xxxx",
          "notify_id": "xxxx",
          "seller_email": "xxxx",
          "receipt_amount": "0.01",
          "invoice_amount": "0.01",
          "sign": "xxx"
        }
    success = alipay.verify(data)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
        print("trade succeed")
```

#### <a name="alipay.trade.pay"></a>[alipay.trade.pay](https://docs.open.alipay.com/api_1/alipay.trade.pay)

```python
alipay = AliPay(appid="", ...)

result = alipay.api_alipay_trade_pay(
    out_trade_no="out_trade_no", 
    scene="bar_code/wave_code",
    auth_code="auth_code", 
    subject="subject",
    discountable_amount=10,
    total_amount=20,
    notify_url="https://example.com/notify" # this is optional 
)

if  result["code"] == "10000":
    print("Order is paid")
```

#### <a name="alipay.trade.precreate"></a>[alipay.trade.precreate](https://docs.open.alipay.com/194/105203/)
```python
alipay = AliPay(appid="", ...)

# create an order
alipay.api_alipay_trade_precreate    (
    subject="test subject",
    out_trade_no="out_trade_no",
    total_amount=100
)

# check order status
paid = False
for i in range(10):
    # check every 3s, and 10 times in all
    print("now sleep 3s")
    time.sleep(3)
    result = alipay.api_alipay_trade_query(out_trade_no="out_trade_no")
    if result.get("trade_status", "") == "TRADE_SUCCESS":
        paid = True
        break
    print("not paid...")

# order is not paid in 30s , cancel this order
if paid is False:
    alipay.api_alipay_trade_cancel(out_trade_no=out_trade_no)
```

#### <a name="alipay.trade.refund"></a>[alipay.trade.refund](https://docs.open.alipay.com/api_1/alipay.trade.refund)

If you want to know what parameters are accepted, take a look into the official document

```python
result = alipay.api_alipay_trade_refund(out_trade_no="xxx", refund_amount="xxx", ...)

if result["code"] == "10000":
    print("success")
```

#### <a name="alipay.trade.fastpay.refund.query"></a>Query refund result[alipay.trade.fastpay.refund.query](https://docs.open.alipay.com/api_1/alipay.trade.fastpay.refund.query)

```python
result = alipay.api_alipay_trade_fastpay_refund_query("20171120", out_trade_no="20171120")

result = {
    'code': '10000', 
    'msg': 'Success', 
    'out_request_no': '20171120', 
    'out_trade_no': '20171120', 
    'refund_amount': '20.00', 
    'total_amount': '20.00', 
    'trade_no': '2017112021001004070200297107'
}
```

#### <a name="alipay.fund.trans.toaccount.transfer"></a>[alipay.fund.trans.toaccount.transfer](https://docs.open.alipay.com/api_28/alipay.fund.trans.toaccount.transfer)
```python
    # transfer money to alipay account
    result = alipay.api_alipay_fund_trans_toaccount_transfer(
        datetime.now().strftime("%Y%m%d%H%M%S"),
        payee_type="ALIPAY_LOGONID/ALIPAY_USERID",
        payee_account="csqnji8117@sandbox.com",
        amount=3.12
    )
    result = {'code': '10000', 'msg': 'Success', 'order_id': '', 'out_biz_no': '', 'pay_date': '2017-06-26 14:36:25'}
```

#### <a name="alipay.fund.trans.order.query"></a> [alipay.fund.trans.order.query](https://docs.open.alipay.com/api_28/alipay.fund.trans.order.query)
```python
   result = alipay.api_alipay_fund_trans_order_query(
        out_biz_no="20170626152216"
    )
    print(result)
```

## [ISV Integration](https://doc.open.alipay.com/doc2/detail?treeId=216&articleId=105193&docType=1)

Go through [the details](https://docs.open.alipay.com/common/105193) before you do anything, or it may pains.

#### alipay.open.auth.token.app
```
    isv_alipay = ISVAliPay(
        ...
        app_auth_code="app_auth_code" 
    )

    response = isv_alipay.api_alipay_open_auth_token_app()
    response = {
      "code": "10000",
      "msg": "Success",
      "app_auth_token": "201708xxx",
      "app_refresh_token": "201708xxx",
      "auth_app_id": "appid",
      "expires_in": 31536000,
      "re_expires_in": 32140800,
      "user_id": "2088xxxxx
    }
```

#### alipay.open.auth.token.app.query
```
    response = alipay_open_auth_token_app_query()
```


## test
```
python -m unittest discover
```

Or you may do test manually in this way, `debug=True` will direct your request to sandbox environment:
```
alipay = AliPay(..., debug=True)
```

## Changelog

#### 2018-03-16(version 1.7)
* Do encryption/decryption with `pycryptodomex`，which has not conflict with Pycrypto (many thanks to fakepoet)

#### 2018-01-23(version 1.6)
* initialize Alipay instance with key string

#### 2017-12-04(version 1.5.1)
* bug fix for `ISVAlipay.build_body`.

#### 2017-11-20(version 1.5)
* `alipay.trade.fastpay.refund.query` Query refund result.

#### 2017-11-14(version 1.4.1)
* bug fix for `api_alipay_trade_precreate`, notify url is not included in request params.

#### 2017-10-20(version 1.4.0)
* change dependence from pycrypto to pycryptodome. for users upgraded from 1.3.0, uninstall pycrypto first

#### 2017-08-21(version 1.3.0)
* allow notify_url be overriden in hose 4 functions: `alipay.trade.wap.pay` `alipay_trade_app_pay` `alipay.trade.page.pay` `alipay.trade.pay`

#### 2017-08-07(version 1.2.0)
* ISV integration

#### 2017-06-25(version 1.1.0)
* `alipay.fund.trans.toaccount.transfer` and `alipay.fund.trans.order.query`

#### 2017-05-28(version 1.0.1)
* return url missing for `alipay.trade.page.pay`

#### 2017-05-26(version 1.0.0)
* code refactoring, all functions are renamed
* `alipay.trade.page.pay` is used instead of `create_direct_pay_by_user`
* load key into memory, local key file access is needed for the 1st time 
