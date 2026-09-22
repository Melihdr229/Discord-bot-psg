import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Giriş yapıldı! Bot aktif: {bot.user}")

@bot.command(name="profil")
async def profil(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.name} - Kullanıcı Profili", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Kullanıcı Adı", value=str(member), inline=True)
    embed.add_field(name="Sunucuya Katılım", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="kanal-aç")
@commands.has_permissions(manage_channels=True)
async def kanal_ac(ctx, *, kanal_adi: str):
    await ctx.guild.create_text_channel(kanal_adi)
    await ctx.send(f"✅ **{kanal_adi}** adlı kanal oluşturuldu!")

@bot.command(name="sil")
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int = 5):
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🧹 Son {miktar} mesaj temizlendi!", delete_after=5)

keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
