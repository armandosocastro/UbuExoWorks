from app import create_app
import os

app = create_app()

#if __name__ == '__main__':

_port = os.environ.get('PORT', 5000)
app.run()