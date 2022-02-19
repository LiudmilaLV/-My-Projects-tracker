import os
from website import create_app

app = create_app()

if __name__ == '__main__':
    DEBUG = os.environ.get('DEBUG') == 'True'
    app.run(debug=DEBUG, host="0.0.0.0")
