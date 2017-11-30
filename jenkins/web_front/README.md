Need to generate a dhparam file. This takes a while!
```bash
openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096
```

Use https://www.ssllabs.com/ssltest/ to test the ssl setup


Review the contents of the nginx-default-website for where the .crt and .keys are stored.


