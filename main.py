import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

# Botun prefix işareti (!) ve tüm izinleri (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Giriş yapıldı! Bot aktif: {bot.user}")

# --- 1. PROFİL / KULLANICI BİLGİSİ ---
@bot.command(name="profil")
async def profil(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.name} - Kullanıcı Profili", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Kullanıcı Adı", value=str(member), inline=True)
    embed.add_field(name="Sunucuya Katılım", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Roller", value=", ".join([role.name for role in member.roles[1:]])participation if len(member.roles) > 1 else "Rolü yok", inline=False)
    await ctx.send(embed=embed)

# --- 2. KANAL OLUŞTURMA ---
@bot.command(name="kanal-aç")
@commands.has_permissions(manage_channels=True)
async def kanal_ac(ctx, *, kanal_adi: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=kanal_adi)
    if not existing_channel:
        await guild.create_text_channel(kanal_adi)
        await ctx.send(f"✅ **{kanal_adi}** adlı metin kanalı başarıyla oluşturuldu!")
    else:
        await ctx.send(f"⚠️ Bu isimde bir kanal zaten mevcut.")

# --- 3. KANAL SİLME ---
@bot.command(name="kanal-sil")
@commands.has_permissions(manage_channels=True)
async def kanal_sil(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    await channel.delete()

# --- 4. MESAJ TEMİZLEME (SINIRLAMA/SİLME) ---
@bot.command(name="sil")
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int = 5):
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🧹 Son {miktar} mesaj temizlendi!", delete_after=5)

# --- 5. LOG SİSTEMİ (MESAJ SİLME / DÜZENLEME TAKİBİ) ---
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    # Sunucuda 'log' isimli bir kanal varsa oraya raporlar
    log_channel = discord.utils.get(message.guild.text_channels, name="log")
    if log_channel:
        embed = discord.Embed(title="🗑️ Mesaj Silindi", color=discord.Color.red())
        embed.add_field(name="Kullanıcı", value=message.author.mention, inline=True)
        embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
        embed.add_field(name="Silinen Mesaj", value=message.content or "İçerik yok (Fotoğraf/Dosya olabilir)", inline=False)
        await log_channel.send(embed=embed)

# 7/24 açık kalması için web sunucusunu başlat ve botu çalıştır
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
