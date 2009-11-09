import os
from webob import Response

from zope.interface import implements
from zope.component import queryUtility

from jinja2.loaders import FileSystemLoader
from jinja2 import Environment

from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.renderers import template_renderer_factory
from repoze.bfg.settings import get_settings

def renderer_factory(path, level=4):
    return template_renderer_factory(path, Jinja2TemplateRenderer, level=level)

class Jinja2TemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path):
        settings = get_settings()
        auto_reload = settings and settings['reload_templates']
        directory, filename = os.path.split(path)
        loader = FileSystemLoader(directory)
        environment = Environment(loader=loader, auto_reload=auto_reload)
        self.template = environment.get_template(filename)
 
    def implementation(self):
        return self.template
   
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.template.render(system)
        return result

def get_renderer(path):
    """ Return a callable ``ITemplateRenderer`` object representing a
    ``jinja2`` template at the package-relative path (may also
    be absolute). """
    return renderer_factory(path)
    

def get_template(path):
    """ Return a ``jinja2`` template object at the package-relative path
    (may also be absolute) """
    renderer = renderer_factory(path)
    return renderer.implementation()

def render_template(path, **kw):
    """ Render a ``jinja2`` template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a string. """
    renderer = renderer_factory(path)
    return renderer(kw, {})

def render_template_to_response(path, **kw):
    """ Render a ``jinja2`` template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a Response object. """
    renderer = renderer_factory(path)
    result = renderer(kw, {})
    response_factory = queryUtility(IResponseFactory, default=Response)
    return response_factory(result)
