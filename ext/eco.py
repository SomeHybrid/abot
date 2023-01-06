import json

from discord.ext import pages
import discord

from .colors import Colors
from .db import create, inv_add, get


class AmountModal(discord.ui.Modal):
    def __init__(self, items, item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = items
        self.item = item

        self.add_item(discord.ui.InputText(label="How much would you like to buy?"))

    async def callback(self, interaction: discord.Interaction):
        price = self.items[self.item]["price"]
        amount = int(self.children[0].value)
        total = price * amount
        user = await get(interaction.user.id)
        if user.wallet < total:
            await interaction.response.send_message("You don't have enough money!", ephemeral=True)
            return
        else:
            await user.update(wallet=user.wallet - total)
            await inv_add(user, self.item, amount)
            await interaction.response.send_message(f"You bought {amount} {self.item} for {total} coins!", ephemeral=True)


class AmountView(discord.ui.View):
    def __init__(self, items, item):
        super().__init__()
        self.items = items
        self.item = item

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelled!", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(AmountModal(self.items, self.item, title="How much would you like to buy?"))


class BuyModal(discord.ui.Modal):
    def __init__(self, items, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = items

        self.add_item(discord.ui.InputText(label="What would you like to buy?"))

    async def callback(self, interaction: discord.Interaction):
        item = self.children[0].value.replace(" ", "_").lower()
        if item not in self.items:
            await interaction.response.send_message("That item doesn't exist.", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Are you sure you want to buy this?", view=AmountView(self.items, item))


class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.items = {
            "apple": {"price": 10, "description": "An apple. When consumed, it restores 15 health."},
        }
    @discord.ui.button(label="List", style=discord.ButtonStyle.gray)
    async def list(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Shop",
            color=Colors.rand()
        )
        for item in tuple(self.items.items()):
            embed.add_field(
                name=item[0].replace("_", " ").title(),
                value=f"{item[1]['description']}\nPrice: {item[1]['price']} coins",
            )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy", style=discord.ButtonStyle.green)
    async def buy(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(BuyModal(self.items, title="Buy"))


class OpenShop(discord.ui.View):
    @discord.ui.button(label="Shop", style=discord.ButtonStyle.green)
    async def npc_shop(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(
            "This is the default shop. You can buy items here.",
            view=ShopView()
        )


class Eco(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command()
    async def free_money(self, ctx: discord.ApplicationContext, amount: int):
        user = await create(ctx.user.id)
        await user.update(wallet=user.wallet + amount)
        await ctx.respond("You got free money!", ephemeral=True)

    @discord.slash_command()
    async def balance(self, ctx: discord.ApplicationContext):
        u = await create(ctx.user.id)

        wallet = u.wallet
        bank = u.bank

        embed = discord.Embed(
            title=f"{ctx.user.name}'s balance",
            description=f"Wallet: {wallet}\nBank: {bank}",
            color=Colors.rand()
        )
        embed.set_footer(text=f"Requested by {ctx.user.name}", icon_url=ctx.user.avatar)

        await ctx.respond(embed=embed)

    @discord.slash_command()
    async def deposit(self, ctx: discord.ApplicationContext, amount: int):
        u = await create(ctx.user.id)
        if amount > u.wallet:
            embed = discord.Embed(
                title="Error",
                description="You don't have enough money in your wallet to deposit that much.",
                color=Colors.ERROR
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        u.wallet -= amount
        u.bank += amount

        await u.save()

        await ctx.respond(f"Deposited {amount} into your bank account!", ephemeral=True)

    @discord.slash_command()
    async def withdraw(self, ctx: discord.ApplicationContext, amount: int):
        u = await create(ctx.user.id)
        if amount > u.bank:
            await ctx.respond("You don't have enough money to withdraw that much!", ephemeral=True)
            return

        u.wallet += amount
        u.bank -= amount

        await u.save()

        await ctx.respond(f"Withdrew {amount} from your bank account!", ephemeral=True)

    @discord.slash_command()
    async def free_stuff(self, ctx: discord.ApplicationContext, item: str, amount: int):
        u = await create(ctx.user.id)
        
        await inv_add(u, item, amount)

        await ctx.respond(f"You got {amount} stuff!", ephemeral=True)

    @discord.slash_command()
    async def inventory(self, ctx: discord.ApplicationContext): 
        u = await create(ctx.user.id)
        inventory = json.loads(u.inventory)

        items = list(inventory.items())
        for index, item in enumerate(items):
            item = list(item)
            item[0] = item[0].replace("_", " ").title()
            item = tuple(item)
            items[index] = item

        desc = [f"{x[0]}: {x[1]}" for x in items]
        i = 0
        i1 = 9
        page = []
        for _ in range(len(desc) // 10 + 1):
            page.append(
                discord.Embed(
                    title=f"{ctx.user.name}'s inventory",
                    description='\n'.join(desc[i:i1]),
                    color=Colors.rand()
                )
            )
            i += 10
            i1 += 10

        paginator = pages.Paginator(pages=page)
        paginator.remove_button("first")
        paginator.remove_button("last")
        await paginator.respond(ctx.interaction)

    @discord.slash_command()
    async def shop(self, ctx: discord.ApplicationContext):
        await create(ctx.user.id)
        await ctx.respond("Which shop would you like to open?", view=OpenShop(), ephemeral=True)


def setup(bot):
    bot.add_cog(Eco(bot))
