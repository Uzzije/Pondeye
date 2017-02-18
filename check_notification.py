from notification_keys import TOKEN_FOR_NOTIFICATION
import urllib2
import urllib
CHECK_NOTIFICATION_URL = 'http://Uzzije.pythonanywhere.com/api/check-proj-and-mil-failed'


def run_notification():
	data = {'token':TOKEN_FOR_NOTIFICATION}
	data_encoded = urllib.urlencode(data)
	url = CHECK_NOTIFICATION_URL
	request = urllib2.Request(url, data_encoded)
	response = request.read()
	print response

run_notification()




