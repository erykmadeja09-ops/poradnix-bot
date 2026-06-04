import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import os
from flask import Flask
from threading import Thread

# --- MINI SERWER WWW (DO UTRZYMANIA BOTA W CHMURZE) ---
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
        role = interaction.guild.get_role(1511454049579434106)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Jesteś zweryfikowany!", ephemeral=True)

# --- SYSTEM TICKETÓW ---
class TicketModal(Modal, title="Otwórz zgłoszenie"):
    problem = TextInput(label="W czym możemy pomóc?", style=discord.TextStyle.paragraph, placeholder="Opisz dokładnie swój problem...")
    async def on_submit(self, interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, name="TICKETY")
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        await channel.send(f"📩 **Zgłoszenie od {interaction.user.mention}**\n\n**Opis problemu:**\n{self.problem.value}\n\n*Administracja wkrótce odpowie.*")
        await interaction.response.send_message(f"Utworzono prywatny ticket: {channel.mention}", ephemeral=True)

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
    if channel: await channel.send(f"Witaj na serwerze, {member.mention}! Miło Cię widzieć.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_weryfikacja(ctx):
    embed = discord.Embed(
        title="🛡️ WERYFIKACJA SERWERA",
        description="Kliknij przycisk poniżej, aby uzyskać pełny dostęp do kanałów.",
        color=discord.Color.green()
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1509199635632095433/1511455274886500432/IMG_20260602_212851.png?ex=6a227e2b&is=6a212cab&hm=ddf7313862fd976be47de73dbd7bfdbaf08f3255330ad3ee9d3906a9b79d37b0&") # <-- TU WKLEJ LINK
    await ctx.send(embed=embed, view=VerificationView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    embed = discord.Embed(
        title="📩 WSPARCIE TECHNICZNE",
        description="Masz problem lub pytanie? Otwórz prywatny ticket, klikając przycisk poniżej.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Nasza administracja odpowie tak szybko jak to możliwe.")
    await ctx.send(embed=embed, view=TicketView())

bot.run(TOKEN)