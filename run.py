from app import create_app
import os

app = create_app()



_port = os.environ.get('PORT', 5000)
app.run(host='0.0.0.0', port=_port)