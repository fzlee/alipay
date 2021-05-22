3.0 开始大部分支付宝的接口可以通过两个函数实现：`client_api` 和 `server_api`

* client api：对请求进行签名，但请求会由客户端（APP，浏览器）发送给支付宝，比如:
  * alipay.trade.page.pay
  * alipay.trade.wap.pay
  * alipay.trade.app.pay
* server api：对请求进行签名并发送给支付宝，并获取响应，比如：
  * alipay.trade.pay
  * alipay.trade.refund
  * alipay.trade.query


```python
# 创建订单
alipay = Alipay(...)

alipay.client_api(
  "alipay.trade.page.pay",
  biz_content={
    "out_trade_no": "20161112",
    "total_amount": 0.01,
    "subject": "an order"
  },
  return_url="https://example.com", # this is optional
)

# 查询订单状态
alipay.server_api(
  "alipay.trade.query",
  biz_content={
    "out_trade_no": "202101010000"
  }
)

# 退款
alipay.server_api(
  "alipay.rade.refund",
  biz_content={
    "out_trade_no": "202101010000",
    "refund_amount": 12.34
  }
)
```