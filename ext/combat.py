# dont look at my code

import random
import json

import discord

from .colors import Colors
from .db import create, User, inv_add


class Item(discord.ui.Button):
    def __init__(self, item, user, enemy, enemytype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.enemy = enemy
        self.enemytype = enemytype
        self.item = item
        self.items = {
            "apple": ("health", 10),
        }

    async def callback(self, interaction: discord.Interaction):
        self.user[self.items[self.item][0]] += self.items[self.item][1]
        inv_add(self.user, "apple", -1)
        embed = discord.Embed(
            title=f"{interaction.user.name} is fighting a {self.enemytype}!",
            color=Colors.rand()
        )
        embed.add_field(name="Your health", value=f'\❤ {round(self.user["health"])}')
        embed.add_field(name="Enemy health", value=f'\❤ {round(self.enemy["health"])}')
        await interaction.message.edit(embed=embed, view=CombatView(self.user, self.enemy, self.enemytype))
        await interaction.response.defer()


class UseView(discord.ui.View):
    def __init__(self, user: User, usable: list, enemy: dict, enemytype: str):
        super().__init__()
        self.user = user
        self.usable = usable
        self.enemy = enemy
        self.enemytype = enemytype

        if "apple" in self.usable:
            self.add_item(Item("apple", self.user, self.enemy, self.enemytype, label="Apple", style=discord.ButtonStyle.green))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{interaction.user.name} is fighting a {self.enemytype}!",
            color=Colors.rand()
        )
        embed.add_field(name="Your health", value=f'\❤ {round(self.user["health"])}')
        embed.add_field(name="Enemy health", value=f'\❤ {round(self.enemy["health"])}')
        await interaction.message.edit(embed=embed, view=CombatView(self.user, self.enemy, self.enemytype))
        await interaction.response.defer()


class CombatView(discord.ui.View):
    def __init__(self, user: User, enemy: dict, type: str):
        super().__init__()
        self.user = json.loads(user.stats)
        self.userstats = user
        self.enemy = enemy
        self.enemytype = type

    @discord.ui.button(label="Attack", style=discord.ButtonStyle.red)
    async def attack(self, button: discord.ui.Button, interaction: discord.Interaction):
        enemy = self.enemy

        atkdmg = round(self.user["combat"] * random.uniform(0.8, 1.2))

        rand = random.randint(0, 100)
        if rand <= self.user["crit_chance"]:
            print('crit')
            atkdmg += round(atkdmg * (self.user["crit_damage"] / 100) * random.uniform(0.8, 1.2))

        if enemy["speed"] <= random.randint(0, 100):
            enemy["health"] -= atkdmg
        else:
            enemy["health"] -= atkdmg / random.uniform(1.2, 1.8)

        atkdmg = round(self.enemy["combat"] * random.uniform(0.8, 1.2))
        if self.user["speed"] <= random.randint(0, 100):
            self.user["health"] -= atkdmg
        else:
            self.user["health"] -= atkdmg / random.uniform(1.2, 1.8)

        embed = discord.Embed(
            title=f"{interaction.user.name} is fighting a {self.enemytype}!",
            color=Colors.rand()
        )

        if round(enemy["health"]) <= 0:
            money_gained = round(self.user["combat"] * 3 * random.uniform(0.8, 1.2))
            embed.description = f"{interaction.user.name} won the fight! You gained {money_gained} coins!"
            await interaction.response.edit_message(embed=embed, view=None)
            await self.userstats.update(wallet=self.userstats.wallet + money_gained)
            if self.enemytype == "zombie":
                await inv_add(self.userstats, "rotten_flesh", random.randint(1, 3))
            elif self.enemytype == "skeleton":
                await inv_add(self.userstats, "bone", random.randint(1, 3))
            elif self.enemytype == "spider":
                await inv_add(self.userstats, "spider_eye", random.randint(1, 2))
                await inv_add(self.userstats, "string", random.randint(1, 2))
            self.stop()

        elif round(self.user["health"]) <= 0:
            money_lost = round(self.user["combat"] * 3 * random.uniform(0.8, 1.2))
            embed.description = f"{interaction.user.name} lost the fight! You lost {money_lost} coins!"
            await interaction.response.edit_message(embed=embed, view=None)
            await self.userstats.update(wallet=self.userstats.wallet - money_lost)
            self.stop()

        else:
            embed.add_field(name="Your health", value=f'\❤ {round(self.user["health"])}')
            embed.add_field(name="Enemy health", value=f'\❤ {round(enemy["health"])}')

            await interaction.message.edit(embed=embed, view=self)
            await interaction.response.defer()

    @discord.ui.button(label="Run", style=discord.ButtonStyle.grey)
    async def run(self, button: discord.ui.Button, interaction: discord.Interaction):
        coins_lost = random.randint(1, 10)
        embed = discord.Embed(
            title=f"{interaction.user.name} ran away from the {self.enemytype}! You lost {coins_lost} coins!",
            color=Colors.rand()
        )
        await self.userstats.update(wallet=self.userstats.wallet - coins_lost)
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="Use", style=discord.ButtonStyle.green)
    async def use(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = await create(interaction.user.id)
        inventory = json.loads(user.inventory)
        usable = ("apple", )
        embed = discord.Embed(
            title="Use item",
            description="Select the item you want to use",
        )

        user_usable = [item for item in json.loads(user.inventory) if item in usable]
        if len(user_usable) == 0:
            embed.description = "You don't have any usable items!"
            view = None
        else:
            view = UseView(self.user, user_usable, self.enemy, self.enemytype)

        for item in user_usable:
            embed.add_field(name=item.replace("_", " ").title(), value=f'Amount: {inventory[item]}')
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="instantkill", style=discord.ButtonStyle.green)
    async def instantkill(self, button: discord.ui.Button, interaction: discord.Interaction):

        embed = discord.Embed(
            title=f"{interaction.user.name} is fighting a {self.enemytype}!",
            color=Colors.rand()
        )

        money_gained = round(self.user["combat"] * 3 * random.uniform(0.8, 1.2))
        embed.description = f"{interaction.user.name} won the fight! You gained {money_gained} coins!"
        await interaction.response.edit_message(embed=embed, view=None)
        await self.userstats.update(wallet=self.userstats.wallet + money_gained)
        if self.enemytype == "zombie":
            await inv_add(self.userstats, "rotten_flesh", random.randint(1, 3))
        elif self.enemytype == "skeleton":
            await inv_add(self.userstats, "bone", random.randint(1, 3))
        elif self.enemytype == "spider":
            await inv_add(self.userstats, "spider_eye", random.randint(1, 2))
            await inv_add(self.userstats, "string", random.randint(1, 2))
        self.stop()

        await interaction.message.edit(embed=embed)


class Combat(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(guild_ids=[942318419011833896])
    async def stats(self, ctx: discord.ApplicationContext):
        u = await create(ctx.user.id)
        stats = json.loads(u.stats)

        embed = discord.Embed(
            title=f"{ctx.user.name}'s stats",
            color=Colors.rand()
        )
        embed.add_field(name="Health", value=f'\❤ {stats["health"]}')
        embed.add_field(name="Combat", value=f'\⚔ {stats["combat"]}')
        embed.add_field(name="Defense", value=f'\❈ {stats["defense"]}')
        embed.add_field(name="Speed", value=f'\✦ {stats["speed"]}')
        embed.add_field(name="Luck", value=f'\✯ {stats["luck"]}')
        embed.add_field(name="Crit Chance", value=f'\☣ {stats["crit_chance"]}')
        embed.add_field(name="Crit Damage", value=f'\☠ {stats["crit_damage"]}')

        embed.set_footer(text=f"Requested by {ctx.user.name}", icon_url=ctx.user.avatar)

        await ctx.respond(embed=embed)

    @discord.slash_command(guild_ids=[942318419011833896])
    async def fight(self, ctx: discord.ApplicationContext):
        u = await create(ctx.user.id)
        stats = json.loads(u.stats)

        enemy_type = random.choice(("zombie", "skeleton", "spider"))

        enemy = {
            "health": stats["health"],
            "combat": stats["combat"] * random.uniform(1, 1.3),
            "defense": stats["defense"] - 5,
            "speed": stats["speed"],
        }

        embed = discord.Embed(
            title=f"{ctx.user.name} is fighting a {enemy_type}!",
            color=Colors.rand()
        )

        embed.add_field(name="Your health", value=f'\❤ {stats["health"]}')
        embed.add_field(name="Enemy health", value=f'\❤ {enemy["health"]}')

        await ctx.respond(embed=embed, view=CombatView(u, enemy, enemy_type))

        
def setup(bot):
    bot.add_cog(Combat(bot))
