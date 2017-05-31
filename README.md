## python-alipay-sdk
[![PyPI version](https://badge.fury.io/py/python-alipay-sdk.svg)](https://badge.fury.io/py/python-alipay-sdk) [![codecov](https://codecov.io/gh/fzlee/alipay/branch/master/graph/badge.svg)](https://codecov.io/gh/fzlee/alipay) ![travis-ci](https://travis-ci.org/fzlee/alipay.svg?branch=master)
## [中文文档](https://github.com/fzlee/alipay/blob/master/README.zh-hans.md)

##  AliPay Python SDK
I can't find any official python alipay sdks so far, and it really pains a lot dealing with those sign methods. Hoping this libarary could do some help :).

So far, the following functions are supported:
* [paid via Web](https://doc.open.alipay.com/doc2/detail.htm?treeId=270&articleId=105901&docType=1)
* [paid via App](https://doc.open.alipay.com/docs/doc.htm?spm=a219a.7629140.0.0.A7oKRx&treeId=204&articleId=105051&docType=1)
* [paid via WAP](https://doc.open.alipay.com/doc2/detail.htm?treeId=203&articleId=105463&docType=1)
* [face to face trade](https://doc.open.alipay.com/doc2/detail?treeId=194&articleId=105072&docType=1)
* [query trade](https://doc.open.alipay.com/doc2/apiDetail.htm?spm=a219a.7629065.0.0.PlTwKb&apiId=757&docType=4)
* [cancel trade](https://doc.open.alipay.com/docs/api.htm?spm=a219a.7395905.0.0.qoLd9V&docType=4&apiId=866)
* [precreate trade](https://doc.open.alipay.com/docs/api.htm?spm=a219a.7395905.0.0.Vttrhx&docType=4&apiId=862)
* [refund](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=759)

Taking a look at [this guide](https://ifconfiger.com/page/python-alipay-sdk) if you are interested at the details on signing your order requests.
Or you may just follow this manual if not.

## GUIDE
#### Installation

```bash
pip install python-alipay-sdk --upgrade
```

#### cert generation
```bash
openssl
OpenSSL> genrsa -out app_private_key.pem   2048  # the private key file
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem # export public key
OpenSSL> exit
```

#### Intialization
```python
    from alipay import AliPay

    alipay = AliPay(
      appid="",
      app_notify_url="", 
      app_private_key_path="", 
      alipay_public_key_path=""  # alipay public key file path, do not put your public key file here
      sign_type="RSA" # RSA or RSA2
      debug=False  # False by default
    )
```


#### Naming convention
Given a alipay function, say `alipay.trade.page.pay`, we will defind a corresponding function `alipay.api_alipay_trade_page_pay()`
Generally we will do such a translation:

    function_name = "alipay_" + alipay_function_name.replace(".", "_")

according to alipay document, some paremeters in `biz_content` are optional and some are not. 
we defind functions in this way so that you can put those optional parameters in `kwargs`:
```
def api_alipay_xxx(self, out_trade, total_amount, **kwargs):
    ...
    biz_content.update(kwargs)
```

#### [alipay.trade.page.pay](https://doc.open.alipay.com/doc2/detail.htm?treeId=270&articleId=105901&docType=1)

```python
    # if you are using Python 2(you should really think about Python 3), making sure non-ascii strings are utf-8 encoded
    subject = u"测试订单".encode("utf8")
    # if you are Python3 user, just use the default string
    subject = "测试订单"

    # paid via Web，open this url in your browser: https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay    (
        out_trade_no="20161112",
        total_amount=0.01,
        subject=subject,
        return_url="https://example.com"
    )
```

#### [alipay.trade.wap.pay](https://doc.open.alipay.com/doc2/detail.htm?treeId=203&articleId=105463&docType=1)

```python
    # paid via WAP, open this url in your browser: https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_app_pay(
        out_trade_no="20161112",
        total_amount="0.01",
        subject=subject,
        return_url="http://example.com"
    )
```

#### [alipay.trade.app.pay](https://doc.open.alipay.com/docs/doc.htm?spm=a219a.7629140.0.0.SLVDO1&treeId=204&articleId=105465&docType=1)
```python
    # paid via App，just order_string to your Android or iOS client
    order_string = alipay.api_alipay_trade_app_pay(
        out_trade_no="20161112",
        total_amount="0.01",
        subject=subject
    )
```

#### Notification Validation
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
    signature = data.pop("sign")

    print(json.dumps(data))
    print(signature)

    # verify 
    alipay.verify(data, signature)
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
    signature = data.pop("sign")
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
        print("trade succeed")
```

#### [alipay.trade.refund](https://doc.open.alipay.com/doc2/apiDetail.htm?spm=a219a.7629065.0.0.PlTwKb&apiId=759&docType=4)

If you want to know what parameters are accepted, take a look into the [official document](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=759), they are listed in **请求参数**

```python
result = alipay.api_alipay_trade_refund(out_trade_no="xxx", refund_amount="xxx", ...)

if result["code"] == "10000":
    print("success")
```

#### [alipay.trade.pay](https://doc.open.alipay.com/doc2/apiDetail.htm?spm=a219a.7629065.0.0.PlTwKb&apiId=850&docType=4)

```python
alipay = AliPay(appid="", ...)

result = alipay.api_alipay_trade_pay(
    out_trade_no="out_trade_no", 
    scene="bar_code/wave_code",
    auth_code="auth_code", 
    subject="subject",
    discountable_amount=10,
    total_amount=20
    )

if  result["code"] == "10000":
    print("Order is paid")
```

#### [alipay.trade.precreate](https://doc.open.alipay.com/doc2/apiDetail.htm?spm=a219a.7629065.0.0.PlTwKb&apiId=862&docType=4)
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

## test
```
python -m unittest discover
```

Or you may do test manually in this way, `debug=True` will direct your request to sandbox environment:
```
alipay = AliPay(..., debug=True)
```

## Thanks to
* John60676
* varwey

## Changelog
#### 2017-05-28(version 1.0.1)
* return url missing for `alipay.trade.page.pay`

#### 2017-05-26(version 1.0.0)
* code refactoring, all functions are renamed
* `alipay.trade.page.pay` is used instead of `create_direct_pay_by_user`
* load key into memory, local key file access is needed for the 1st time 
