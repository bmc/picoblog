# $Id$

"""
Handles pinging Technorati for the blog.
"""

__docformat__ = 'restructuredtext' # for Epydoc

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import sys
import xmlrpclib
import logging

from google.appengine.api import urlfetch

import defs

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

TECHNORATI_PING_RPC_URL = 'http://rpc.technorati.com/rpc/ping'
FAKE_TECHNORATI_PING_RPC_URL = 'http://localhost/~bmc/technorati-mock/'

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class TechnoratiPingError(Exception):
    
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return msg

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class GoogleXMLRPCTransport(object):
    """Handles an HTTP transaction to an XML-RPC server."""

    def __init__(self):
        pass

    def request(self, host, handler, request_body, verbose=0):
        """
        Send a complete request, and parse the response. See xmlrpclib.py.

        :Parameters:
            host : str
                target host
                
            handler : str
                RPC handler on server (i.e., path to handler)
                
            request_body : str
                XML-RPC request body
                
            verbose : bool/int
                debugging flag. Ignored by this implementation

        :rtype: dict
        :return: parsed response, as key/value pairs
        """

        # issue XML-RPC request

        result = None
        url = 'http://%s%s' % (host, handler)
        try:
            response = urlfetch.fetch(url,
                                      payload=request_body,
                                      method=urlfetch.POST,
                                      headers={'Content-Type': 'text/xml'})
        except:
            msg = 'Failed to fetch %s' % url
            raise xmlrpclib.ProtocolError(host + handler, 500, msg, {})
                                          
        if response.status_code != 200:
            logging.error('%s returned status code %s' % 
                          (url, response.status_code))
            raise xmlrpclib.ProtocolError(host + handler,
                                          response.status_code,
                                          "",
                                          response.headers)
        else:
            result = self.__parse_response(response.content)
        
        return result

    def __parse_response(self, response_body):
        p, u = xmlrpclib.getparser(use_datetime=self._use_datetime)
        p.feed(response_body)
        return u.close()

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

def ping_technorati():
    if defs.ON_GAE:
        url = TECHNORATI_PING_RPC_URL
    else:
        url = FAKE_TECHNORATI_PING_RPC_URL

    logging.debug('Pinging Technorati at: %s' % url)
    try:
        rpc_server = xmlrpclib.ServerProxy(url,
                                           transport=GoogleXMLRPCTransport())
    except:
        raise TechnoratiPingError("Can't ping Technorati: %s" %
                                  sys.exc_info()[1])
    
    try:
        result = rpc_server.weblogUpdates.ping(defs.BLOG_NAME,
                                               defs.CANONICAL_BLOG_URL)
        if result.get('flerror', False) == True:
            logging.error('Technorati ping error from server: %s' %
                          result.get('message', '(No message in RPC result)'))
        else:
            logging.debug('Technorati ping successful.')
    except:
        raise TechnoratiPingError("Can't ping Technorati: %s" %
                                  sys.exc_info()[1])
