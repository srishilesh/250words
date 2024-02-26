import os
from flask import Flask

def create_app(test_config=None):
    """
    create_app - application factory function
    instance_relative_config - can hold local data that shouldn't be commited to git - relative to 'instance' folder
    SECRET_KEY - to keep session data safe using a key
    DATABASE - path to the db file
    instance_path - folders or files that are runtime configurable, and not app 
    test_config - load test configurations from map or py file
    """

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, '250words.sqlite')
    )

    # if test_config is None:
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def ping():
        return "Ping successful"
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    return app