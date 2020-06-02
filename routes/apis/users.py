from flask import Blueprint, jsonify, request
from controllers.users import UserController, UniqueViolation
from jsonschema import validate, ValidationError

router = Blueprint('users api', __name__)

@router.route('/', methods=[ 'GET' ])
def get_all():
	users = list(map(lambda u: u.to_json(), UserController.get_all()))
	return jsonify(users), 200

@router.route('/<int:uid>/', methods=[ 'GET' ])
def get_one(uid: int):
	user = UserController.get_one(uid)

	if user is None:
		error = { "error": "NotFound", "msg": f"The user \"{uid}\" not found." }
		return jsonify(error), 404

	return jsonify(user.to_json()), 200

@router.route('/login/', methods=[ 'POST' ])
def get_login():
	schema = {
		"type": "object",
		"additionalProperties": False,
		"required": [ 'email', 'password' ],
		"properties": {
			"email": {
				"type": "string",
				"pattern": r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
			},
			"password": {
				"type": "string",
				"minLength": 8
			}
		}
	}
	data = dict(**request.form)

	try:
		validate(data, schema)
	except ValidationError as e:
		err = { "error": "ValidationError", "msg": e.message }
		return jsonify(err), 400

	user = UserController.get_login(data["email"], data["password"])

	if user is None:
		err = { "error": "Unauthorized", "msg": f"The user \"{data['email']}\" doesn\'t exist or the password doesn\'t match." }
		return jsonify(err), 401

	return jsonify(user.to_json()), 200

@router.route('/', methods=[ 'POST' ])
def create():
	schema = {
		"type": "object",
		"additionalProperties": False,
		"required": [ 'fName', 'fLastName', 'email', 'password' ],
		"properties": {
			"fName": {
				"type": "string"
			},
			"sName": {
				"type": "string"
			},
			"fLastName": {
				"type": "string"
			},
			"sLastName": {
				"type": "string"
			},
			"email": {
				"type": "string",
				"pattern": r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
			},
			"password": {
				"type": "string",
				"minLength": 8
			}
		}
	}

	data = dict(**request.form)

	try:
		validate(data, schema)
	except ValidationError as e:
		err = { "error": "ValidationError", "msg": e.message }
		return jsonify(err), 400

	data['f_name'] = data.pop('fName')
	data['f_last_name'] = data.pop('fLastName')
	data['s_name'] = data.pop('sName', None)
	data['s_last_name'] = data.pop('sLastName', None)

	try:
		uid = UserController.create(**data)
		return jsonify(uid), 200
	except UniqueViolation as e:
		err = { "error": "UniqueViolation", "msg": "The email already exists." }
		return jsonify(err), 500



@router.route('/<int:uid>/', methods=[ 'PUT' ])
def modify(uid: int):
	schema = {
		"type": "object",
		"additionalProperties": False,
		"properties": {
			"fName": {
				"type": "string"
			},
			"sName": {
				"type": "string"
			},
			"fLastName": {
				"type": "string"
			},
			"sLastName": {
				"type": "string"
			},
			"email": {
				"type": "string",
				"pattern": r"^([a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*|)$"
			}
		}
	}

	form = dict(**request.form)
	data = {}

	try:
		validate(form, schema)
	except ValidationError as e:
		err = { "error": "ValidationError", "msg": e.message }
		return jsonify(err), 400

	for index in form:
		if form[index] != '':
			data[index] = form.get(index)

	if 'fName' in data:
		data['f_name'] = data.pop('fName')

	if 'fLastName' in data:
		data['f_last_name'] = data.pop('fLastName')

	if 'sName' in data:
		if data.get('sName') == 'null':
			data['s_name'] = None
			data.pop('sName')
		else:
			data['s_name'] = data.pop('sName')

	if 'sLastName' in data:
		if data.get('sLastName') == 'null':
			data['s_last_name'] = None
			data.pop('sLastName')
		else:
			data['s_last_name'] = data.pop('sLastName')

	modified = UserController.modify(uid, **data)

	if not modified:
		error = { "error": "NotFound", "msg": f"The user \"{uid}\" not found." }
		return jsonify(error), 404
	else:
		return jsonify('modified'), 200


@router.route('/change_password/<int:uid>/', methods=[ 'PUT' ])
def change_password(uid: int):
	schema = {
		"type": "object",
		"additionalProperties": False,
		"required": [ 'password' ],
		"properties": {
			"password": {
				"type": "string",
				"minLength": 8
			}
		}
	}

	data = dict(**request.form)

	try:
		validate(data, schema)
	except ValidationError as e:
		err = { "error": "ValidationError", "msg": e.message }
		return jsonify(err), 400


	modified = UserController.change_password(uid, data['password'])

	if not modified:
		error = { "error": "NotFound", "msg": f"The user \"{uid}\" not found." }
		return jsonify(error), 404
	else:
		return jsonify('password modified'), 200

@router.route('/<int:uid>/', methods=[ 'DELETE' ])
def delete(uid: int):
	deleted = UserController.delete(uid)

	if not deleted:
		error = { "error": "NotFound", "msg": f"The user \"{uid}\" not found." }
		return jsonify(error), 404

	return jsonify('deleted'), 200