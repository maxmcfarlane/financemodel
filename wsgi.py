"""Application entry point"""
import flask
from dashapp import create_app

server = flask.Flask(__name__,
                     template_folder='templates',
                     static_folder='static',
                     instance_relative_config=True)

app = create_app(server)

if __name__ == "__main__":
    app.run(debug=True)
