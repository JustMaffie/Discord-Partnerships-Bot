import json
import os

class I18N:
	def __init__(self, bot):
		self.lang = bot.config.language
		self._translations = {}
		self.initialize()

	def __call__(self, string, default=None):
		return self.get(string, default)

	def initialize(self):
		if not os.path.exists("i18n/{}/data.json".format(self.lang)):
			raise SyntaxError("The language '{}' isn't yet supported.".format(self.lang))
		self._translations = json.load(open('i18n/{}/data.json'.format(self.lang)))

	def get(self, string, default):
		if default == None:
			default = string
		return self._translations.get(string, default)