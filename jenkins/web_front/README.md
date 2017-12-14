# web\_front

web\_front is a TLS terminating proxy server to the actual application. It should be where DNS records point to and holds any TLS certificates for signed https traffic. This allows jenkins upgrade-deployments to be smoother as it can simply ask this web\_front server to point to a new server once it has been verified to have successfully instantiated.

The code here is designed to do a once-off instantiation of a server.

_Note_: This is more for documentation reasons. The current servers for Resplat is not made via this method.

__Server Outline__:
 * Serves https traffic by default
 * Redirects http to https
 * Proxies one application
 * To restrict tracffic to application servers, you get a OpenStack security group "http\_only\_security\_group" to use.
 * Assumes __you__ will do additional things to secure traffic between web\_front server and proxied application
 * All operational matters are up to __you__ after instantiation


## Deployment ##

Uses openstack HEAT to deploy. Review the contents of [deploy_web_front.yaml](deploy_web_front.yaml) for what is deployed.

__Requirements__:
 * Openstack CLI
 * Ubuntu 16.04 image on Openstack cloud
 * TLS certificates (see the following sections for self-signed or signed options)

Use [OS_deploy_web_front.bash](OS_deploy_web_front.bash) to deploy the server. A HEAT environment file is used to provide parameters.
```bash
# Assumes you have Openstack CLI and your OpenStack rc profile sourced. 
# Launch stack named 'web_front', but of course change the name as you please
./OS_deploy_web_front.bash web_front environment.yaml
```
There are _two_ options you need to consider for your environment.yaml

### Option 1: Self-signed certificate example (default) ###

I've made the deployment script to deploy with a self-signed certificate to as a demo/example instance for testing purposes, not to be used for production.

Example environment.yaml: 
```yaml
parameters:
  # an ssh key pair you have on your cloud
  key_name: mykey
  # ubuntu 16.04
  image_id: e4d127a9-458e-42a6-8401-2221e7fdc581
  # m2.tiny
  instance_type: cba9ea52-8e90-468b-b8c2-777a94d81ed3
```

Once the orchestration is complete, point your browser to the IP address. You should see a directory listing of /var/www/html as presented by python SimpleHTTPServer module.

Review user script inside [deploy_web_front.yaml](deploy_web_front.yaml) to see how this was done.


### Option 2: Signed certficate ###

The default behaviour of the signed certificate option is to launch the instance __but wait for user to complete the final setup__. This is because the user should copy over the certificates obtained by their provider and do the final checks.

Example environment.yaml: 
```yaml
parameters:
  # an ssh key pair you have on your cloud
  key_name: mykey
  # ubuntu 16.04
  image_id: e4d127a9-458e-42a6-8401-2221e7fdc581
  # m2.tiny
  instance_type: cba9ea52-8e90-468b-b8c2-777a94d81ed3
  # The default dhparam_size is 1024 which makes it really fast to create.
  # 4096 is better but will take much longer to make!
  dhparam_size: 4096
  # No self-signed cert will be made here and nginx will initially be stopped.
  is_self_signed: False
```

The instance is created, but does not have the certificates and nginx is __off__.

What we need to do now is:
 - [ ] Generate a CSR on this server for making a TLS certificate with a provider
 - [ ] Get a domain name for this server
 - [ ] Get signed TLS certificate from a provider
 - [ ] Install the certificate on the server
 
Consult the internet on how to do this. The following is an example of how the current Resplat instance was created.


__Generate a CSR on new instance (example)__:
```bash
sudo openssl req -new -newkey rsa:2048 -keyout /etc/ssl/private/mykey.key -nodes -out mycsr.csr
Generating a 2048 bit RSA private key
...............+++
..........+++
writing new private key to 'mykey.key'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:AU
State or Province Name (full name) [Some-State]:Victoria
Locality Name (eg, city) []:Melbourne
Organization Name (eg, company) [Internet Widgits Pty Ltd]:UoM
Organizational Unit Name (eg, section) []:Resplat
Common Name (e.g. server FQDN or YOUR name) []:mydomain.edu.au
Email Address []:myemail@edu.au

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:supersecret7!  
An optional company name []:
```
Use appropriate filenames and parameters to your situation.
_Note_: You need to think about what your domain name for 'Common Name'. Make sure you can actually get that name before filing a request.

__Getting domain name and signed TLS certificate__:

For Resplat instance, this was obtained through a single ticket request to AgileOps including details of (sub)domain name and IP address of this web\_front server. 

__Install the certificate on the server__:

When your certificate provider reponds, you should receive:
 * A certficate file for your domain .crt
 * One or more certificate files of the trusted provider issuing the certificate
 
Nginx expects the ssl certificate to be __"bundled"__. 
```bash
# For example,
cat mydomain_edu_au.crt provider_intermediate.crt provider_root.crt > mydomain_edu_au-bundle.crt
```
Order of concatenation matters! Check support from the provider if this is not explained.

 * Copy all of these files to the web\_front server in /etc/ssl/certs/
 * Edit /etc/nginx/site-available/default (with sudo) and update the following lines
``` 
    ...
    ssl_certificate /etc/ssl/certs/mydomain_edu_au-bundle-bundle.crt;
    ssl_certificate_key /etc/ssl/private/mykey.key;
    ...
    ssl_trusted_certificate /etc/ssl/certs/provider_root.crt;
    ...
```


## Testing SSL installation ##

Use https://www.ssllabs.com/ssltest/ to test the ssl setup

## Changing proxied application ##

There is a script called [change\_proxy.sh](change_proxy.sh) in the home directory of the default user, designed to be involved remotely over ssh for switching applications in deployments.

Make sure you have your ssh key installed for the default user in order to invoke this.

```bash
# Example
ssh ubuntu@server_name ./change_proxy.sh (ip address)
```









