## Initialization
```python
from alipay import AliPay, DCAliPay, ISVAliPay
from alipay.utils import AliPayConfig

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
    # alipay public key, do not use your own public key!
    alipay_public_key_string=alipay_public_key_string,
    sign_type="RSA2",  # RSA or RSA2
    debug=False,  # False by default
    verbose=False,  # useful for debugging
    config=AliPayConfig(timeout=15)  # optional, request timeout
)


dc_alipay = DCAliPay(
    appid="appid",
    app_notify_url="http://example.com/app_notify_url",
    app_private_key_string=app_private_key_string,
    app_public_key_cert_string=app_public_key_cert_string,
    alipay_public_key_cert_string=alipay_public_key_cert_string,
    alipay_root_cert_string=alipay_root_cert_string
)


# Forget about what I mentioned below if you don't know what ISV is
# either app_auth_code or app_auth_token should not be None
isv_alipay = ISVAliPay(
    appid="",
    app_notify_url=None,  # the default notify path
    app_private_key_string="",
    # alipay public key, do not use your own public key!
    alipay_public_key_string=alipay_public_key_string,
    sign_type="RSA",  # RSA or RSA2
    debug=False,  # False by default
    app_auth_code=None,
    app_auth_token=None
)
```


### Differences among AliPay, DCAliPay, and ISVAliPay
* AliPay: sign request with your private key, several alipay apis are not available
* DCAliPay: sign request with cert
* ISVAliPay: used when you need to host multiple alipay services


DCAlipay is a must for certain [Alipay APIs](https://opensupport.alipay.com/support/knowledge/20069/201602429395?ant_source=zsearch)



## <a name="verification"></a>[Notification Validation](https://docs.open.alipay.com/58/103596/)

**Notice: As of version 3.0, this library won't pop sign from data, you must do it by yourself!**

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
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        print("trade succeed")
    return 'Hello, World!'
```

And also an example for Django:
```python
def hello_world(request):
    # for django users
    data = request.dict()
    # for rest_framework users
    data = request.data

    # sign must be popped out
    signature = data.pop("sign")

    # verification
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
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

# sign must be popped out
signature = data.pop("sign")
success = alipay.verify(data, signature)
if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
    print("trade succeed")
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
    "user_id": "2088xxxxx",
}
```
