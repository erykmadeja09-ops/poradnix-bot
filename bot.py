import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import os
from flask import Flask
from threading import Thread

# --- MINI SERWER WWW (DO TRZYMANIA BOTA W CHMURZE) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running 24/7!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
keep_alive()

TOKEN = os.environ.get("TOKEN")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SYSTEM WERYFIKACJI ---
class VerificationView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, custom_id="verify_btn")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(1511454049579434106) # Upewnij się, że to ID jest poprawne
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Jesteś zweryfikowany!", ephemeral=True)

# --- SYSTEM TICKETÓW ---
class TicketModal(Modal, title="Otwórz zgłoszenie"):
    problem = TextInput(label="W czym możemy pomóc?", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, name="TICKETY")
        channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=category)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await channel.send(f"{interaction.user.mention} pisze: {self.problem.value}")
        await interaction.response.send_message(f"Utworzono: {channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.blurple, custom_id="ticket_btn")
    async def ticket_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(TicketModal())

@bot.event
async def on_ready():
    print(f"✅ Bot działa jako {bot.user}")
    bot.add_view(VerificationView())
    bot.add_view(TicketView())

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="powitania")
    if channel: await channel.send(f"Witaj, {member.mention}!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_weryfikacja(ctx):
    await ctx.send("Kliknij poniżej, aby uzyskać dostęp:", view=VerificationView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    await ctx.send("Potrzebujesz pomocy? Otwórz ticket:", view=TicketView())

bot.run(TOKEN)