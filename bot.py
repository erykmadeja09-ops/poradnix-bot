import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from flask import Flask
from threading import Thread

# --- MINI SERWER WWW DLA RENDERA ---
# To sprawia, że Render "widzi" bota jako działającą stronę
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# -----------------------------------

# POBIERANIE TOKENU Z USTAWIEŃ RENDERA (Environment Variable)
TOKEN = os.environ.get("TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class VerificationView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        # Twoje ID roli
        role_id = 1511454049579434106
        role = interaction.guild.get_role(role_id)
        
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Pomyślnie przeszedłeś weryfikację! Witamy na serwerze.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Bot odpalony jako {bot.user}")
    bot.add_view(VerificationView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_weryfikacja(ctx):
    await ctx.message.delete()
    
    embed = discord.Embed(
        title="🛡️ WERYFIKACJA SERWERA PORADNIX",
        description="Aby uzyskać pełen dostęp do serwera i wszystkich kanałów, kliknij poniższy zielony przycisk.",
        color=discord.Color.green()
    )
    embed.set_footer(text="System weryfikacji bot.py")
    
    await ctx.send(embed=embed, view=VerificationView())

# Startujemy
keep_alive()
bot.run(TOKEN)