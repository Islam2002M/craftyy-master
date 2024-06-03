import logging
from logging.handlers import RotatingFileHandler
from pythonic import app, db


if __name__ == '__main__':
     # Configure logging
  if not app.debug:
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Ensure that we log to the console as well
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)

app.run(debug=True)
