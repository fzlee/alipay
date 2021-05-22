## Installation

```bash
pip install python-alipay-sdk --upgrade
# For python2, use: pip install python-alipay-sdk==1.1 (You should really think about Python3)
```

## Cert generation
```bash
# openssl
OpenSSL> genrsa -out app_private_key.pem 2048  # the private key file
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem # export public key
OpenSSL> exit
```

The public key we download from open.alipay.com is a string, which cannot be recognized by this lib directly, making sure it's surrounded with:
```
-----BEGIN PUBLIC KEY----- and -----END PUBLIC KEY-----
```

There is also an [example](https://github.com/fzlee/alipay/blob/master/tests/certs/ali/ali_public_key.pem) for your reference.

