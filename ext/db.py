import json
import asyncio
import typing

from aredis_om import HashModel, Field, Migrator
from aredis_om.model.model import NotFoundError


class User(HashModel):
    """
    A user model.
    """

    wallet = 0
    bank = 0

    inventory = json.dumps({})
    stats = json.dumps(
        {
            "health": 100,
            "combat": 25,
            "defense": 10,
            "speed": 10,
            "luck": 0,
            "crit_chance": 30,
            "crit_damage": 10,
        }
    )


class Auction(HashModel):
    """
    An auction model.
    """

    owner: str
    item: str = Field(index=True)
    amount: int
    price: int


async def get(id: typing.Union[str, int]):
    from .cache import cache

    id = str(id)
    if id in cache:
        return cache[await User.get(id)]

    try:
        return await User.get(id)
    except NotFoundError:
        return None


async def inv_add(user, item, amount):
    inv = json.loads(user.inventory)
    
    if item in inv:
        inv[item] += amount
    else:
        inv[item] = amount

    user.inventory = json.dumps(inv)
    await user.save()


async def create(id: typing.Union[str, int]):
    id = str(id)
    g = await get(id)
    if g is not None:
        return g
    
    u = User()
    u.pk = id
    return await u.save()


async def get_auction(item: str):
    try:
        return Auction.find(item in Auction.item).all()
    except NotFoundError:
        return None


async def initialize():
    migrator = Migrator()
    await migrator.run()
