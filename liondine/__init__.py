from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow

from liondine.models import appmaker
from secret import AUTH_SECRET
from secret import SEC_CALLBACK
from pyramid.session import UnencryptedCookieSessionFactoryConfig

authentication_policy = AuthTktAuthenticationPolicy(AUTH_SECRET, callback=SEC_CALLBACK)
authorization_policy = ACLAuthorizationPolicy()
my_session_factory = UnencryptedCookieSessionFactoryConfig(AUTH_SECRET)


class RootFactory(object):
    __acl__ = [ (Allow, 'student', 'register'),
                (Allow, 'faculty', 'create')]
    def __init__(self, request):
        pass

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
#    engine = engine_from_config(settings, 'sqlalchemy.')
#    get_root = appmaker(engine)
    config = Configurator(settings=settings, root_factory=RootFactory, session_factory=my_session_factory, authentication_policy=authentication_policy, authorization_policy=authorization_policy)
    config.add_static_view('static', 'liondine:static')
    config.add_view('liondine.views.view_model',
                    context='liondine.models.MyModel',
                    renderer="templates/model.pt")
    config.add_view('liondine.views.home',
                    context='pyramid.httpexceptions.HTTPForbidden',
                    renderer='templates/home.pt')
    config.add_route('home', '/')
    config.add_route('logout', '/logout')
    config.add_route('student', '/student')
    config.add_route('student_register', '/student_join')
    config.add_route('st_login', '/st_login')
    config.add_route('fac_login', '/fac_login')
    config.add_route('st_auth', '/st_auth')
    config.add_route('fac_auth', '/fac_auth')
    config.add_route('appts', '/appts')
    config.add_route('faculty', '/faculty')
    config.add_route('faculty_register', '/faculty_join')
    config.add_route('create', '/create')
    config.add_route('signup', '/signup/{mongoid}')
    config.add_route('create_conf', '/create_conf')
    config.scan("liondine")
    return config.make_wsgi_app()
