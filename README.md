## python-alipay-sdk
[![codecov](https://codecov.io/gh/fzlee/alipay/branch/master/graph/badge.svg)](https://codecov.io/gh/fzlee/alipay)
## [中文文档](https://github.com/fzlee/alipay/blob/master/README.zh-hans.md)
## Changelog

### 2017-03-21(version 0.6)
* create/cancel/query face to face query

### 2017-01-17(version 0.5.1)
* Refund bug fix( many thanks to varwey)

### 2017-01-13(version 0.5)
* SHA256withRSA is the default sign method now, if you want to use SHA1withRSA，set `sign_type = "RSA"` while intializing alipay instance

### 2017-01-06(version 0.4)
* Refund functions
* Code for testing
* Fixed coding and decoding issues in Python 2 

##  Alipay Python SDK
I can't find any official python alipay sdks so far, and it really pains a lot dealing with those sign methods. Hoping this libarary could do some help :).

So far, the following functions are supported:
* [paid by Android/iOS](https://doc.open.alipay.com/docs/doc.htm?treeId=193&articleId=105051&docType=1)
* [paid by WAP](https://doc.open.alipay.com/docs/doc.htm?treeId=193&articleId=105288&docType=1)
* [paid by Web](https://doc.open.alipay.com/doc2/detail?treeId=62&articleId=103566&docType=1)
* [Refund](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=759)
* [create face to face trade](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=850)
* [query face to face trade](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=757)
* [cancel face to face trade](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=866)
* [precreate face to face trade](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=862)

Taking a look at [this guide](https://ifconfiger.com/page/python-alipay-sdk) if you are interested at the details on signing your order requests.
Or you may just follow this manual if you are not.

## GUIDE
#### Installation

```bash
pip install python-alipay-sdk
```

#### Intialization
```Python
    from alipay import AliPay
    
    # paid by WAP or iOS/Android
    alipay = AliPay(
      appid="",
      app_notify_url="", 
      app_private_key_path="", 
      app_alipay_public_key_path="",  # public key which belongs to alipay, this is used to validate messages sent from alipay server.
      sign_type="RSA" # RSA or  RSA2
    )
    
    # paid by Web
    alipay = AliPay(
      partner="",
      web_notify_url="", 
      web_private_key_path="", 
      web_alipay_public_key_path=""  # public key which belongs to alipay, this is used to validate messages sent from alipay server.
    )
    
    # Intialize alipay in this way if you want to handling all the paying methods mentioned,  
    alipay = AliPay(
      appid="",
      app_notify_url="", 
      app_private_key_path="",
      app_alipay_public_key_path="",
      partner="", 
      web_notify_url="",
      web_private_key_path="", 
      web_alipay_public_key_path="" 
    )
```
    
#### Creating order string
```Python
    # paid by App，just generating order_string and pass it to your mobile app
    order_string = alipay.create_app_trade(out_trade_no="20161112", total_amount=0.01, subject="testing order")
    # paid by WAP, open this url in your browser: https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.create_wap_trade(out_trade_no="20161112", total_amount=0.01, subject="testing order", return_url="https://example.com")
    # paid by Web，open this url in your browser: https://mapi.alipay.com/gateway.do? + order_string
    order_string = alipay.create_web_trade(out_trade_no="20161112", total_amount=0.01, subject="testing order", return_url="https://example.com")
```
#### Notification Validation
Once an order is paid, you will get a POST request from alipay servers which informs you that the order is paid 

```Python
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
    # Verification for App
    success = alipay.verify_app_notify(data, signature)
    # Verification for WAP
    success = alipay.verify_wap_notify(data, signature)
    # Verification for Web
    success = alipay.verify_web_notify(data, signature)
    if success and (data["trade_status"] == "TRADE_SUCCESS" or data["trade_status"] == "TRADE_FINISHED" ):
        print("trade succeed")
```

#### Refund

If you want to know what parameters are accepted, take a look into the [official document](https://doc.open.alipay.com/docs/api.htm?docType=4&apiId=759), they are listed in **请求参数**

```Python
# Example for refund
try:
    alipay.refund_web_order(out_trade_no="xxx", refund_amount="xxx", ...)
    alipay.refund_app_order(out_trade_no="xxx", refund_amount="xxx", ...)
    alipay.refund_wap_order(out_trade_no="xxx", refund_amount="xxx", ...)
except AliPayException as e:
    raise e
return True
```

#### create face to face trade

```Python
alipay = Alipay(appid="", ...)

result = alipay.create_face_to_face_trade(
    "out_trade_no", "bar_code/wave_code", "auth_code", "subject",
    discountable_amount=10,
    total_amount=20,
    # you may input more parameters here, refer to alipay official doc for details
    )

if  result["code"] == "10000":
    print("Order is paid")
```

#### create precreate/query/cancel face to face trade
```Python
alipay = Alipay(appid="", ...)

# create an order
result1 = alipay.precreate_face_to_face_trade(
    "out_trade_no", 100, "test subject"
    # you may input more parameters here, refer to alipay official doc for details
    )

if result1["code"] = "10000":
    print("Order is paid")
elif result1["code"] == "10003":
    print("Pending paid by user")
    for i in range(10):
    # check every 3s to see if the order is paid
        time.sleep(3)
        result2 = alipay.query_face_to_face_trade(out_trade_no=out_trade_no)
        if result2["code"] == "10000":
            print("Order is paid")
            break

    # order is not paid in 30s , cancel this order
    alipay.cancel_face_to_face_trade(out_trade_no=out_trade_no)
```

## test
```
python -m unittest discover
```

Or you may do test manually in this way, `debug=True` will direct your request to sandbox environment:
```
alipay = Alipay(..., debug=True)
```

## Thanks to
* varwey
