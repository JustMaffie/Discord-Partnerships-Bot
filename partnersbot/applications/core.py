import discord
import datetime

class Application: 
    def __init__(self, manager, _id, author, fields, timestamp, message_id=None, approved=None, deny_reason=None):
        self.manager = manager
        self.id = _id
        self.author = author
        self.fields = fields
        self.timestamp = timestamp
        self.message_id = message_id
        self.approved = approved
        self.deny_reason = deny_reason

    async def update_message_id(self, new_message_id):
        self.message_id = new_message_id
        if self.manager.db_enabled:
            await self.manager.bot.applications.update_one({"_id": self.id}, {"$set": self.mongo_dict}, upsert=True)

    async def update_message(self):
        message = await self.manager.output.get_message(self.message_id)
        embed = await self.manager.generate_embed(self)
        if not message:
            await self.manager.send(embed=embed)
        else:
            await message.edit(embed=embed)

    async def approve(self):
        if self.approved != None:
            return 1
        try:
            self.approved = True
            if self.manager.db_enabled:
                await self.manager.bot.applications.update_one({"_id": self.id}, {"$set": self.mongo_dict}, upsert=True)
            await self.update_message()
            return 2
        except:
            return 3

    async def deny(self, reason=None):
        if self.approved != None:
            return 1
        try:
            self.approved = False
            self.deny_reason = reason
            if self.manager.db_enabled:
                await self.manager.bot.applications.update_one({"_id": self.id}, {"$set": self.mongo_dict}, upsert=True)
            await self.update_message()
            return 2
        except:
            return 3

    @property
    def approved_to_string(self) -> str:
        if self.approved == None:
            return "Pending"
        elif self.approved == True:
            return "Approved"
        elif self.approved == False:
            return "Denied"
        return "Unknown Status"

    @property
    def __dict__(self):
        return {
            "id": self.id, 
            "author": self.author, 
            "fields": self.fields, 
            "timestamp": self.timestamp, 
            "message_id": self.message_id,
            "approved": self.approved,
            "deny_reason": self.deny_reason
        }
    
    @classmethod
    def from_mongo(self, manager, dict):
        app = Application(
            manager, 
            dict.get("_id", None), 
            dict.get("author", None), 
            dict.get("fields", None), 
            dict.get("timestamp", None), 
            dict.get("message_id", None), 
            dict.get("approved", None), 
            dict.get("deny_reason", None)
        )
        return app

    @property
    def mongo_dict(self):
        return {
            "_id": self.id, 
            "author": self.author, 
            "fields": self.fields, 
            "timestamp": self.timestamp, 
            "message_id": self.message_id,
            "approved": self.approved,
            "deny_reason": self.deny_reason
        }

class EmptyApplication(Application):
    def __init__(self):
        super(EmptyApplication, self, None, None, None, None)

class ApplicationManager:
    def __init__(self, bot):
        self.bot = bot
        self.db_enabled = bot.config.database.enabled
        if bot.config.database.enabled:
            self.metadata = bot.db.metadata
        self.output = self.bot.get_channel(id=self.bot.config.output)

    async def generate_embed_no_instance(self, author, fields, timestamp) -> discord.Embed:
        embed = discord.Embed(timestamp=timestamp)
        embed.colour = discord.Color.blue()
        author_instance = await self.bot.get_user_info(author)
        embed.set_author(name=str(author_instance), icon_url=author_instance.avatar_url)
        embed.set_footer(text="User ID: {}".format(author))
        embed.set_thumbnail(url=author_instance.avatar_url)
        for field in fields:
            embed.add_field(name=field['embed_title'], value=field['answer'])
        return embed

    async def generate_embed(self, application:Application) -> discord.Embed:
        embed = discord.Embed(title="{} | Application #{}".format(application.approved_to_string, application.id), timestamp=application.timestamp)
        author_instance = await self.bot.get_user_info(application.author)
        embed.set_author(name=str(author_instance), icon_url=author_instance.avatar_url)
        embed.set_footer(text="User ID: {}".format(application.author))
        embed.set_thumbnail(url=author_instance.avatar_url)
        if application.deny_reason:
            embed.add_field(name="Deny Reason", value=application.deny_reason)
        if application.approved == None:
            embed.colour = discord.Color.blue()
        elif application.approved == False:
            embed.colour = discord.Color.red()
        elif application.approved == True:
            embed.colour = discord.Color.green()
        for field in application.fields:
            embed.add_field(name=field['embed_title'], value=field['answer'])
        return embed

    async def insert(self, application:Application) -> None:
        await self.bot.db.applications.insert_one(application.mongo_dict)

    async def send(self, embed) -> discord.Message:
        return await self.output.send(embed=embed)        

    async def _get_request_id(self) -> int:
        if not hasattr(self, "metadata"):
            return None
        casecount_doc = await self.metadata.find_one({'_id': "request_count"})
        if not casecount_doc:
            await self.metadata.insert_one({"_id": "request_count", "value": 0})
            return await self._get_request_id()
        casecount = casecount_doc['value'] + 1
        await self.metadata.replace_one({'_id': "request_count"},{'value': casecount})
        return casecount

    async def create_application(self, author, fields) -> Application:
        timestamp = datetime.datetime.utcnow()
        if self.db_enabled:
            _id = await self._get_request_id()
            app = Application(self, _id, author, fields, timestamp)
            embed = await self.generate_embed(app)
            message = await self.send(embed)
            app.message_id = message.id
            await self.insert(app)
            return app
        else:
            await self.send(await self.generate_embed_no_instance(author, fields, timestamp))
            return Application(self, None, author, fields, timestamp)

    async def get_application(self, _id) -> Application:
        if not self.db_enabled:
            return EmptyApplication()
        result = await self.bot.db.applications.find_one({"_id": _id})
        if not result:
            return EmptyApplication()
        return Application.from_mongo(self, result)
        