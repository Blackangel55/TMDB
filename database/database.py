"""
database.py — MongoDB handler for TMDB Poster Bot
"""

import logging
import motor.motor_asyncio

from config import DB_URI, DB_NAME

log = logging.getLogger(__name__)


class Database:

    def __init__(self, db_uri: str, db_name: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            db_uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        self.db = self.client[db_name]

        self.users       = self.db["users"]
        self.banned      = self.db["banned_users"]
        self.admins      = self.db["admins"]
        self.fsub        = self.db["fsub_channels"]
        self.image_cache = self.db["image_cache"]

    async def ping(self) -> bool:
        try:
            await self.client.admin.command("ping")
            return True
        except Exception as e:
            log.error("MongoDB connection failed: %s", e)
            return False

    # ─── USER ────────────────────────────────────────────────────────────────

    async def user_exists(self, user_id: int) -> bool:
        return bool(await self.users.find_one({"_id": user_id}))

    async def add_user(self, user_id: int):
        if not await self.user_exists(user_id):
            await self.users.insert_one({"_id": user_id})
            log.info("New user: %s", user_id)

    async def del_user(self, user_id: int):
        await self.users.delete_one({"_id": user_id})

    async def get_all_users(self) -> list[int]:
        docs = await self.users.find().to_list(length=None)
        return [d["_id"] for d in docs]

    async def total_users(self) -> int:
        return await self.users.count_documents({})

    # ─── BAN ─────────────────────────────────────────────────────────────────

    async def is_banned(self, user_id: int) -> bool:
        return bool(await self.banned.find_one({"_id": user_id}))

    async def ban_user(self, user_id: int):
        if not await self.is_banned(user_id):
            await self.banned.insert_one({"_id": user_id})

    async def unban_user(self, user_id: int):
        await self.banned.delete_one({"_id": user_id})

    async def get_banned_users(self) -> list[int]:
        docs = await self.banned.find().to_list(length=None)
        return [d["_id"] for d in docs]

    # ─── ADMIN ───────────────────────────────────────────────────────────────

    async def is_admin(self, user_id: int) -> bool:
        return bool(await self.admins.find_one({"_id": user_id}))

    async def add_admin(self, user_id: int):
        if not await self.is_admin(user_id):
            await self.admins.insert_one({"_id": user_id})

    async def del_admin(self, user_id: int):
        await self.admins.delete_one({"_id": user_id})

    async def get_all_admins(self) -> list[int]:
        docs = await self.admins.find().to_list(length=None)
        return [d["_id"] for d in docs]

    # ─── FORCE SUBSCRIBE ─────────────────────────────────────────────────────

    async def add_fsub_channel(self, channel_id: int):
        if not await self.fsub.find_one({"_id": channel_id}):
            await self.fsub.insert_one({"_id": channel_id})

    async def remove_fsub_channel(self, channel_id: int):
        await self.fsub.delete_one({"_id": channel_id})

    async def get_fsub_channels(self) -> list[int]:
        docs = await self.fsub.find().to_list(length=None)
        return [d["_id"] for d in docs]

    async def fsub_channel_exists(self, channel_id: int) -> bool:
        return bool(await self.fsub.find_one({"_id": channel_id}))

    # ─── IMAGE CACHE ─────────────────────────────────────────────────────────

    async def get_cached_image(self, url_hash: str) -> dict | None:
        return await self.image_cache.find_one({"_id": url_hash})

    async def cache_image(self, url_hash: str, url: str,
                          file_id: str = None, image_bytes: bytes = None):
        import bson
        update = {"url": url}
        if file_id:
            update["file_id"] = file_id
        if image_bytes:
            update["bytes"] = bson.Binary(image_bytes)
        await self.image_cache.update_one(
            {"_id": url_hash}, {"$set": update}, upsert=True
        )

    async def update_file_id(self, url_hash: str, file_id: str | None):
        update = {"$set": {"file_id": file_id}} if file_id else {"$unset": {"file_id": ""}}
        await self.image_cache.update_one({"_id": url_hash}, update)

    async def clear_cache(self, url_hash: str):
        await self.image_cache.delete_one({"_id": url_hash})


db = Database(DB_URI, DB_NAME)
