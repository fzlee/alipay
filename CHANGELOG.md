#Mini Program Pay# Changelog

#### 2020-08-01(version2.1.0)
* alipay.trade.create


#### 2019-12-03(version 2.0.0)
* version 2.0.0 published (thanks to 00Kai0)
* removed support for python2
* [sign with cert instead of public key](https://docs.open.alipay.com/291/twngcd/)


#### 2019-03-05(version 1.10)
* `alipay.trade.close`(thanks to iv8)

#### 2019-01-07(version 1.9)
* potential security issue fix

#### 2018-08-23(version 1.8)
* alipay.trade.order.settle

#### 2018-03-16(version 1.7)
* Do encryption/decryption with `pycryptodomex`，which has no conflict with Pycrypto (many thanks to fakepoet)

#### 2018-01-23(version 1.6)
* initialize Alipay instance with key string

#### 2017-12-04(version 1.5.1)
* bug fix for `ISVAlipay.build_body`.

#### 2017-11-20(version 1.5)
* `alipay.trade.fastpay.refund.query` Query refund result.

#### 2017-11-14(version 1.4.1)
* bug fix for `api_alipay_trade_precreate`, notify url is not included in request params.

#### 2017-10-20(version 1.4.0)
* change dependence from pycrypto to pycryptodome. for users upgraded from 1.3.0, uninstall pycrypto first

#### 2017-08-21(version 1.3.0)
* allow notify_url be overriden in hose 4 functions: `alipay.trade.wap.pay` `alipay_trade_app_pay` `alipay.trade.page.pay` `alipay.trade.pay`

#### 2017-08-07(version 1.2.0)
* ISV integration

#### 2017-06-25(version 1.1.0)
* `alipay.fund.trans.toaccount.transfer` and `alipay.fund.trans.order.query`

#### 2017-05-28(version 1.0.1)
* return url missing for `alipay.trade.page.pay`

#### 2017-05-26(version 1.0.0)
* code refactoring, all functions are renamed
* `alipay.trade.page.pay` is used instead of `create_direct_pay_by_user`
* load key into memory, local key file access is needed for the 1st time
