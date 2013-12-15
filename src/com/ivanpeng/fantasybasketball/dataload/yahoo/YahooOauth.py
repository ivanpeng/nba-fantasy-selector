'''
This module will be responsible for doing two-legged authentication with Yahoo. This will allow us to be connected to the
teams module, and the stats database without having to manually add in csv tables.
Created on 2013-12-05

@author: ivan
'''

from rauth import OAuth1Service
import urllib2

class YahooOAuthException(Exception): pass

class YahooOAuth():
    
    CONSUMER_KEY = 'dj0yJmk9M05qVzF5c3dOcE1NJmQ9WVdrOWEzQm9SRXBWTjJrbWNHbzlPRGd3T0RNMk5qSS0mcz1jb25zdW1lcnNlY3JldCZ4PWQx'
    CONSUMER_SECRET = '9c495f1584e5ef7ee667383be94170056fd86efc'
    
    name = 'yahoofantasybasketball'
    access_token_url='https://api.login.yahoo.com/oauth/v2/get_token'
    authorize_url='https://api.login.yahoo.com/oauth/v2/request_auth'
    request_token_url='https://api.login.yahoo.com/oauth/v2/get_request_token'
    base_url='https://api.login.yahoo.com/oauth/v2/'
    
    yahoo = OAuth1Service(consumer_key = CONSUMER_KEY,
                          consumer_secret = CONSUMER_SECRET, 
                          name = name,
                          request_token_url = request_token_url,
                          access_token_url = access_token_url, 
                          authorize_url = authorize_url,
                          base_url =  base_url)

    def __init__(self):
        try:
            request_token, request_token_secret = self.yahoo.get_request_token(data = {'oauth_callback': 'oob'})
            auth_url = self.yahoo.get_authorize_url(request_token)
            # TODO: can we hit with urllib2.urlopen?
            #urllib2.urlopen(auth_url)
            print "Visit this in your browser: " + auth_url
            pin = raw_input('Enter PIN from your browser: ' )
            # Enter pin
            self.session = self.yahoo.get_auth_session(request_token, request_token_secret, data={'oauth_verifier': pin})
        except:
            print "Error caught. Please check stack trace"
        
    def sanityCheck(self):
        r = self.session.get('http://fantasysports.yahooapis.com/fantasy/v2/game/nba')
        if r.text is None:
            raise YahooOAuthException
    
    # This simple function is used to take the input url and then append the signature signoffs, along with oauth tokens.
    def getFormattedURL(self, reqURL):
        return self.session.get(reqURL).request().url
        
        