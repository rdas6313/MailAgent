import socket
import ssl
import base64
import time

class SmtpResponseCodes:
	error_codes = {
		'421': 'Service not available and connection will be closed',
		'432': ' A password transition is needed',
		'450': 'Requested command failed',
		'451': 'Command aborted due to server error',
		'452': 'Command aborted due to server storage error',
		'454': 'Temporary authentication failure',
		'455': 'Server unable to accommodate parameters',
		'500': 'Unable to recognize the command due to syntax error',
		'501': 'Syntax error',
		'502': 'command not implemented',
		'503': 'bad sequence of command',
		'523': 'Encryption Needed',
		'530': 'Authentication required',
		'534': 'Authentication mechanism is too weak',
		'535': 'Authentication credentials invalid',
		'538': 'Encryption required for requested authentication mechanism',
		'550': 'mailbox unavailable',
		'551': 'User not local',
		'552': 'action aborted due to exceeded storage allocation',
		'553': 'mailbox name is invalid',
		'554': 'mailbox disabled or Transaction has failed or Message too big for system',
		'556': 'Domain does not accept mail'
		
	}
	
	success_codes = {
		'220': 'service ready',
		'354': 'ready to accept data',
		'250': 'action taken and completed',
		'221': 'service closing',
		'334': 'provide base64 encoded input',
		'235': 'Authentication succeed',
		'211': 'system status',
		'214': 'help message',
		'240': 'quit',
		'250': 'Requested mail action completed',
		'251': 'User not local, will forward',
		'252': 'Cannot verify the user, but will try to deliver the message anyway'

	}
	
	def isValid(self,data):
		return self.success_codes.get(data[:3],False)

class SmtpClient:

	def __init__(self,hostname,port):
		self.hostname = hostname
		self.port = port
		self.checker = SmtpResponseCodes()

	def get(self,conn,checker):
		data = conn.recv(2048).decode()
		print(f'Mail server: {data}')
		if not checker.isValid(data):
			raise ValueError(checker.error_codes.get(data[:3],f'{data[:3]}, Unknown Error occured'))

	def send(self,conn,data):
		print(f'Client app: {data}')
		conn.sendall(data.encode())

	def get_msg_id(self):
		timestamp = round(time.time() * 1000)
		msg_id = f'{timestamp}@{mail_server}'
		return msg_id

	def start_dialoging(self,conn,meta_data):
		try:
			username = meta_data.get('username',None)
			password = meta_data.get('password',None)
			user_mail = meta_data.get('user_mail',None)
			receiver_mail = meta_data.get('receiver_mail',None)
			user_mail = meta_data.get('user_mail',None)
			subject = meta_data.get('subject',None)
			body = meta_data.get('body',None)

			checker = self.checker
			self.get(conn,checker)
			self.send(conn,'HELO ClientApp\r\n')
			self.get(conn,checker)
			self.send(conn,'AUTH LOGIN\r\n')
			self.get(conn,checker)
			self.send(conn,f'{username}\r\n')
			self.get(conn,checker)
			self.send(conn,f'{password}\r\n')
			self.get(conn,checker)
			self.send(conn,f'MAIL FROM:<{user_mail}>\r\n')
			self.get(conn,checker)
			self.send(conn,f'RCPT TO:<{receiver_mail}>\r\n')
			self.get(conn,checker)
			self.send(conn,'DATA\r\n')
			self.get(conn,checker)
			self.send(conn,f'From:<{user_mail}>\r\nTo:<{receiver_mail}>\r\nMessage-id:{self.get_msg_id()}\r\nContent-Type: text/plain; charset="UTF-8"\r\nSubject:{subject}\r\n{body}\r\n')
			self.send(conn,'\r\n.\r\n')
			self.get(conn,checker)
			self.send(conn,'QUIT\r\n')
			self.get(conn,checker)

		except ValueError as v:
			print(f'Error Msg: {v}')
			return False
		return True

	def send_mail(self,meta_data):
		try:
			context = ssl.create_default_context()
			with socket.create_connection((self.hostname,self.port)) as sock:
				with context.wrap_socket(sock,server_hostname=self.hostname) as conn:
					print(f'Version: {conn.version()}\n')
					return self.start_dialoging(conn,meta_data)
		except ssl.SSLError as ssl_error:
			print(ssl_error)
			return false
		except:
			print('Unknown Error while connection establishing.')
			return false
		
				




if __name__ == '__main__':
	print('Provide your login auth..( Here we need app password, not your gmail password. )')
	user_mail = input('Your Mail id: ')
	user_mail = user_mail.strip().split('@')
	username = user_mail[0]
	mail_server = user_mail[1]
	password = input('App password: ')
	receiver_mail = input('Receiver Mail id: ')
	subject = input('Subject: ')
	body = input('Body: ')
	
	mail_meta_data = {
		'mail_server': mail_server,
		'user_mail': f'{username}@{mail_server}',
		'receiver_mail': receiver_mail,
		'subject': subject,
		'body': body,
		'username': base64.standard_b64encode(username.encode()).decode(),
		'password': base64.standard_b64encode(password.encode()).decode()
	}

	hostname = 'smtp.gmail.com'
	port = 465

	smtp_client = SmtpClient(hostname,port)
	print(f'\nTrying to send mail to {receiver_mail}...')
	print('\n.................................................................\n')
	is_sent = smtp_client.send_mail(mail_meta_data)
	print('\n.................................................................\n')
	if is_sent:
		print("Mail sent successfully.")
	else:
		print("Unable to send Mail.")

