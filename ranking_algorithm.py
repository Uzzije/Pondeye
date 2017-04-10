from notification_keys import TOKEN_FOR_NOTIFICATION
import urllib2
import urllib
RANKING_STATUS_URL = 'http://Uzzije.pythonanywhere.com/api/rank-all-users'


def run_ranking_algorithm():
	data = {'token':TOKEN_FOR_NOTIFICATION}
	data_encoded = urllib.urlencode(data)
	url = RANKING_STATUS_URL
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}
	request = urllib2.Request(url, data_encoded, headers)
	response = urllib2.urlopen(request)
	print response.read()


run_ranking_algorithm()