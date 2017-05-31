## python-alipay-sdk
[![PyPI version](https://badge.fury.io/py/python-alipay-sdk.svg)](https://badge.fury.io/py/python-alipay-sdk) [![codecov](https://codecov.io/gh/fzlee/alipay/branch/master/graph/badge.svg)](https://codecov.io/gh/fzlee/alipay) ![travis-ci](https://travis-ci.org/fzlee/alipay.svg?branch=master)

##  支付宝Python SDK
支付宝没有提供Python SDK。生成预付订单需要使用SHA1withRSA签名，签名的生成比较麻烦容易出错。这里提供了一个简单的库，希望能够简化一些Python开发的流程。

自`1.0`开始，我们不再支持旧版的接口，比如[即时到帐](https://doc.open.alipay.com/doc2/detail?treeId=62&articleId=103566&docType=1)（你可以选择使用`0.6.*`版本的python-alipay-sdk或者使用[电脑网站支付](https://doc.open.alipay.com/doc2/detail.htm?treeId=270&articleId=105901&docType=1)接口）。

我们支持的所有支付方式，其签名类型必须为RSA或者RSA2。目前实现了以下功能：
* [电脑网站支付](https://doc.open.alipay.com/doc2/detail.htm?treeId=270&articleId=105901&docType=1)
* [APP支付 ](https://doc.open.alipay.com/docs/doc.htm?spm=a219a.7629140.0.0.A7oKRx&treeId=204&articleId=105051&docType=1)
* [手机网站支付](https://doc.open.alipay.com/doc2/detail.htm?treeId=203&articleId=105463&docType=1)
* [当面付](https://doc.open.alipay.com/doc2/detail?treeId=194&articleId=105072&docType=1)
* [交易查询](https://doc.open.alipay.com/doc2/apiDetail.htm?spm=a219a.7629065.0.0.PlTwKb&apiId=757&docType=4)
* [交易取消](https://doc.open.alipay.com/docs/api.htm?spm=a219a.7395905.0.0.qoLd9V&docType=4&apiId=866)
* [交易预创建](https://doc.open.alipay.com/docs/api.htm?spm=a219a.7395905.0.0.Vttrhx&docType=4&apiId=862)
* [退款](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=759)

关于签名的详细实现细节参看[这篇教程](https://ifconfiger.com/page/python-alipay-sdk). 如果你不希望深入了解技术实现的细节，你可以直接阅读下面的使用教程。

## 使用教程
#### 安装

```bash
pip install python-alipay-sdk --upgrade
```

#### 生成密钥文件
```bash
openssl
OpenSSL> genrsa -out app_private_key.pem   2048  # 私钥
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem # 导出公钥
OpenSSL> exit
```

#### 初始化
```python
    from alipay import AliPay

    alipay = AliPay(
      appid="",
      app_notify_url="", 
      app_private_key_path="", 
      alipay_public_key_path=""  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
      sign_type="RSA" # RSA 或者 RSA2
      debug=False  # 默认False
    )
```
#### 接口基本命名规则
对于一个支付宝的接口，比如`alipay.trade.page.pay`，则一般可以这么调用接口：`alipay.api_alipay_trade_page_pay()`.
也就是说，我们做了这么一个转换:

     内部函数名 =  alipay_ + 支付宝接口名.replace(".", "_")
     
支付宝对于请求的biz_content,里面有一些参数必选，有一些可选。对于必选的参数，他们一般被明确定义在函数的参数里面。对于可选参数，他们一般被放在kwargs里面,然后被添加到biz_content里面去。比如`alipay.trade.page.pay`可以这么调用:
```python
alipay.api_alipay_trade_page_pay(
    subject="测试订单", 
    out_trade_no="2017020101", 
    total_amount=100
)
```

也可以这么调用：
```python
alipay.api_alipay_trade_page_pay(
    subject="测试订单", 
    out_trade_no="2017020101", 
    total_amount=100,
    goods_type=0,  # 可选
    timeout_express="90m"  # 可选
    ...
)
```

#### 电脑网站支付 [alipay.trade.page.pay](https://doc.open.alipay.com/doc2/detail.htm?treeId=270&articleId=105901&docType=1)

```python
    # 如果你是Python 2用户（考虑考虑升级到Python 3吧），请确保非ascii的字符串为utf8编码：
    subject = u"测试订单".encode("utf8")
    # 如果你是 Python 3的用户，使用默认的字符串即可
    subject = "测试订单"

    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no="20161112",
        total_amount=0.01,
        subject=subject,
        return_url="https://example.com"
    )
```

#### 手机网站支付 [alipay.trade.wap.pay](https://doc.open.alipay.com/doc2/detail.htm?treeId=203&articleId=105463&docType=1)

```python
    # 手机网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.alipay_trade_wap_pay(
        out_trade_no="20161112",
        total_amount="0.01",
        subject=subject,
        return_url="https://example.com"
    )
```

#### App支付 [alipay.trade.app.pay](https://doc.open.alipay.com/docs/doc.htm?spm=a219a.7629140.0.0.SLVDO1&treeId=204&articleId=105465&docType=1)
```python
    # App支付，将order_string返回给app即可
    order_string = alipay.api_alipay_trade_app_pay(
        out_trade_no="20161112",
        total_amount="0.01",
        subject=subject
    )
```

#### 通知验证
这里有一个简单的基于flask的验证：
```python
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
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
        print("trade succeed")
```

一般而言，可以这样验证回调通知
```python
    # 验证alipay的异步通知，data来自支付宝回调POST 给你的data，字典格式.
    data = {
          "subject": "测试订单",
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

#### 退款 [alipay.trade.refund](https://doc.open.alipay.com/doc2/apiDetail.htm?spm=a219a.7629065.0.0.PlTwKb&apiId=759&docType=4)

refund 需要传入的参数参见[官方文档](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=759)的**请求参数**

```python
result = alipay.api_alipay_trade_refund(out_trade_no="xxx", refund_amount="xxx", ...)

if result["code"] == "10000":
    print("success")
```

#### 当面付（条码支付） [alipay.trade.pay](https://doc.open.alipay.com/doc2/apiDetail.htm?spm=a219a.7629065.0.0.PlTwKb&apiId=850&docType=4)

以下是一个当面付的基本例子
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

#### 交易预创建 （扫码支付） [alipay.trade.precreate](https://doc.open.alipay.com/doc2/apiDetail.htm?spm=a219a.7629065.0.0.PlTwKb&apiId=862&docType=4)
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

## 测试
```
python -m unittest discover
```

或者你可以传入debug=True, 进行手动测试
```python
alipay = AliPay(..., debug=True)
```

## 感谢（排名不分先后）
* John60676
* varwey

## Changelog
#### 2017-05-28(version 1.0.1)
* `alipay.trade.page.pay`里面return_url没有被传入

### 2017-05-26 (version 1.0)
* 后台全部重构，对各种接口重命名。
* 使用新版的`电脑网站支付接口`，不再`支持即使到帐`接口
* 将key重文件读出后放到内存，避免每次签名都需要访问文件。
