from . import create_app

app = create_app()

from .createEvent import createEvent

app.register_blueprint(createEvent)