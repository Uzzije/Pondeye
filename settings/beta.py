from .base import *

DATABASES = {
	'default':{
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'Uzzije$default',
		'USER': 'Uzzije',
		'PASSWORD': 'DaKuimcv1',
		'HOST': 'Uzzije.mysql.pythonanywhere-services.com',
	}
}
CORS_ORIGIN_WHITELIST = (
	'http://localhost:8100'
)