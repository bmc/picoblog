# $Id$

"""
Base class for requests handled by this blog software.
"""

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import defs

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class BlogRequestHandler(webapp.RequestHandler):
    """
    Base class for all request handlers in this application. This class
    serves primarily to isolate common logic.
    """

    def get_template(self, template_name):
        """
        Return the full path of the template.
        
        :Parameters:
            template_name : str
                Simple name of the template
                
        :rtype: str
        :return: the full path to the template. Does *not* ensure that the
                 template exists.
        """
        return os.path.join(os.path.dirname(__file__), 
                            defs.TEMPLATE_SUBDIR,
                            template_name)

    def render_template(self, template_name, template_vars):
        """
        Render a template and write the output to ``self.response.out``.
        
        :Parameters:
            template_name : str
                Simple name of the template

            template_vars : dict
                Dictionary of variables to make available to the template.
                Can be empty.
        """
        template_path = self.get_template(template_name)
        return template.render(template_path, template_vars)
