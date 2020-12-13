from . import create_app

app = create_app()

from .createEvent import createEvent
from .deleteEvent import deleteEvent

app.register_blueprint(createEvent)
app.register_blueprint(deleteEvent)
