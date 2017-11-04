# SAML 2.0 for Netbox

[TOC]

### Overview

This doc covers only the most basic setup of a SAML Service Provider (SP, e.g. netbox) and a basic example of Identity Provider (IDP, e.g. Okta, OneLogin, etc.) settings.  The config.py used for SAML configuration has been simplified and should work, given a few simple modifications to suit your environment.  However, SAML is a large and complicated subject and some IDPs may require specific settings.  Should this not work with the basic configuration, we encourage you to refer to the pysaml2 and djangosaml2 documentation for its much greater detail on SAML options and settings.

### Installation

SAML authentication support is provided via [djangosaml2](https://github.com/knaperek/djangosaml2/) and [pysaml2](http://pysaml2.readthedocs.io/en/latest/).

To set up basic SAML support for Netbox, begin by installing pysaml2, djangosaml2 and xmlsec1

```
# cd /path/to/netbox
# pip3 install -r requirements_saml.txt
```

Or manually install the dependencies:

```# pip3 install pysaml2 djangosaml2```

Then, install the xmlsec1 program.  The package proivding this program is different depending on your OS/distribution.

##### Ubuntu/Debian

``` # sudo apt-get install xmlsec1```

##### OSX+Homebrew

``` # brew install libxmlsec1```



### Configuration

Once the dependencies are installed, copy the sample config to the `config.py`.

```
# cd /path/to/netbox
# cp netbox/netbox/saml/config.example.py netbox/netbox/saml/config.py
```

At minimum, you must modify the "Basic Settings" at the top of this file to match your environment.  However,  the full pysaml2 configuration is available via the SAML_CONFIG dictionary.  Please refer to the djangosaml2 and pysaml2 docs for full detail on configuration options.

##### Basic Settings

```python
# Set to true to enable SAML login
SAML_ENABLED = False

# Set to true to require SAML login. Use with LOGIN_REQUIRED to require SAML login for all access.
SAML_REQUIRED = False

# The base URL of your Netbox installation.
NETBOX_BASE = "http://localhost:8080"

SAML_IDP_ENTITY_ID = 'http://idp.domain.com/metadata'     # Commonly the URL for the IDP metadata
SAML_IDP_SSO_SERVICE = 'https://idp.domain.com/sso/saml'  # The SSO URL for your IDP

# Don't change this unless you know what you're doing. Defaults to the directory this file is in.
SAML_DIR = path.dirname(path.abspath(__file__))

# Set this to the URL of the page where users should be redirected, upon logout
# Only relevant if SAML is enabled and login is required.
# Otherwise, users will be sent to the netbox root page.
SAML_ON_LOGOUT_URL = 'https://idp.domain.com/'
```



##### Recommended Additional Settings

In the SAML_CONFIG dictionary, it's reommended that you also configure the contact and organization information so your metadata is prettier, or at least more accurate.

```python
    # own metadata settings
    'contact_person': [
        {'given_name': 'Lorenzo',
         'sur_name': 'Gil',
         'company': 'Yaco Sistemas',
         'email_address': 'lgs@yaco.es',
         'contact_type': 'technical'},
        {'given_name': 'Angel',
         'sur_name': 'Fernandez',
         'company': 'Yaco Sistemas',
         'email_address': 'angel@yaco.es',
         'contact_type': 'administrative'},
    ],
    # you can set multilanguage information here
    'organization': {
        'name': [('Yaco Sistemas', 'es'), ('Yaco Systems', 'en')],
        'display_name': [('Yaco', 'es'), ('Yaco', 'en')],
        'url': [('http://www.yaco.es', 'es'), ('http://www.yaco.com', 'en')],
    },
```



##### Set Up Metadata

Once you have modified your `config.py`, you'll need to fetch your IDP's metadata and generate your own. Download your IDP metadata and copy it to `netbox/netbox/saml/idp.xml`. 

Next, you'll need to generate your metadata. Luckily, pysaml2 comes with a utility for this.

```shell
# cd /path/to/netbox
# cd netbox/netbox/saml
# make_metadata.py config.py > sp.xml
```



##### Set Up Certificates

SAML assertion signing works fine with a self-signed SSL certificate.  Alternately, you can also use custom, privately signed or commercial certificates.  In all cases, the paths to the certificate and key must be configured in `config.py`.  By default, the config expects both files to be in the same directory as itself:

```python
    # For assertion signing. This can be a self-signed pair.
    'key_file': path.join(SAML_DIR, 'key.pem'),  # private part
    'cert_file': path.join(SAML_DIR, 'cert.pem'),  # public part
```

If you have your own cert+key, simply copy them into the same directory as `config.py`, to `cert.pem` and `key.pem` respectively.  If you'd like to generate a self-signed certificate, you can do so as follows:

```
# cd /path/to/netbox
# cd netbox/netbox/saml
# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

Please note:  *This generates a self-signed cert that is valid for **one year**, and **without a passphrase**.



### IDP Configuration

The defaults as given were confiured against Okta.  Covering all the possible IDP settings is beyond the scope of this README, but we can offer the generic settings that work for Okta, and should be generally translatable to other IDPs

```shell
# IDP's commonly use the same URL for all three of these
Single Sign On URL: http://localhost:8080/saml2/acs/
Recipient URL: http://localhost:8080/saml2/acs/
Destination URL: http://localhost:8080/saml2/acs/

# This should be the SP entityID. If in doubt, use the URL to the SP metadata
Audience Restriction: http://localhost:8080/saml2/metadata/

# This is the path to which the IDP will redirect a client following auth.
# We experienced issues using the full URL, so instead set it to the relative
# URL, i.e. the relative path to the netbox root
Default Relay State: /

# Ensure the name ID format is set to "unspecified" unless you specifically need something else
Name ID Format: Unspecified

# These were defaults for Okta. YMMV
Response: Signed
Assertion Signature: Signed
Signature Algorithm: RSA_SHA256
Digest Algorithm: SHA256
Assertion Encryption: Unencrypted
SAML Single Logout: Disabled 
authnContextClassRef: PasswordProtectedTransport
Honor Force Authentication: Yes
SAML Issuer ID: http://www.okta.com/${org.externalKey}
```



### Usage

Once you have configured your SAML settings, generated metadata and certificates, you can adjust the authentication behavior of netbox with a combination of settings.

If you want netbox to be public, but also to support SAML and username+password auth:

```
netbox/netbox/configuration.py:
	LOGIN_REQUIRED = False
netbox/netbox/saml/config.py:
	SAML_ENABLED = True
	SAML_REQUIRED = False
```

If you would like to completely protect netbox behind SAML auth:

```
netbox/netbox/configuration.py:
	LOGIN_REQUIRED = True
netbox/netbox/saml/config.py:
	SAML_ENABLED = True
	SAML_REQUIRED = True
```

Lastly, perhaps obviously, if you'd like to enforce login but accept both SAML and username+password

```
netbox/netbox/configuration.py:
	LOGIN_REQUIRED = True
netbox/netbox/saml/config.py:
	SAML_ENABLED = True
	SAML_REQUIRED = False
```

