import saml2
import saml2.saml
from os import path

###
#
# See documentation for djangosaml2 and pysaml2 for the full set of options.
# Defaults here have been configured against a simple and fairly generic IDP
#
#   pysaml2: http://pysaml2.readthedocs.io/en/latest/
#   djangosaml2: https://github.com/knaperek/djangosaml2/
#
# For djangosaml2 to work properly, and determine the user from the SAML assertion, your
# IDP must send the username in the "uid" attribute OR SAML_USE_NAME_ID_AS_USERNAME must be True
# in settings.py. As an alternative, you can refer to the pysaml2 docs and configure any
# IDP attributes and attribute mappings that you like, though that is beyond the scope of a
# comment.
#
###

## Basic Settings

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

## End Basic Settings

# Full pysaml2 config
SAML_CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': '%s/saml2/metadata/' % NETBOX_BASE,

    # directory with attribute mapping
    'attribute_map_dir': path.join(SAML_DIR, 'attribute-maps'),

    # Necessary for attributes to work on non-SSL instances. YMMV.
    'allow_unknown_attributes': True,

    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp': {
            'name': 'Netbox',
            'name_id_format': saml2.saml.NAMEID_FORMAT_UNSPECIFIED,
            'endpoints': {
                # url and binding to the assertion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    ('%s/saml2/acs/' % NETBOX_BASE, saml2.BINDING_HTTP_REDIRECT),
                    ('%s/saml2/acs/' % NETBOX_BASE, saml2.BINDING_HTTP_POST),
                ],

                # url and binding to the single logout service view
                # do not change the binding or service name
                # 'single_logout_service': [
                #     ('%s/saml2/ls/' % NETBOX_BASE, saml2.BINDING_HTTP_REDIRECT),
                #     ('%s/saml2/ls/post' % NETBOX_BASE, saml2.BINDING_HTTP_POST),
                # ],
            },

            'allow_unsolicited': True,
            'authn_requests_signed': False,
            'logout_requests_signed': True,
            'want_assertions_signed': True,
            'want_response_signed': False,

            # attributes that this project need to identify a user
            # 'required_attributes': [''],

            # attributes that may be useful to have but not required
            # 'optional_attributes': ['eduPersonAffiliation'],

            # in this section the list of IdPs we talk to are defined
            'idp': {

                # the keys of this dictionary are entity ids
                SAML_IDP_ENTITY_ID: {
                    'single_sign_on_service': {
                        saml2.BINDING_HTTP_REDIRECT:
                            SAML_IDP_SSO_SERVICE,
                    },
                    # Left over from the upstream example
                    # 'single_logout_service': {
                    #     saml2.BINDING_HTTP_REDIRECT:
                    #         '%s/saml2/idp/SingleLogoutService.php' % SAML_IDP,
                    # },
                },
            },
        },
    },

    # where the remote metadata is stored
    'metadata': {
        'local': [path.join(SAML_DIR, 'idp.xml')],
    },

    # set to 1 to output debugging information
    'debug': 1,

    # For assertion signing. This can be a self-signed pair.
    'key_file': path.join(SAML_DIR, 'key.pem'),  # private part
    'cert_file': path.join(SAML_DIR, 'cert.pem'),  # public part

    # For encrypting assertions
    # 'encryption_keypairs': [{
    #     'key_file': path.join(SAML_DIR, 'my_encryption_key.key'),
    #     'cert_file': path.join(SAML_DIR, 'my_encryption_cert.pem'),
    # }],

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
    'valid_for': 24,  # how long is our metadata valid
}

# For support of make_metadata.py
CONFIG = SAML_CONFIG