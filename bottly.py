import json, re, socket, string, sys

from urllib.request import urlopen

with open('config.json') as json_data:
	data = json.load(json_data)

SERVER = data['Server']
PORT = data['Port']
CHANNEL = data['Channel']

NICK = data['BotNick']
TRIGGER = data['Trigger']
ADMINS = data['Admins']


class Bottly(object):

	def __init__(self, server, port, nick, admins, trigger):
		self.server = server
		self.port = int(port)
		self.nick = nick
		self.admins = admins
		self.trigger = trigger
		self.hushed = False

	def connect_server(self):
		self.irc = socket.socket()
		self.irc.connect((self.server, self.port))

	def disconnect_server(self):
		self.send_data('QUIT :Quit: fuck this shit')
		self.irc.close()

	def pong(self, target=':Pong'):
		message = 'PONG %s' % target
		self.send_data(message)

	def join_channel(self, channel, password=''):
		self.send_data('JOIN %s' % channel)

	def leave_channel(self, channel, message):
		self.send_data('PART %s :[...not that anyone cares ]' % channel)
		print(message)


	def register_nick(self):
		self.send_data('USER {0} {0} {1} {0}'.format(self.nick, self.server))
		self.send_data('NICK ' + self.nick)

	def send_data(self, data):
		if data is not None:
			self.irc.send(str.encode(data + '\r\n'))

	def send_message(self, reciever, message):
		self.send_data('PRIVMSG ' + reciever + ' :' + message)

	def get_data(self):
		data = self.irc.recv(4096)
		decoded_data = []
		for item in data.split():
			decoded_data.append(item.decode('UTF-8'))
		print(decoded_data)
		print(data)
		return decoded_data

	def check_input(self, data):
		if 'ERROR' in data:
			print('Error, disconnecting')
		elif data[1] in ['PRIVMSG', 'JOIN', 'PART']:
			self.command_filter(data)
		elif data[0] == 'PING':
			self.pong(data[0])

	def command_filter(self, data):
		sender = self.get_sender(data[0])
		channel = data[2]
		try:
			command = data[3].lstrip(':')
		except:
			command = None
		if '#' not in channel:
			print('privmsg')
		else:
			if self.hushed==False:
				if self.trigger + 'foo' == command:
					self.send_message(channel, 'bar')
				elif self.trigger + 'leave' == command:
					if self.is_admin(sender):
						try:
							channel = data[4]
						except IndexError:
							pass
						message = '...not that anyone cares'
						self.leave_channel(channel, message)
					else:
						self.deny_command(channel, sender)
				elif self.trigger + 'join' == command:
					if self.is_admin(sender):
						try:
							channel = data[4]
						except IndexError:
							pass
						self.join_channel(channel)
					else:
						self.deny_command(channel, sender)
				elif self.trigger + 'quit' == command:
					self.disconnect_server()
				elif self.trigger + 'hush' == command:
					self.send_message(channel, 'Fine... I\'ll be quite!')
					self.hushed = True
				elif self.trigger + 'isup' == command:
					try:
						state = self.isup(data[4])
						if state=='UP':
							self.send_message(channel, 'It\'s just you! %s appears to be up from here' % data[4])
						elif state=='DOWN':
							self.send_message(channel, 'It\'s not just you! %s appears to be down from here to' % data[4])	
					except IndexError:
						self.send_message(channel, 'Please provide a URL')
			if self.trigger + 'unhush' == command and self.is_admin(sender):
				self.send_message(channel, 'Freedom!!!')
				self.hushed = False
	def get_sender(self, line):
		sender = ''
		for char in line:
			if char == '!':
				break
			if char != ':':
				sender += str(char)
		return sender

	def is_admin(self, user_nick):
		return user_nick in self.admins

	def isup(self, domain):
		resp = urlopen('http://www.isup.me/%s' % domain).read()
		if re.search(str.encode('It\'s just you.'), resp, re.DOTALL):
			state = 'UP'
		else:
			state = 'DOWN'	
		return state

	def deny_command(self, channel, sender):	
		self.send_message(channel, 'Not authed')

if __name__ == '__main__':
	bot = Bottly(SERVER, PORT, NICK, ADMINS, TRIGGER)
	bot.connect_server()
	bot.register_nick()

	for channel in CHANNEL:
		bot.join_channel(channel)

	while 1:
		data = bot.get_data()
		if len(data) == 0:
			break
		bot.check_input(data)

	bot.disconnect_server()
