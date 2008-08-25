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
        p, u = xmlrpclib.getparser(use_datetime=0)
        p.feed(response_body)
        return u.close()
