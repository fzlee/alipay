As of 3.0, most alipay apis could be implemented with two functions: `client_api` and `server_api`

* client api: sign requests, requests will be sent to Alipay via client(APP, browser etc.) for example:
  * alipay.trade.page.pay
  * alipay.trade.wap.pay
  * alipay.trade.app.pay
* server api: sign request parameters, and send to alipay immediately. for example:
  * alipay.trade.pay
  * alipay.trade.refund
  * alipay.trade.query


```python
# create order
alipay = Alipay(...)

alipay.client_api(
  "alipay.trade.page.pay",
  biz_content={
    "out_trade_no": "20161112",
    "total_amount": 0.01,
    "subject": "an order",
    "product_code": "FAST_INSTANT_TRADE_PAY"
  },
  return_url="https://example.com" 
)

# query order status
alipay.server_api(
  "alipay.trade.query",
  biz_content={
    "out_trade_no": "202101010000"
  }
)

# refund
alipay.server_api(
  "alipay.rade.refund",
  biz_content={
    "out_trade_no": "202101010000",
    "refund_amount": 12.34
  }
)
```
