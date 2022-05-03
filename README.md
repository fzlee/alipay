## python-alipay-sdk
[![PyPI version](https://badge.fury.io/py/python-alipay-sdk.svg)](https://badge.fury.io/py/python-alipay-sdk) [![codecov](https://codecov.io/gh/fzlee/alipay/branch/master/graph/badge.svg)](https://codecov.io/gh/fzlee/alipay) ![travis-ci](https://travis-ci.org/fzlee/alipay.svg?branch=master)
## [中文文档](./README.zh-hans.md)

## Unofficial AliPay Python SDK

Taking a look at [this guide](https://ifconfiger.com/articles/python-alipay-sdk) if you are interested at the details on signing your order requests.

## GUIDES
* [Preparation](./docs/preparation.md)
* [Initialization & validation](./docs/init.md)
* [API](./docs/apis.md)
* [Advanced API, introduced in 3.0](./docs/apis_new.md)

## What's new in 3.0 and how to migrate to 3.0
3.0 introduced two new functions: `client_api` and `server_appi` as a replacement of old-styled function based api .

3.0 keeps backward compatibility with 2.*, The only thing you should keep in mind is `Alipay.verify` won't pop `sign` from `data` automatically, you should handle it by yourself.  

## Test
```bash
python -m unittest discover
```

Or you may do test manually in this way, `debug=True` will direct your request to sandbox environment:
```python
alipay = AliPay(..., debug=True)
```
