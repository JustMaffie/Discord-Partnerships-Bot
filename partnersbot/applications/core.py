class Application:
    pass

class ApplicationManager:
    def __init__(self, bot):
        self.bot = bot
        self.metadata = bot.db.metadata

    async def _get_request_id(self):
        casecount_doc = await self.metadata.find_one({'_id': "request_count"})
        if not casecount_doc:
            await self.metadata.insert_one({"_id": "request_count", "value": 0})
            return await self._get_request_id()
        casecount = casecount_doc['value'] + 1
        await self.metadata.replace_one({'_id': "request_count"},{'value': casecount})
        return casecount
