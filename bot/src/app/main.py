from .bot import app

from . import logger

if __name__ == "__main__":
    app.run_polling()