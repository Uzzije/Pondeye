from .base import *
from secret_keys import *
DATABASES = {
	'default':{
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'Uzzije$mobile-data-base',
		'USER': 'Uzzije',
		'PASSWORD': DATABASE_PASSWORD,
		'HOST': 'Uzzije.mysql.pythonanywhere-services.com',
	}
}
CORS_ORIGIN_WHITELIST = (
	'http://localhost:8100'
)