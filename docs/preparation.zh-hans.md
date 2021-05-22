## 安装
```bash
# 安装 python-alipay-sdk
pip install python-alipay-sdk --upgrade
# 对于 python2，请安装 2.0 以下版本: pip install python-alipay-sdk==1.1
```

## 生成密钥文件
```bash
openssl
OpenSSL> genrsa -out app_private_key.pem   2048  # 私钥
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem # 导出公钥
OpenSSL> exit
```

在支付宝上下载的公钥是一个字符串，你需要在文本的首尾添加标记位：
```
-----BEGIN PUBLIC KEY----- 和 -----END PUBLIC KEY-----
```

才能正常使用，证书的格式你可以参考[这里](https://github.com/fzlee/alipay/blob/master/tests/certs/ali/ali_public_key.pem)。