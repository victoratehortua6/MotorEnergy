from flask import Blueprint, render_template, request
# from controllers.users import UserController, UniqueViolation
# from jsonschema import validate, ValidationError

router = Blueprint('users', __name__)

@router.route('/login', methods=[ 'GET' ])
def login():
	return render_template('login.html', title='Login')

@router.route('/register', methods=[ 'GET' ])
def register():
	return render_template('register.html', title='Sign up')