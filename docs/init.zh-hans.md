## 初始化
```python
from alipay import AliPay, DCAliPay, ISVAliPay
from alipay.utils import AliPayConfig

app_private_key_string = open("/path/to/your/private/key.pem").read()
alipay_public_key_string = open("/path/to/alipay/public/key.pem").read()

app_private_key_string == """
    -----BEGIN RSA PRIVATE KEY-----
    base64 encoded content
    -----END RSA PRIVATE KEY-----
"""

alipay_public_key_string == """
    -----BEGIN PUBLIC KEY-----
    base64 encoded content
    -----END PUBLIC KEY-----
"""

alipay = AliPay(
    appid="",
    app_notify_url=None,  # 默认回调 url
    app_private_key_string=app_private_key_string,
    # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    alipay_public_key_string=alipay_public_key_string,
    sign_type="RSA",  # RSA 或者 RSA2
    debug=False,  # 默认 False
    verbose=False,  # 输出调试数据
    config=AliPayConfig(timeout=15)  # 可选，请求超时时间
)

dc_alipay = DCAliPay(
    appid="appid",
    app_notify_url="http://example.com/app_notify_url",
    app_private_key_string=app_private_key_string,
    app_public_key_cert_string=app_public_key_cert_string,
    alipay_public_key_cert_string=alipay_public_key_cert_string,
    alipay_root_cert_string=alipay_root_cert_string
)

# 如果您没有听说过 ISV， 那么以下部分不用看了
# app_auth_code 或 app_auth_token 二者需要填入一个
isv_alipay = ISVAliPay(
    appid="",
    app_notify_url=None,  # 默认回调 url
    app_private_key_srting="",
    # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    alipay_public_key_string="",
    sign_type="RSA",  # RSA or RSA2
    debug=False,  # False by default
    app_auth_code=None,
    app_auth_token=None
)
```

### AliPay, DCAliPay, ISVAliPay的区别
* AliPay: 使用应用公钥进行报文验签
* DCAliPay: 使用公钥证书进行验签
* ISVAliPay: 托管多个支付宝应用使用

[部分接口](https://opensupport.alipay.com/support/knowledge/20069/201602429395?ant_source=zsearch)必须使用DCAlipay
