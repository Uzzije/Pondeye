from .base import *
#from secret_keys import *
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
if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
	DATABASES = {
		'default':{
			'ENGINE': 'django.db.backends.mysql',
			'NAME': 'Uzzije$mobile-data-base',
			'USER': 'Uzzije',
			'PASSWORD': "",
			'HOST': 'Uzzije.mysql.pythonanywhere-services.com',
		}
	}
STATIC_ROOT = os.path.join(BASE_DIR, "www", "static")
