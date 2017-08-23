from .base import *
DATABASES = {
	'default':{
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'Uzzije$mobile-data-base',
		'USER': 'Uzzije',
		'PASSWORD': "",
		'HOST': 'Uzzije.mysql.pythonanywhere-services.com',
	}
}
CORS_ORIGIN_WHITELIST = (
	'http://localhost:8100'
)
if os.environ.get('RDS_DB_NAME', False):
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
	from secret_keys import *
	DATABASES = {
		'default':{
			'ENGINE': 'django.db.backends.mysql',
			'NAME': 'Uzzije$mobile-data-base',
			'USER': 'Uzzije',
			'PASSWORD': "",
			'HOST': 'Uzzije.mysql.pythonanywhere-services.com',
		}
	}
	AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID_PASS
	AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY_PASS
DEFAULT_FILE_STORAGE = 's3utils.MediaS3BotoStorage'
STATICFILES_STORAGE = 's3utils.StaticS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'pondeye'
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_DIRECTORY = '/static/'
MEDIA_DIRECTORY = '/media/'
STATIC_URL = S3_URL + STATIC_DIRECTORY
MEDIA_URL = S3_URL + MEDIA_DIRECTORY

STATIC_ROOT = os.path.join(BASE_DIR, "www", "static")