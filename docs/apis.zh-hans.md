* [电脑网站支付](#alipay.trade.page.pay)
* [手机网站支付](#alipay.trade.wap.pay)
* [APP支付](#alipay.trade.app.pay)
* [小程序支付](#alipay.trade.create)
* [通知验证](#verification)
* [当面付](#alipay.trade.pay)
* [交易预创建](#alipay.trade.precreate)
* [交易查询](#alipay.trade.precreate)
* [交易取消](#alipay.trade.precreate)
* [退款](#alipay.trade.refund)
* [统一退款查询](#alipay.trade.fastpay.refund.query)
* [统一收单交易结算接口](#alipay.trade.order.settle)
* [统一收单交易关闭接口](#alipay.trade.close)
* [单笔转账到支付宝账户接口](#alipay.fund.trans.toaccount.transfer)
* [DC/单笔转账接口](#alipay.fund.trans.uni.transfer)
* [查询转账订单接口](#alipay.fund.trans.order.query)
* [ISV集成/生成app_auth_code](#alipay.open.auth.token.app)
* [ISV集成/查询授权产品](#alipay.open.auth.token.app.query)


#### <a name="alipay.trade.page.pay"></a>电脑网站支付 [alipay.trade.page.pay](https://docs.open.alipay.com/270/105900/)

```python
# 如果你是 Python2 用户（考虑考虑升级到 Python3 吧），请确保非 ascii 的字符串为 utf8 编码：
subject = u"测试订单".encode("utf8")
# 如果你是 Python3 的用户，使用默认的字符串即可
subject = "测试订单"

# 电脑网站支付，需要跳转到：https://openapi.alipay.com/gateway.do? + order_string
order_string = alipay.api_alipay_trade_page_pay(
    out_trade_no="20161112",
    total_amount=0.01,
    subject=subject,
    return_url="https://example.com",
    notify_url="https://example.com/notify" # 可选，不填则使用默认 notify url
)
```

#### <a name="alipay.trade.wap.pay"></a>手机网站支付 [alipay.trade.wap.pay](https://docs.open.alipay.com/60/104790)

```python
# 手机网站支付，需要跳转到：https://openapi.alipay.com/gateway.do? + order_string
order_string = alipay.api_alipay_trade_wap_pay(
    out_trade_no="20161112",
    total_amount=0.01,
    subject=subject,
    return_url="https://example.com",
    notify_url="https://example.com/notify" # 可选，不填则使用默认 notify url
)
```

#### <a name="alipay.trade.app.pay"></a>App支付 [alipay.trade.app.pay](https://docs.open.alipay.com/204/105465)
```python
# App 支付，将 order_string 返回给 app 即可
order_string = alipay.api_alipay_trade_app_pay(
    out_trade_no="20161112",
    total_amount=0.01,
    subject=subject,
    notify_url="https://example.com/notify" # 可选，不填则使用默认 notify url
)
```

#### <a name="alipay.trade.create"></a>小程序支付[alipay.trade.create](https://opendocs.alipay.com/mini/introduce/pay)
```python
# 小程序支付
alipay.api_alipay_trade_create(
    out_trade_no="20161112",
    total_amount=0.01,
    subject=subject,
    buyer_id="",
    notify_url="https://example.com/notify" # 可选
)
```


#### <a name="verification"></a>[通知验证](https://docs.open.alipay.com/58/103596/)
这里有一个简单的基于 flask 的验证：
```python
from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def hello_world():
    data = request.form.to_dict()
    # sign 不能参与签名验证
    signature = data.pop("sign")

    print(json.dumps(data))
    print(signature)

    # verify
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
        print("trade succeed")
```

Django 版的
```python
def hello_world(request):
    # for django users
    data = request.dict()
    # for rest_framework users
    data = request.data

    signature = data.pop("sign")

    # verification
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
        print("trade succeed")
    return 'Hello, World!'
```



一般而言，可以这样验证回调通知
```python
# 验证 alipay 的异步通知，data 来自支付宝回调 POST 给你的 data，字典格式。
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
    notify_url="https://example.com/notify" # 可选，不填则使用默认notify url
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

#### <a name="alipay.trade.order.settle"></a>统一收单交易结算接口[alipay.trade.order.settle](https://docs.open.alipay.com/api_1/alipay.trade.order.settle/)

```python
result = alipay.api_alipay_trade_order_settle(
    out_request_no,
    trade_no,
    royalty_parameters
)
```

#### <a name="alipay.trade.close"></a>[统一收单交易关闭接口](https://docs.open.alipay.com/api_1/alipay.trade.close)

```python
result = alipay.api_alipay_trade_close(
    trace_no="xxx",
    out_trade_no="xxx",
    operator_id="this is optional"
)

result = {
     "code": "10000",
     "msg": "Success",
     "trade_no": "2013112111001004500000675971",
     "out_trade_no": "YX_001"
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

#### <a name="alipay.fund.trans.uni.transfer"></a>单笔转账接口 [alipay.fund.trans.uni.transfer](https://opendocs.alipay.com/apis/api_28/alipay.fund.trans.uni.transfer)
```python
# Only support dc_client. Transfer money to alipay account
result = dc_alipay.api_alipay_fund_trans_uni_transfer(
    out_biz_no=datetime.now().strftime("%Y%m%d%H%M%S"),
    identity_type="ALIPAY_LOGON_ID/ALIPAY_LOGON_ID",
    identity="egdjny5218@sandbox.com",
    trans_amount=82.32,
    name="沙箱环境"
)
result = {'code': '10000', 'msg': 'Success', 'order_id': '', 'out_biz_no': '', 'status': 'SUCCESS'}
```

#### <a name="alipay.fund.trans.order.query"></a> 查询转账订单接口 [alipay.fund.trans.order.query](https://docs.open.alipay.com/api_28/alipay.fund.trans.order.query)

```python
result = alipay.api_alipay_fund_trans_order_query(
    out_biz_no="20170626152216"
)
print(result)
```


#### <a name="alipay.ebpp.invoice.token.batchquery"></a> 根据查询令牌获取发票要素列表 [alipay.ebpp.invoice.token.batchquery](https://opendocs.alipay.com/pre-apis/api_pre/alipay.ebpp.invoice.token.batchquery)

```python
result = alipay.api_alipay_ebpp_invoice_token_batchquery(
    invoice_token="123456"
)
print(result)
```

## [ISV 集成](https://doc.open.alipay.com/doc2/detail?treeId=216&articleId=105193&docType=1)

在开始前，请务必阅读[官方文档](https://docs.open.alipay.com/common/105193)

#### <a name="alipay.open.auth.token.app"></a> 生成app_auth_code []()
```python
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
```python
response = isv_alipay.alipay_open_auth_token_app_query()
```