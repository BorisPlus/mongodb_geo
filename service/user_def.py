from dummy_wsgi_framework.core.dispatchers import decorate_loaded_view_function_for_response
from dummy_wsgi_framework.core.exceptions import (
    ExistViewFileIsInvalid,
    ViewDoesNotExist
)
import config
import jinja2
import os


@decorate_loaded_view_function_for_response
def load_jinja2_view_template(view_template_path, **kwargs):
    try:
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(config.APP_VIEWS_DIR))
        template = environment.get_template(os.path.basename(view_template_path))
        return template.render(**kwargs).encode()
    except jinja2.exceptions.TemplateSyntaxError as e:
        raise ExistViewFileIsInvalid('File "%s" - %s' % (view_template_path, e.message))
    except jinja2.exceptions.TemplateNotFound as e:
        raise ViewDoesNotExist('File "%s" not found %s' % (view_template_path, e.message))
