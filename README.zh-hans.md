## python-alipay-sdk
[![PyPI version](https://badge.fury.io/py/python-alipay-sdk.svg)](https://badge.fury.io/py/python-alipay-sdk) [![codecov](https://codecov.io/gh/fzlee/alipay/branch/master/graph/badge.svg)](https://codecov.io/gh/fzlee/alipay) ![travis-ci](https://travis-ci.org/fzlee/alipay.svg?branch=master)
## [English document](./README.md)

## 非官方支付宝 Python SDK

关于签名的详细实现细节参看[这篇教程](https://ifconfiger.com/articles/python-alipay-sdk)。如果你不希望深入了解技术实现的细节，你可以直接阅读下面的使用教程。

## 使用教程
* [准备](./docs/preparation.zh-hans.md)
* [初始化](./docs/init.zh-hans.md)
* [接口](./docs/apis.zh-hans.md)
* [3.0 新版接口](./docs/apis_new.zh-hans.md) 

## 3.0 的特性以及如何升级
3.0 提供了两个函数 `client_api` 和 `server_api`，他们可以处理大部分支付宝的接口。

3.0 保持向前的兼容性，唯一需要注意的是 `Alipay.verify` 函数不会将 `sign` 从 `data` 里面 `pop` 出来，你需要自己处理。

## 测试
```bash
python -m unittest discover
```

或者你可以传入 `debug=True`，进行手动测试：
```python
alipay = AliPay(..., debug=True)
```
