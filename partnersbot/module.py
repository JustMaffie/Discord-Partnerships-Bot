class Module:
    def __init__(self, bot):
        self.bot = bot
        self._ = bot._
        self.db = bot.db
        self.logger = bot.logger
        self.config = bot.config