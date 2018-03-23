from collections import namedtuple

Application = namedtuple("Application", 'id approved author fields timestamp deny_reason')

class ApplicationManager:
    def __init__(self, bot):
        self.bot = bot
        if bot.config.database.enabled:
            self.metadata = bot.db.metadata

    def get_channel(self, id):
        channel = self.bot.get_channel(id=id)
        return channel

    async def _get_request_id(self):
        if not hasattr(self, "metadata"):
            return None
        casecount_doc = await self.metadata.find_one({'_id': "request_count"})
        if not casecount_doc:
            await self.metadata.insert_one({"_id": "request_count", "value": 0})
            return await self._get_request_id()
        casecount = casecount_doc['value'] + 1
        await self.metadata.replace_one({'_id': "request_count"},{'value': casecount})
        return casecount

    async def create_application(self, author, fields):
        pass

    async def get_application(self, _id):
        pass