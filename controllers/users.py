from controllers.database import DB, UniqueViolation
import hashlib

def hash_password(password: str) -> str:
	hash_text = hashlib.new('sha512')
	hash_text.update(password.encode())
	return hash_text.hexdigest()

class User:
	def __init__(self, **kwargs):
			self.id = kwargs['id']
			self.f_name = kwargs['fName']
			self.s_name = kwargs.get('sName', None)
			self.f_last_name = kwargs['fLastName']
			self.s_last_name = kwargs.get('sLastName', None)
			self.email = kwargs['email']
			self.creation = kwargs['creation']

	def get_initials(self) -> str:
		initials = ''

		initials += self.f_name[0:1]
		if self.s_name is not None:
			initials += self.s_name[0:1]
		initials += self.f_last_name[0:1]
		if self.s_last_name is not None:
			initials += self.s_last_name[0:1]

		return initials.upper()

	def full_name(self) -> str:
		name = [ self.f_name.title() ]

		if self.s_name is not None:
			name.append(self.s_name.title())

		name.append(self.f_last_name.title())

		if self.s_last_name is not None:
			name.append(self.s_last_name.title())
		return ' '.join(name)

	def to_json(self):
		user = {
			'id': self.id,
			'fName': self.f_name,
			'sName': self.s_name,
			'fLastName': self.f_last_name,
			'sLastName': self.s_last_name,
			'email': self.email,
			'creation': self.creation.isoformat()
		}

		return user

	def __str__(self):
		return f'{self.f_name.title()} {self.f_last_name.title()} - {self.email}'

class UserController:
	@staticmethod
	def get_all() -> list:
		cursor = DB.cursor()
		cursor.execute("SELECT id, f_name, s_name, f_last_name, s_last_name, email, creation FROM users")

		def format(cursor):
			for user in cursor:
				user = {
					'id': user[0],
					'fName': user[1],
					'sName': user[2],
					'fLastName': user[3],
					'sLastName': user[4],
					'email': user[5],
					'creation': user[6]
				}

				yield User(**user)

		
		users = list(format(cursor))

		cursor.close()

		return users

	@staticmethod
	def get_one(uid: int) -> User or None:
		cursor = DB.cursor()

		cursor.execute("SELECT f_name, s_name, f_last_name, s_last_name, email, creation FROM users WHERE id = %s ORDER BY id ASC", [ uid ])

		data = cursor.fetchone()
		if data == None:
			return None

		user = {
			'id': uid,
			'fName': data[0],
			'sName': data[1],
			'fLastName': data[2],
			'sLastName': data[3],
			'email': data[4],
			'creation': data[5]
		}

		cursor.close()

		return User(**user)

	@staticmethod
	def get_login(email: str, password: str) -> User:
		cursor = DB.cursor()

		cursor.execute("SELECT id, f_name, s_name, f_last_name, s_last_name, email, creation FROM users WHERE email = %s AND password = %s", [ email, hash_password(password) ])

		data = cursor.fetchone()
		if data == None:
			return None

		user = {
			'id': data[0],
			'fName': data[1],
			'sName': data[2],
			'fLastName': data[3],
			'sLastName': data[4],
			'email': data[5],
			'creation': data[6]
		}

		cursor.close()

		return User(**user)

	@staticmethod
	def create(**kwargs) -> int:
		if 'f_name' not in kwargs and 'f_last_name' not in kwargs and 'email' not in kwargs and 'password' not in kwargs:
			raise ValueException('Some field are required')

		fields = [ 'f_name', 'f_last_name', 'email', 'password' ]
		data = [ kwargs['f_name'].lower(), kwargs['f_last_name'].lower(), kwargs['email'], hash_password(kwargs['password']) ]

		if kwargs.get('s_name', None) is not None and kwargs.get('s_name', None) != '':
			fields.append('s_name')
			data.append(kwargs['s_name'].lower())

		if kwargs.get('s_last_name', None) is not None and kwargs.get('s_last_name', None) != '':
			fields.append('s_last_name')
			data.append(kwargs['s_last_name'].lower())

		cursor = DB.cursor()

		try:
			cursor.execute(f"INSERT INTO users ({ ', '.join(fields) }) VALUES ({ ', '.join(list(map(lambda f: '%s', fields))) }) RETURNING id", data)
		except Exception as e:
			DB.rollback()
			raise e

		uid = cursor.fetchone()[0]

		DB.commit()
		cursor.close()

		return uid

	@staticmethod
	def modify(uid: int, **kwargs) -> bool:
		fields = [ ]
		data = [ ]
		for index in kwargs:
			if 'f_name' == index or 's_name' == index or 'f_last_name' == index or 's_last_name' == index or 'email' == index:
				fields.append(index)
				if kwargs[index] != '' and kwargs[index] != None:
					if 'f_name' == index or 's_name' == index or 'f_last_name' == index or 's_last_name' == index:
						data.append(kwargs[index].lower())
					else:
						data.append(kwargs[index])
				else:
					data.append(None)

		cursor = DB.cursor()

		data.append(uid)

		try:
			cursor.execute(f"UPDATE users SET { ', '.join(list(map(lambda f: '{} = %s'.format(f), fields))) } WHERE id = %s", data)
		except Exception as e:
			DB.rollback()
			raise e

		if cursor.rowcount == 0:
			DB.rollback()
			cursor.close()
			return False
		else:
			DB.commit()
			cursor.close()
			return True

	@staticmethod
	def change_password(uid: int, password: str) -> bool:
		cursor = DB.cursor()

		try:
			cursor.execute("UPDATE users SET password = %s WHERE id = %s", [ hash_password(password), uid ])
		except Exception as e:
			DB.rollback()
			raise e

		if cursor.rowcount == 0:
			DB.rollback()
			cursor.close()
			return False
		else:
			DB.commit()
			cursor.close()
			return True

	@staticmethod
	def delete(uid: int) -> bool:
		cursor = DB.cursor()

		try:
			cursor.execute("DELETE FROM users WHERE id = %s", [ uid ])
		except Exception as e:
			DB.rollback()
			raise e

		if cursor.rowcount == 0:
			DB.rollback()
			cursor.close()
			return False
		else:
			DB.commit()
			cursor.close()
			return True
