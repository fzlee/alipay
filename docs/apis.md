* [Pay via Web](#alipay.trade.page.pay)
* [Pay via WAP](#alipay.trade.wap.pay)
* [Pay via App](#alipay.trade.app.pay)
* [Pay via Mini Program](#alipay.trade.create)
* [Verification](#verification)
* [Face to face trade](#alipay.trade.pay)
* [Precreate trade](#alipay.trade.precreate)
* [Query trade](#alipay.trade.precreate)
* [Cancel trade](#alipay.trade.precreate)
* [Refund](#alipay.trade.refund)
* [Query refund result](#alipay.trade.fastpay.refund.query)
* [Order Settlement](#alipay.trade.order.settle)
* [Close Order](#alipay.trade.close)
* [Transfer money to alipay account](#alipay.fund.trans.toaccount.transfer)
* [DC transfer money to alipay account](#alipay.fund.trans.uni.transfer)
* [Query money transfer result](#alipay.fund.trans.order.query)
* [alipay.ebpp.invoice.token.batchquery](#alipay.ebpp.invoice.token.batchquery)
* [ISV integration/Get app_auth_code by app_auth_token](#alipay.open.auth.token.app)
* [ISV integration/Query authorized apps](#alipay.open.auth.token.app.query)



#### <a name="alipay.trade.page.pay"></a>[alipay.trade.page.pay](https://docs.open.alipay.com/270/105900/)

```python
# For Python 2 users(you should really think about Python 3), 
# making sure non-ascii strings are utf-8 encoded
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

#### <a name="alipay.trade.create"></a>[alipay.trade.create](https://opendocs.alipay.com/mini/introduce/pay)
```python
# Mini Program Pay
alipay.api_alipay_trade_create(
    out_trade_no="20161112",
    total_amount=0.01,
    subject=subject,
    buyer_id="",
    notify_url="https://example.com/notify" # this is optional
)
```

#### <a name="verification"></a>[Notification Validation](https://docs.open.alipay.com/58/103596/)
Once an order is paid, a POST request will be sent to tell you the information

Here is a simple example for flask web server:

```python
import json
from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def hello_world():
    data = request.form.to_dict()
    # sign must be popped out
    signature = data.pop("sign")

    print(json.dumps(data))
    print(signature)

    # verify
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
        print("trade succeed")
    return 'Hello, World!'
```

And also an example for Django
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

Here is a more general example for verification
```python
# gathering all parameters sent from alipay server, and put them into a dictionary called data
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

#### <a name="alipay.trade.precreate"></a>[alipay.trade.precreate/alipay.trade.cancel/alipay.trade.query](https://docs.open.alipay.com/194/105203/)
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

#### <a name="alipay.trade.fastpay.refund.query"></a>[alipay.trade.fastpay.refund.query](https://docs.open.alipay.com/api_1/alipay.trade.fastpay.refund.query)

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

#### <a name="alipay.trade.order.settle"></a>[alipay.trade.order.settle](https://docs.open.alipay.com/api_1/alipay.trade.order.settle/)

```python
result = alipay.api_alipay_trade_order_settle(
    out_request_no,
    trade_no,
    royalty_parameters
)
```

#### <a name="alipay.trade.close"></a>[alipay.trade.close](https://docs.open.alipay.com/api_1/alipay.trade.close)

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


#### <a name="alipay.fund.trans.toaccount.transfer"></a>[alipay.fund.trans.toaccount.transfer](https://docs.open.alipay.com/api_28/alipay.fund.trans.toaccount.transfer)
```python
# transfer money to alipay account
result = alipay.api_alipay_fund_trans_toaccount_transfer(
    datetime.now().strftime("%Y%m%d%H%M%S"),
    payee_type="ALIPAY_LOGONID/ALIPAY_USERID",
    payee_account="csqnji8117@sandbox.com",
    amount=3.12
)
result = {
    'code': '10000', 
    'msg': 'Success', 
    'order_id': '', 
    'out_biz_no': '', 
    'pay_date': '2017-06-26 14:36:25'
}
```

#### <a name="alipay.fund.trans.uni.transfer"></a>[alipay.fund.trans.uni.transfer](https://opendocs.alipay.com/apis/api_28/alipay.fund.trans.uni.transfer)
```python
# Only support dc_client. Transfer money to alipay account
result = dc_alipay.api_alipay_fund_trans_uni_transfer(
    out_biz_no=datetime.now().strftime("%Y%m%d%H%M%S"),
    identity_type="ALIPAY_LOGON_ID/ALIPAY_LOGON_ID",
    identity="egdjny5218@sandbox.com",
    trans_amount=82.32,
    name="sandbox env"
)
result = {'code': '10000', 'msg': 'Success', 'order_id': '', 'out_biz_no': '', 'status': 'SUCCESS'}
```

#### <a name="alipay.fund.trans.order.query"></a> [alipay.fund.trans.order.query](https://docs.open.alipay.com/api_28/alipay.fund.trans.order.query)
```python
result = alipay.api_alipay_fund_trans_order_query(
    out_biz_no="20170626152216"
)
print(result)
```

#### <a name="alipay.ebpp.invoice.token.batchquery"></a> [alipay.ebpp.invoice.token.batchquery](https://opendocs.alipay.com/pre-apis/api_pre/alipay.ebpp.invoice.token.batchquery)

```python
result = alipay.api_alipay_ebpp_invoice_token_batchquery(
    invoice_token="123456"
)
print(result)
```

## [ISV Integration](https://doc.open.alipay.com/doc2/detail?treeId=216&articleId=105193&docType=1)

Go through [the details](https://docs.open.alipay.com/common/105193) before you do anything, or it may pains.

#### alipay.open.auth.token.app
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

#### alipay.open.auth.token.app.query
```python
response = isv_alipay.alipay_open_auth_token_app_query()
```
