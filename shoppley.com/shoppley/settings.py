# -*- coding: utf-8 -*-
# Django settings for social pinax project.

import os.path
import posixpath
import pinax

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
# TODO: the following line needs to be updated when running from your local machine
PYTHON_ROOT = os.path.abspath("/home/virtual/shoppley-env/lib/python2.7/site-packages")
#PYTHON_ROOT = os.path.abspath("/home/virtual/shoppley-env/lib/python2.6/site-packages")


GOOGLE_API_KEY = "ABQIAAAAtw1JH2yMfNAUgmPaNN9VkBTXP1I12cNpFhrTXkYpZhbq5Uv9LRT-1q0bgOQMK8ZOKjSUhquxiiodbA"


# tells Pinax to use the default theme
PINAX_THEME = "default"

# Following DEBUG flags get overridden in local_settings.py in dev and deployment
# SMS_DEBUG, DEBUG, TEMPLATE_DEBUG, SERVE_MEDIA

# set SMS_DEBUG=True when running django tests so that
# it doesn't send out unnecessary txt messages
SMS_DEBUG = True 

DEBUG = True 
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

INTERNAL_IPS = [
    "127.0.0.1",
]
DEBUG_TOOLBAR_PANELS = (
	'debug_toolbar.panels.version.VersionDebugPanel',
	'debug_toolbar.panels.timer.TimerDebugPanel',
	'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
	'debug_toolbar.panels.headers.HeaderDebugPanel',
	'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
	'debug_toolbar.panels.template.TemplateDebugPanel',
	'debug_toolbar.panels.sql.SQLDebugPanel',
	'debug_toolbar.panels.signals.SignalDebugPanel',
	'debug_toolbar.panels.logger.LoggingPanel',
)

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
	("Meng", "smengl@shoppley.com"),

]

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "dev.db",                       # Or path to database file if using sqlite3.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "US/Eastern"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

# SITE_ID = 1 # example.com default in django
SITE_ID = 2	# shoppley.com is inserted after you run python manage.py initialize

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/site_media/static/"

# Additional directories which hold static files
STATICFILES_DIRS = [
	os.path.join(PROJECT_ROOT, "media"),
	os.path.join(PINAX_ROOT, "media", PINAX_THEME),
	os.path.join(PYTHON_ROOT, "uni_form", "media"),
]



# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = "sdj=%zk!()r=^#pvvk!e2d#=wju!jugn6+w_j$yuudvz9(4s-i"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

MIDDLEWARE_CLASSES = [
	"django.middleware.common.CommonMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	#'django.middleware.csrf.CsrfResponseMiddleware',
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	#"django_openid.consumer.SessionConsumer",
	"django.contrib.messages.middleware.MessageMiddleware",
	"groups.middleware.GroupAwareMiddleware",
	"pinax.apps.account.middleware.LocaleMiddleware",
	"django.middleware.doc.XViewMiddleware",
	"pagination.middleware.PaginationMiddleware",
	"django_sorting.middleware.SortingMiddleware",
	#"pinax.middleware.security.HideSensistiveFieldsMiddleware",
	"debug_toolbar.middleware.DebugToolbarMiddleware",
]
ROOT_URLCONF = "shoppley.urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
]

TEMPLATE_CONTEXT_PROCESSORS = [
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.core.context_processors.request",
	"django.contrib.messages.context_processors.messages",
	"pinax.apps.account.context_processors.account",
	"notification.context_processors.notification",
	"announcements.context_processors.site_wide_announcements",
	"messages.context_processors.inbox",
	"friends_app.context_processors.invitations",
	"shoppley.context_processors.combined_inbox_count",
	"shoppley.context_processors.current_site",
]

COMBINED_INBOX_COUNT_SOURCES = [
	"messages.context_processors.inbox",
	"friends_app.context_processors.invitations",
	"notification.context_processors.notification",
]

INSTALLED_APPS = [
	# Django
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.sites",
	"django.contrib.messages",
	"django.contrib.humanize",
	"django.contrib.markup",
	"django.contrib.staticfiles",
	"django.contrib.gis",
	#"world",	
	"pinax.templatetags",
	
	# external
	"notification", # must be first
	"debug_toolbar",
	"mailer",
	"uni_form",
	"ajax_validation",
	"timezones",
	"emailconfirmation",
	"announcements",
	"pagination",
	"friends",
	"messages",
	"oembed",
	"threadedcomments",
	"swaps",
	"voting",
	"tagging",
	"groups",
	"bookmarks",
	"photologue",
	"avatar",
	"flag",
	"microblogging",
	"locations",
	"django_sorting",
	"django_markup",
	"tagging_ext",
	"djcelery",
	
	# Pinax
	"pinax.apps.account",
	"pinax.apps.signup_codes",
	"pinax.apps.analytics",
	"pinax.apps.profiles",
	"pinax.apps.blog",
	"pinax.apps.tribes",
	"pinax.apps.photos",
	"pinax.apps.topics",
	"pinax.apps.threadedcomments_extras",
	"pinax.apps.voting_extras",
	
	# project
	"about",
	'offer',
	'shoppleyuser',
	'autofixture',
	'buxfer',
	'mobile',
	'worldbank',
	'premium',
  'common',
]

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = "none"
MARKUP_CHOICES = [
    ("restructuredtext", u"reStructuredText"),
    ("textile", u"Textile"),
    ("markdown", u"Markdown"),
    ("creole", u"Creole"),
]

AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = False 
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = False

#AUTHENTICATION_BACKENDS = [
#    "pinax.apps.account.auth_backends.AuthenticationBackend",
#]

LOGIN_URL = "/account/login/" # @@@ any way this can be a url name?
LOGIN_REDIRECT_URLNAME = "what_next"


EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = "support@shoppley.com"
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/shoppley-messages'

# For Shoppleyuser
MAX_FORWARDS = 2

OFFER_CODE_LENGTH = 6
TRACKING_CODE_LENGTH= 6
RANDOM_PASSWORD_LENGTH = 6

INIT_CUSTOMER_BALANCE = 0
INIT_MERCHANT_BALANCE = 10000

ugettext = lambda s: s
LANGUAGES = [
    ("en", u"English"),
]

# URCHIN_ID = "ua-..."

YAHOO_MAPS_API_KEY = "..."

class NullStream(object):
    def write(*args, **kwargs):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    "cloak_email_addresses": True,
    "file_insertion_enabled": False,
    "raw_enabled": False,
    "warning_stream": NullStream(),
    "strip_comments": True,
}

# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

# Uncomment this line after signing up for a Yahoo Maps API key at the
# following URL: https://developer.yahoo.com/wsregapp/
# YAHOO_MAPS_API_KEY = ""

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": True,
}

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass

DEFAULT_OFFER_IMG_URL = STATIC_URL+"images/offers/offer-default.jpg"
DEFAULT_MERCHANT_BANNER_URL = STATIC_URL+"images/merchant/restaurant_banner.png"
CONTACT_EMAIL = "support@shoppley.com"

# set django-celery autoloader 

import djcelery
djcelery.setup_loader()

# set information to connect to rabbitmq (broker) 

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_VHOST = "shoppley_vhost"
BROKER_USER = "shoppley_rabbit"
BROKER_PASSWORD = "shoppley_rabbit"


# logging config starts here...
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

nullhandler = logger.addHandler(NullHandler())
LOG_DIR = os.path.join(PROJECT_ROOT, "log")
LOG_FILE = os.path.join(PROJECT_ROOT, "log", "django.log")
if not os.path.exists(LOG_DIR):
	try:
		os.mkdir(LOG_DIR)
	except OSError, e:
		print e
		os.mkdir(os.path.join(PROJECT_ROOT, "log"))
if not os.path.exists(LOG_FILE):
	fd = os.open(LOG_FILE, os.O_RDONLY|os.O_CREAT)
	os.close(fd)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'log_file':{
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': '16777216', # 16megabytes
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
	'offer.management.commands.check_sms':{
	   'handlers': ['log_file','mail_admins'],
	   'level': 'INFO',
	   'propagate': True,
	},
   	 'apps': {
            'handlers': ['log_file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
# end of logging config

