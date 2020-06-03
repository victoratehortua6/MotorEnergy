from flask import Flask

app = Flask(__name__)
app.secret_key = 'A blog by victoratehortua6 & SGT911'
app.template_folder = 'views'

from routes.apis.users import router as users_api
from routes.users import router as users

app.register_blueprint(users_api, url_prefix='/api/users')
app.register_blueprint(users, url_prefix='/')

if __name__ == "__main__":
	app.debug = True
	app.run(
		port=5000,
		host='localhost'
	)