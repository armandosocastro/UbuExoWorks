from multiprocessing import context
from OpenSSL import SSL
from app import create_app
import app
import os

app = create_app()

#app.config['SECRET_KEY'] = 'pASSW0Rd'

if __name__ == '__main__':

    _port = os.environ.get('PORT', 5000)
    context = ('./cert/selfsigned.crt', './cert/selfsigned.key')
    #app.run('0.0.0.0', port=_port)
    app.run('0.0.0.0', ssl_context=context)