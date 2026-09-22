import os
import random
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Basit Seviye Sistemi için Hafıza Deposu {user_id: xp}
user_xp = {}

# Küfür / Yasaklı Kelime Listesi (İstediğin kelimeyi ekleyebilirsin)
YASAKLI_KELIMELER = ["küfür1", "küfür2", "zararlıkelime"]

@bot.event
async def on_ready():
    print(f"Giriş yapıldı! Bot aktif: {bot.user}")

# --- 1. OTOMATİK ROL VE HOŞ GELDİN MESAJI ---
@bot.event
async def on_member_join(member):
    # Yeni üyeye otomatik "Üye" rolü verme (Sunucunda "Üye" adında bir rol olmalı)
    rol = discord.utils.get(member.guild.roles, name="Üye")
    if rol:
        try:
            await member.add_roles(rol)
        except:
            pass

    # Hoş geldin kanalı duyurusu
    channel = discord.utils.get(member.guild.text_channels, name="hosgeldin") or discord.utils.get(member.guild.text_channels, name="giriş")
    if channel:
        embed = discord.Embed(
            title="🎉 Sunucuya Biri Katıldı!",
            description=f"Aramıza hoş geldin, {member.mention}! Otomatik olarak **Üye** rolün verildi. Seninle beraber **{member.guild.member_count}** kişi olduk.",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

# --- 2. KÜFÜR FİLTRESİ VE XP (SEVİYE) SİSTEMİ ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Küfür / Yasaklı Kelime Kontrolü
    mesaj_icerik = message.content.lower()
    for kelime in YASAKLI_KELIMELER:
        if kelime in mesaj_icerik:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda bu kelimenin kullanılmasına izin verilmiyor!", delete_after=5)
                return
            except:
                pass

    # Seviye ve XP Kazanma (Her mesaj başına rastgele 5-15 XP)
    user_id = message.author.id
    user_xp[user_id] = user_xp.get(user_id, 0) + random.randint(5, 15)

    await bot.process_commands(message)

# --- 3. YARDIM MENÜSÜ ---
@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(
        title="🤖 Tam Donanımlı Bot Komutları",
        description="Sunucuyu yönetmek ve eğlenmek için kullanabileceğin tüm komutlar:",
        color=discord.Color.green()
    )
    embed.add_field(name="!yardim", value="Komutları listeler.", inline=False)
    embed.add_field(name="!profil [@kullanıcı]", value="Kullanıcı profili gösterir.", inline=False)
    embed.add_field(name="!seviye", value="Mevcut mesaj XP puanını ve seviyeni gösterir.", inline=False)
    embed.add_field(name="!sunucu-bilgi", value="Sunucu hakkında detaylı bilgi verir.", inline=False)
    embed.add_field(name="!zar", value="1 ile 6 arasında zar atar.", inline=False)
    embed.add_field(name="!yazıtura", value="Yazı tura atar.", inline=False)
    embed.add_field(name="!kanal-aç <isim>", value="Yeni metin kanalı açar (Yönetici).", inline=False)
    embed.add_field(name="!sil <sayı>", value="Mesaj temizler (Yönetici).", inline=False)
    embed.add_field(name="!kick @kullanıcı", value="Üyeyi sunucudan atar (Yönetici).", inline=False)
    embed.add_field(name="!ban @kullanıcı", value="Üyeyi sunucudan yasaklar (Yönetici).", inline=False)
    await ctx.send(embed=embed)

# --- 4. SEVİYE SİSTEMİ KOMUTU ---
@bot.command(name="seviye")
async def seviye(ctx, member: discord.Member = None):
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    seviye_puani = xp // 100  her 100 XP 1 seviye
    
    embed = discord.Embed(title=f"⭐ {member.name} - Seviye Bilgisi", color=discord.Color.orange())
    embed.add_field(name="Toplam XP", value=f"{xp} XP", inline=True)
    embed.add_field(name="Mevcut Seviye", value=f"Seviye {seviye_puani}", inline=True)
    await ctx.send(embed=embed)

# --- 5. SUNUCU BİLGİ ---
@bot.command(name="sunucu-bilgi")
async def sunucu_bilgi(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name} - Sunucu Bilgileri", color=discord.Color.purple())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Sunucu Sahibi", value=guild.owner, inline=True)
    embed.add_field(name="Üye Sayısı", value=guild.member_count, inline=True)
    embed.add_field(name="Kuruluş Tarihi", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Kanal Sayısı", value=len(guild.channels), inline=True)
    await ctx.send(embed=embed)

# --- 6. KULLANICI PROFİLİ ---
@bot.command(name="profil")
async def profil(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.name} - Kullanıcı Profili", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Kullanıcı Adı", value=str(member), inline=True)
    embed.add_field(name="Sunucuya Katılım", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

# --- 7. EĞLENCE: ZAR VE YAZI-TURA ---
@bot.command(name="zar")
async def zar(ctx):
    sayi = random.randint(1, 6)
    await ctx.send(f"🎲 Zar atıldı ve gelen sayı: **{sayi}**!")

@bot.command(name="yazıtura")
async def yazitura(ctx):
    sonuc = random.choice(["Yazı 🪙", "Tura 🪙"])
    await ctx.send(f"🪙 Para havaya atıldı ve sonuç: **{sonuc}**!")

# --- 8. MODERASYON: KICK, BAN, KANAL AÇ, SİL ---
@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 **{member.name}** sunucudan atıldı. Sebep: {sebep}")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 **{member.name}** sunucudan yasaklandı. Sebep: {sebep}")

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
