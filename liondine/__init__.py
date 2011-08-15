from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from liondine.models import appmaker

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    get_root = appmaker(engine)
    config = Configurator(settings=settings, root_factory=get_root)
    config.add_static_view('static', 'liondine:static')
    config.add_view('liondine.views.view_root', 
                    context='liondine.models.MyRoot', 
                    renderer="templates/root.pt")
    config.add_view('liondine.views.view_model',
                    context='liondine.models.MyModel',
                    renderer="templates/model.pt")
    config.add_route('student', '/student')
    config.add_route('student_register', '/student_join')
    config.add_route('appts', '/appts')
    config.add_route('faculty', '/faculty')
    config.add_route('faculty_register', '/faculty_join')
    config.add_route('create', '/create')
    config.add_route('signup', '/signup/{mongoid}')
    config.add_route('create_conf', '/create_conf')
    config.scan("liondine")
    return config.make_wsgi_app()


