## python-alipay-sdk
[![PyPI version](https://badge.fury.io/py/python-alipay-sdk.svg)](https://badge.fury.io/py/python-alipay-sdk) [![codecov](https://codecov.io/gh/fzlee/alipay/branch/master/graph/badge.svg)](https://codecov.io/gh/fzlee/alipay) ![travis-ci](https://travis-ci.org/fzlee/alipay.svg?branch=master)

##  支付宝Python SDK
支付宝没有提供Python SDK。生成预付订单需要使用SHA1withRSA签名，签名的生成比较麻烦容易出错。这里提供了一个简单的库，希望能够简化一些Python开发的流程。

自`1.0`开始，我们不再支持旧版的接口，比如[即时到帐](https://doc.open.alipay.com/doc2/detail?treeId=62&articleId=103566&docType=1)（你可以选择使用`0.6.*`版本的python-alipay-sdk或者使用[电脑网站支付](https://doc.open.alipay.com/doc2/detail.htm?treeId=270&articleId=105901&docType=1)接口）。

我们支持的所有支付方式，其签名类型必须为RSA或者RSA2。目前实现了以下功能：
* [电脑网站支付](#alipay.trade.page.pay)
* [手机网站支付](#alipay.trade.wap.pay)
* [APP支付](#alipay.trade.app.pay)
* [通知验证](#verification)
* [当面付](#alipay.trade.pay)
* [交易预创建](#alipay.trade.precreate)
* [交易查询](#alipay.trade.precreate)
* [交易取消](#alipay.trade.precreate)
* [退款](#alipay.trade.refund)
* [统一退款查询](#alipay.trade.fastpay.refund.query)
* [单笔转账到支付宝账户接口](#alipay.fund.trans.toaccount.transfer)
* [查询转账订单接口](#alipay.fund.trans.order.query)
* [ISV集成/生成app_auth_code](#alipay.open.auth.token.app)
* [ISV集成/查询授权产品](#alipay.open.auth.token.app.query)

关于签名的详细实现细节参看[这篇教程](https://ifconfiger.com/page/python-alipay-sdk). 如果你不希望深入了解技术实现的细节，你可以直接阅读下面的使用教程。

## 使用教程
#### 安装

```bash
# 从 1.3.0升级上来的用户, 请先卸载pycrypto:
pip uninstall pycrypto
# 安装python-alipay-sdk
pip install python-alipay-sdk --upgrade
```

#### 生成密钥文件
```bash
openssl
OpenSSL> genrsa -out app_private_key.pem   2048  # 私钥
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem # 导出公钥
OpenSSL> exit
```

在支付宝上下载的公钥是一个字符串，直接放入文本文件不能被我们识别，你需要在文本的首尾添加标记位(-----BEGIN PUBLIC KEY-----和-----END PUBLIC KEY-----)
证书的格式你可以参考[这里](https://github.com/fzlee/alipay/blob/master/tests/certs/ali/ali_public_key.pem)

#### 初始化
```python
    from alipay import AliPay, ISVAlipay

    alipay = AliPay(
      appid="",
      app_notify_url="",  # 默认回调url
      app_private_key_path="", 
      alipay_public_key_path=""  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
      sign_type="RSA" # RSA 或者 RSA2
      debug=False  # 默认False
    )


    # If you don't know what ISV is, then forget about what I mentioned below
    # either app_auth_code or app_auth_token should not be None
    isv_alipay = ISVAliPay(
      appid="",
      app_notify_url="",  # 默认回调url
      app_private_key_path="", 
      alipay_public_key_path=""  # alipay public key file path, do not put your public key file here
      sign_type="RSA" # RSA or RSA2
      debug=False  # False by default,
      app_auth_code=None, 
      app_auth_token=None
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

#### <a name="alipay.trade.page.pay"></a>电脑网站支付 [alipay.trade.page.pay](https://docs.open.alipay.com/270/105900/)

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
        return_url="https://example.com",
        notify_url="https://example.com/notify" # 可选, 不填则使用默认notify url
    )
```

#### <a name="alipay.trade.wap.pay"></a>手机网站支付 [alipay.trade.wap.pay](https://docs.open.alipay.com/60/104790)

```python
    # 手机网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no="20161112",
        total_amount="0.01",
        subject=subject,
        return_url="https://example.com",
        notify_url="https://example.com/notify" # 可选, 不填则使用默认notify url
    )
```

#### <a name="alipay.trade.app.pay"></a>App支付 [alipay.trade.app.pay](https://docs.open.alipay.com/204/105465)
```python
    # App支付，将order_string返回给app即可
    order_string = alipay.api_alipay_trade_app_pay(
        out_trade_no="20161112",
        total_amount="0.01",
        subject=subject,
        notify_url="https://example.com/notify" # 可选, 不填则使用默认notify url
    )
```

#### <a name="verification"></a>[通知验证](https://docs.open.alipay.com/58/103596/)
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

#### <a name="alipay.trade.pay"></a>当面付(条码支付) [alipay.trade.pay](https://docs.open.alipay.com/api_1/alipay.trade.pay)

以下是一个当面付的基本例子
```python
alipay = AliPay(appid="", ...)

result = alipay.api_alipay_trade_pay(
    out_trade_no="out_trade_no", 
    scene="bar_code/wave_code",
    auth_code="auth_code", 
    subject="subject",
    discountable_amount=10,
    total_amount=20,
    notify_url="https://example.com/notify" # 可选, 不填则使用默认notify url
    )

if  result["code"] == "10000":
    print("Order is paid")
```

#### <a name="alipay.trade.precreate"></a>交易预创建(扫码支付)  [alipay.trade.precreate](https://docs.open.alipay.com/194/105203/)
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

#### <a name="alipay.trade.refund"></a>退款 [alipay.trade.refund](https://docs.open.alipay.com/api_1/alipay.trade.refund)

refund 需要传入的参数参见官方文档

```python
result = alipay.api_alipay_trade_refund(out_trade_no="xxx", refund_amount="xxx", ...)

if result["code"] == "10000":
    print("success")
```

#### <a name="alipay.trade.fastpay.refund.query"></a>统一退款查询[alipay.trade.fastpay.refund.query](https://docs.open.alipay.com/api_1/alipay.trade.fastpay.refund.query)

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

#### <a name="alipay.fund.trans.toaccount.transfer"></a>单笔转账到支付宝账户接口 [alipay.fund.trans.toaccount.transfer](https://docs.open.alipay.com/api_28/alipay.fund.trans.toaccount.transfer)
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

#### <a name="alipay.fund.trans.order.query"></a> 查询转账订单接口 [alipay.fund.trans.order.query](https://docs.open.alipay.com/api_28/alipay.fund.trans.order.query)

```python
   result = alipay.api_alipay_fund_trans_order_query(
        out_biz_no="20170626152216"
    )
    print(result)
```


## [ISV 集成](https://doc.open.alipay.com/doc2/detail?treeId=216&articleId=105193&docType=1)

在开始前，请务必阅读[官方文档](https://docs.open.alipay.com/common/105193)

#### <a name="alipay.open.auth.token.app"></a> 生成app_auth_code []()
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

#### <a name="alipay.open.auth.token.app.query"></a> 查询授权产品 []()
```
    response = alipay_open_auth_token_app_query()
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
* EveryIsNormal 
* varwey
* Macuilxochitl

## Changelog

#### 2017-12-04(version 1.5.1)
* bug fix for `ISVAlipay.build_body`.

#### 2017-11-20(version 1.5)
* `alipay.trade.fastpay.refund.query` 统一收单交易退款查询

#### 2017-11-14(version 1.4.1)
* 修复忘记将notify url 传入`api_alipay_trade_precreate`的bug.

#### 2017-10-20(version 1.4.0)
* 将加密库依赖更新到pycryptodome，旧版用户请卸载pycrypto后安装使用.

#### 2017-08-21(version 1.3.0)
`alipay.trade.wap.pay` `alipay_trade_app_pay` `alipay.trade.page.pay` `alipay.trade.pay`


#### 2017-08-07(version 1.2.0)
* 四个支付函数可以额外传入notify_url

#### 2017-08-07(version 1.2.0)
* ISV 授权等功能

#### 2017-06-25(version 1.1.0)
* `alipay.fund.trans.toaccount.transfer` 以及 `alipay.fund.trans.order.query`

#### 2017-05-28(version 1.0.1)
* `alipay.trade.page.pay`里面return_url没有被传入

### 2017-05-26 (version 1.0)
* 后台全部重构，对各种接口重命名。
* 使用新版的`电脑网站支付接口`，不再`支持即时到帐`接口
* 将key重文件读出后放到内存，避免每次签名都需要访问文件。
