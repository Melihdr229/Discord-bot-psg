import os
import random
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True  

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Hafıza Depoları
user_xp = {}         
ses_xp = {}          
ses_takip = {}       
sunucu_autorol = {}  
kilitli_odalilar = set()  
aktif_tahminler = {}  
afk_kullanicilar = {}  
uyari_veritabani = {}  

OTO_CEVAPLAR = {
    "sa": "as",
    "selamun aleyküm": "aleyküm selam"
}

YASAKLI_KELIMELER = [
    "allahı sikeyim", "kuranı sikeyim", "allahı", "kuranı", 
    "küfür1", "küfür2"
]

GUNCEL_SORULAR = [
    "🧠 **Günün Bilgi Sorusu:** Hangi futbol takımı, Şampiyonlar Ligi'ni en çok kazanan kulüptür?",
    "🧠 **Günün Bilgi Sorusu:** Türkiye'nin yüz ölçümü bakımından en büyük şehri hangisidir?",
    "🧠 **Günün Bilgi Sorusu:** Bilgisayar biliminin babası olarak bilinen ve yapay zekanın temellerini atan ünlü İngiliz matematikçi kimdir?",
    "🧠 **Günün Bilgi Sorusu:** 'Grand Line' hangi ünlü anime serisinde yer alan okyanus yoludur?",
    "🧠 **Günün Bilgi Sorusu:** Güneş sistemindeki en büyük gezegen hangisidir?",
    "🧠 **Günün Bilgi Sorusu:** İstanbul hangi yıl feth edilmiştir?"
]

mesaj_sayaci = 0

@bot.event
async def on_ready():
    print(f"Giriş yapıldı! Bot aktif: {bot.user}")

# --- 1. OTOMATİK ROL VE HOŞ GELDİN MESAJI (GÜNCELLENDİ) ---
@bot.event
async def on_member_join(member):
    # Önce !autorol-ayarla ile ayarlananı arar, yoksa doğrudan "Üye" rolünü arar
    verilecek_rol_adi = sunucu_autorol.get(member.guild.id, "Üye")
    rol = discord.utils.get(member.guild.roles, name=verilecek_rol_adi)
    
    # Eğer "Üye" de bulunamazsa sunucudaki ilk normal rolü alternatif olarak aratabiliriz
    if not rol:
        rol = discord.utils.get(member.guild.roles, name="Üye") or discord.utils.get(member.guild.roles, name="uye")

    if rol:
        try:
            await member.add_roles(rol)
        except Exception as e:
            print(f"Otorol verme hatası: {e}")

    channel = discord.utils.get(member.guild.text_channels, name="hosgeldin") or discord.utils.get(member.guild.text_channels, name="giriş")
    if channel:
        embed = discord.Embed(
            title="🎉 Sunucuya Biri Katıldı!",
            description=f"Aramıza hoş geldin, {member.mention}! Otomatik olarak rolün verildi. Seninle beraber **{member.guild.member_count}** kişi olduk.",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

# --- 2. GELİŞMİŞ MODERATÖR LOG SİSTEMİ ---
@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return
    log_kanal = discord.utils.get(message.guild.text_channels, name="mod-log")
    if log_kanal:
        embed = discord.Embed(
            title="🗑️ Mesaj Silindi",
            description=f"**Kanal:** {message.channel.mention}\n**Yazan:** {message.author.mention}\n**İçerik:** `{message.content or 'İçerik yok'}`",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Kullanıcı ID: {message.author.id}")
        await log_kanal.send(embed=embed)

@bot.event
async def on_member_remove(member):
    if not member.guild:
        return
    log_kanal = discord.utils.get(member.guild.text_channels, name="mod-log")
    if log_kanal:
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id:
                    embed = discord.Embed(
                        title="👢 Üye Kicklendi (Atıldı)",
                        description=f"**Atılan:** {member.mention} ({member.name})\n**Atan Yetkili:** {entry.user.mention}\n**Sebep:** {entry.reason or 'Belirtilmedi'}",
                        color=discord.Color.orange()
                    )
                    await log_kanal.send(embed=embed)
                    return
        except:
            pass

@bot.event
async def on_member_ban(guild, user):
    log_kanal = discord.utils.get(guild.text_channels, name="mod-log")
    if log_kanal:
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    embed = discord.Embed(
                        title="🔨 Üye Banlandı (Yasaklandı)",
                        description=f"**Yasaklanan:** {user.mention} ({user.name})\n**Yasaklayan Yetkili:** {entry.user.mention}\n**Sebep:** {entry.reason or 'Belirtilmedi'}",
                        color=discord.Color.dark_red()
                    )
                    await log_kanal.send(embed=embed)
                    return
        except:
            pass

# --- 3. SES KANALI VE BAĞLANTI KESİLME LOGLARI ---
@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    log_kanal = discord.utils.get(member.guild.text_channels, name="mod-log")

    if log_kanal:
        if before.channel is not None and after.channel is None:
            durum_mesaji = f"🔇 **{member.mention}** adlı kullanıcı **{before.channel.name}** ses kanalından ayrıldı."
            await asyncio.sleep(0.5)
            try:
                async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_move):
                    if entry.target.id == member.id:
                        durum_mesaji = f"🔌 **{member.mention}**, **{entry.user.mention}** tarafından **{before.channel.name}** kanalından atıldı/bağlantısı kesildi!"
                        break
            except:
                pass
            await log_kanal.send(embed=discord.Embed(title="🔌 Ses Bağlantısı Kesildi", description=durum_mesaji, color=discord.Color.purple()))

        elif before.channel is None and after.channel is not None:
            await log_kanal.send(embed=discord.Embed(title="🔊 Ses Kanalına Girdi", description=f"{member.mention} kullanıcısı **{after.channel.name}** kanalına katıldı.", color=discord.Color.blue()))
        elif before.channel != after.channel and before.channel is not None and after.channel is not None:
            await log_kanal.send(embed=discord.Embed(title="🔀 Ses Kanalı Değiştirdi", description=f"{member.mention} kullanıcısı **{before.channel.name}** kanalından **{after.channel.name}** kanalına geçiş yaptı.", color=discord.Color.gold()))

    if after.channel and after.channel.name == "➕ Oda Oluştur":
        guild = member.guild
        category = after.channel.category
        oda_adi = f"🔊 | {member.name}'in Odası"
        yeni_kanal = await guild.create_voice_channel(oda_adi, category=category)
        await member.move_to(yeni_kanal)
        
        def check(b, a):
            return len(yeni_kanal.members) == 0
        
        try:
            await bot.wait_for('voice_state_update', check=check, timeout=86400)
            if len(yeni_kanal.members) == 0:
                if yeni_kanal.id in kilitli_odalilar:
                    kilitli_odalilar.remove(yeni_kanal.id)
                await yeni_kanal.delete()
        except:
            pass

    import time
    simdiki_zaman = time.time()

    if before.channel is None and after.channel is not None:
        if not after.self_mute and not after.self_deaf:
            ses_takip[member.id] = simdiki_zaman

    elif before.channel is not None and after.channel is None:
        if member.id in ses_takip:
            gecen_sure = simdiki_zaman - ses_takip[member.id]
            dakika = int(gecen_sure // 60)
            if dakika > 0:
                kazanilan_ses_xp = dakika * random.randint(10, 20)
                ses_xp[member.id] = ses_xp.get(member.id, 0) + kazanilan_ses_xp
            del ses_takip[member.id]

# --- 4. MESAJ KONTROLÜ VE KÜFÜR FİLTRESİ ---
@bot.event
async def on_message(message):
    global mesaj_sayaci
    if message.author.bot:
        return

    mesaj_metni = message.content.lower().strip()
    if mesaj_metni in OTO_CEVAPLAR:
        await message.channel.send(OTO_CEVAPLAR[mesaj_metni])

    if message.mentions:
        for user in message.mentions:
            if user.id in afk_kullanicilar:
                sebep = afk_kullanicilar[user.id]
                await message.channel.send(f"💤 **{user.name}** şu an uzakta (AFK). Sebep: *{sebep}*")

    if message.author.id in afk_kullanicilar:
        del afk_kullanicilar[message.author.id]
        try:
            await message.channel.send(f"👋 Hoş geldin {message.author.mention}, AFK modundan çıktın!", delete_after=5)
        except:
            pass

    if message.channel.id in aktif_tahminler:
        try:
            tahmin = int(message.content)
            gizli_sayi = aktif_tahminler[message.channel.id]
            if tahmin == gizli_sayi:
                await message.channel.send(f"🎉 Helal olsun {message.author.mention}, doğru tahmin ettin! Sayı **{gizli_sayi}** idi. 🏆")
                del aktif_tahminler[message.channel.id]
            elif tahmin < gizli_sayi:
                await message.add_reaction("⬆️")
            else:
                await message.add_reaction("⬇️")
        except ValueError:
            pass

    for kelime in YASAKLI_KELIMELER:
        if kelime in mesaj_metni:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda bu tarz küfür ve hakaretlerin kullanılmasına kesinlikle izin verilmiyor!", delete_after=5)
                return
            except:
                pass

    user_id = message.author.id
    user_xp[user_id] = user_xp.get(user_id, 0) + random.randint(5, 15)

    mesaj_sayaci += 1
    if mesaj_sayaci >= 15:
        mesaj_sayaci = 0
        secilen_soru = random.choice(GUNCEL_SORULAR)
        await message.channel.send(secilen_soru)

    await bot.process_commands(message)

# --- 5. YARDIM MENÜSÜ ---
@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(
        title="🤖 Ultimate Mega Bot Komutları",
        description="Sunucuyu yönetmek ve eğlenmek için kullanabileceğin tüm komutlar:",
        color=discord.Color.green()
    )
    embed.add_field(name="!yardim", value="Komutları listeler.", inline=False)
    embed.add_field(name="!git <ses kanalı>", value="Boşsa direkt gider, doluysa odadakilerin ✅ onayından sonra seni içeri alır.", inline=False)
    embed.add_field(name="!oda-kapat / !oda-aç", value="Özel ses odasını kilitler/açar.", inline=False)
    embed.add_field(name="!sayaç", value="Sunucu üye hedefini gösterir.", inline=False)
    embed.add_field(name="!autorol-ayarla <rol>", value="Oto-rolü ayarlar (Yönetici).", inline=False)
    embed.add_field(name="!ses-seviye [@kullanıcı]", value="Ses aktiflik puanını gösterir.", inline=False)
    embed.add_field(name="!kadro-kur [pozisyon]", value="20 TL bütçeli futbol kadro oyunu.", inline=False)
    embed.add_field(name="!rastgele-kadro", value="Rastgele 11 kurar.", inline=False)
    embed.add_field(name="!rol-mesaj @Rol <mesaj>", value="Roldeki herkese DM atar (Yönetici).", inline=False)
    embed.add_field(name="!afk <sebep>", value="Uzakta moduna geçiş.", inline=False)
    embed.add_field(name="!öneri <mesaj>", value="Öneri gönderir.", inline=False)
    embed.add_field(name="!tahmin", value="Sayı tahmin oyunu.", inline=False)
    embed.add_field(name="!çekiliş <saniye> <ödül>", value="Çekiliş başlatır (Yönetici).", inline=False)
    embed.add_field(name="!profil / !kullanıcı-bilgi", value="Kullanıcı profili ve detayları.", inline=False)
    embed.add_field(name="!sunucu-bilgi", value="Sunucu bilgileri.", inline=False)
    embed.add_field(name="!zar / !yazıtura", value="Eğlence komutları.", inline=False)
    embed.add_field(name="!uyarı / !uyarılar / !uyarı-sil", value="Uyarı yönetim sistemi.", inline=False)
    embed.add_field(name="!yavaşmod <saniye>", value="Kanalı yavaş moda alır (Yönetici).", inline=False)
    embed.add_field(name="!kilit / !aç", value="Kanalı kilitler/açar (Yönetici).", inline=False)
    embed.add_field(name="!kanal-aç <isim>", value="Kanal açar (Yönetici).", inline=False)
    embed.add_field(name="!sil <sayı>", value="Mesaj siler (Yönetici).", inline=False)
    embed.add_field(name="!kick / !ban", value="Üye atar/yasaklar (Yönetici).", inline=False)
    await ctx.send(embed=embed)

# --- 6. SES KANALINA GİTME VE EMOJİ ONAY SİSTEMİ (!git) ---
@bot.command(name="git")
async def git(ctx, *, kanal_adi: str):
    hedef_kanal = discord.utils.get(ctx.guild.voice_channels, name=kanal_adi)
    
    if not hedef_kanal:
        await ctx.send(f"❌ '{kanal_adi}' adında bir ses kanalı bulunamadı!")
        return

    hedef_uye = ctx.message.mentions[0] if ctx.message.mentions else ctx.author

    if not hedef_uye.voice:
        await ctx.send(f"❌ {hedef_uye.mention} herhangi bir ses kanalında değil!")
        return

    if len(hedef_kanal.members) == 0:
        try:
            await hedef_uye.move_to(hedef_kanal)
            await ctx.send(f"✅ {hedef_uye.mention} boş olan **{hedef_kanal.name}** kanalına taşındı!")
        except Exception as e:
            await ctx.send(f"⚠️ Taşıma hatası: `{e}`")
        return

    embed = discord.Embed(
        title="🚪 Odaya Giriş Talebi",
        description=f"**{hedef_uye.name}**, **{hedef_kanal.name}** odasına girmek istiyor!\nOdadakilerden biri onaylamak için ✅ emojisine tıklasın.",
        color=discord.Color.orange()
    )
    talep_mesaji = await ctx.send(embed=embed)
    await talep_mesaji.add_reaction("✅")

    def check(reaction, user):
        return not user.bot and str(reaction.emoji) == "✅" and user in hedef_kanal.members

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        await hedef_uye.move_to(hedef_kanal)
        await ctx.send(f"✅ **{user.name}** onay verdi ve {hedef_uye.mention}, **{hedef_kanal.name}** kanalına alındı!")
    except asyncio.TimeoutError:
        await ctx.send(f"⏱️ Süre doldu, **{hedef_kanal.name}** odasından kimse onay vermedi.")

# --- 7. ÖZEL ODA VE SAYAÇ KOMUTLARI ---
@bot.command(name="oda-kapat")
async def oda_kapat(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        kanal = ctx.author.voice.channel
        await kanal.set_permissions(ctx.guild.default_role, connect=False)
        kilitli_odalilar.add(kanal.id)
        await ctx.send(f"🔒 **{kanal.name}** odası dışarıdan gelenlere kapatıldı!")
    else:
        await ctx.send("❌ Önce kendi ses odana girmelisin!")

@bot.command(name="oda-aç")
async def oda_ac_komut(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        kanal = ctx.author.voice.channel
        await kanal.set_permissions(ctx.guild.default_role, connect=True)
        if kanal.id in kilitli_odalilar:
            kilitli_odalilar.remove(kanal.id)
        await ctx.send(f"🔓 **{kanal.name}** odası yeniden herkese açıldı!")
    else:
        await ctx.send("❌ Önce kendi ses odana girmelisin!")

@bot.command(name="sayaç")
async def sayac(ctx):
    g = ctx.guild
    uye_sayisi = g.member_count
    hedef = 100 
    kalan = max(0, hedef - uye_sayisi)
    embed = discord.Embed(
        title="📊 Sunucu Sayaç & Hedef Durumu",
        description=f"👥 **Toplam Üye:** {uye_sayisi}\n🎯 **Hedef Üye:** {hedef}\n⏳ **Hedefe Kalan:** {kalan} kişi",
        color=discord.Color.teal()
    )
    await ctx.send(embed=embed)

@bot.command(name="autorol-ayarla")
@commands.has_permissions(administrator=True)
async def autorol_ayarla(ctx, *, rol_adi: str):
    bulunan_rol = discord.utils.get(ctx.guild.roles, name=rol_adi)
    if bulunan_rol:
        sunucu_autorol[ctx.guild.id] = rol_adi
        await ctx.send(f"✅ Yeni gelenler için otomatik verilecek rol **{rol_adi}** olarak güncellendi!")
    else:
        await ctx.send(f"❌ '{rol_adi}' adında bir rol bulunamadı.")

# --- 8. DİĞER KOMUTLAR ---
@bot.command(name="ses-seviye")
async def ses_seviye(ctx, member: discord.Member = None):
    member = member or ctx.author
    puan = ses_xp.get(member.id, 0)
    await ctx.send(embed=discord.Embed(title=f"🔊 {member.name} - Ses Puanı", description=f"{puan} Puan", color=discord.Color.blue()))

@bot.command(name="kadro-kur")
async def kadro_kur(ctx, kategori: str = "genel"):
    kategori = kategori.lower()
    if kategori == "kaleci":
        desc = "**9 TL:** Neuer, Buffon, Courtois\n**1 TL:** Altay, Uğurcan"
    elif kategori == "defans":
        desc = "**9 TL:** Maldini, Ramos\n**1 TL:** Maguire, Çağlar"
    elif kategori == "orta":
        desc = "**9 TL:** Zidane, Iniesta, Modric\n**1 TL:** İsmail Yüksek"
    elif kategori == "forvet":
        desc = "**9 TL:** Messi, Ronaldo, Pelé\n**1 TL:** Cenk Tosun"
    else:
        desc = "20 TL bütçen var! Pozisyonlar: `!kadro-kur kaleci/defans/orta/forvet`"
    await ctx.send(embed=discord.Embed(title="⚽ Futbolcu Havuzu", description=desc, color=discord.Color.dark_green()))

@bot.command(name="rastgele-kadro")
async def rastgele_kadro(ctx):
    yildizlar = ["Messi", "Ronaldo (R9)", "Pelé", "Maradona", "Zidane", "Iniesta"]
    secilenler = random.sample(yildizlar, min(5, len(yildizlar)))
    await ctx.send(embed=discord.Embed(title="🎲 Rastgele Kadro", description="\n".join([f"• {oyuncu}" for oyuncu in secilenler]), color=discord.Color.orange()))

@bot.command(name="rol-mesaj")
@commands.has_permissions(administrator=True)
async def rol_mesaj(ctx, role: discord.Role, *, mesaj: str):
    await ctx.message.delete()
    sayac = 0
    for member in role.members:
        if not member.bot:
            try:
                await member.send(f"📩 **{ctx.guild.name}** duyurusu:\n\n{mesaj}")
                sayac += 1
            except:
                pass
    await ctx.send(f"✅ {sayac} kişiye özelden mesaj atıldı.", delete_after=10)

@bot.command(name="afk")
async def afk(ctx, *, sebep="Belirtilmedi"):
    afk_kullanicilar[ctx.author.id] = sebep
    await ctx.send(f"💤 {ctx.author.mention} AFK moduna geçti. Sebep: *{sebep}*")

@bot.command(name="çekiliş")
@commands.has_permissions(administrator=True)
async def cekilis(ctx, sure: int, *, odul: str):
    await ctx.message.delete()
    embed = discord.Embed(title="🎉 ÇEKİLİŞ!", description=f"Ödül: **{odul}**\nKatılmak için 🎉 emojisine tıkla!", color=discord.Color.magenta())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await asyncio.sleep(sure)
    yeni_msg = await ctx.channel.fetch_message(msg.id)
    reaction = discord.utils.get(yeni_msg.reactions, emoji="🎉")
    users = [u for u in await reaction.users().flatten() if not u.bot] if reaction else []
    if users:
        kazanan = random.choice(users)
        await ctx.send(f"🎊 Tebrikler {kazanan.mention}! **{odul}** kazandın!")
    else:
        await ctx.send("❌ Yeterli katılım olmadı.")

@bot.command(name="uyarı")
@commands.has_permissions(manage_messages=True)
async def uyari(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    uyari_veritabani.setdefault(member.id, []).append(sebep)
    await ctx.send(f"⚠️ {member.mention} uyarıldı. Sebep: {sebep}")

@bot.command(name="uyarılar")
@commands.has_permissions(manage_messages=True)
async def uyarilar(ctx, member: discord.Member):
    sebepler = uyari_veritabani.get(member.id, [])
    liste = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sebepler)]) if sebepler else "Temiz."
    await ctx.send(embed=discord.Embed(title=f"⚠️ {member.name} Uyarıları", description=liste, color=discord.Color.red()))

@bot.command(name="uyarı-sil")
@commands.has_permissions(manage_messages=True)
async def uyari_sil(ctx, member: discord.Member):
    if member.id in uyari_veritabani and uyari_veritabani[member.id]:
        uyari_veritabani[member.id].pop()
        await ctx.send(f"✅ {member.name} son uyarısı silindi.")
    else:
        await ctx.send("❌ Uyarı yok.")

@bot.command(name="yavaşmod")
@commands.has_permissions(manage_channels=True)
async def yavasmod(ctx, saniye: int):
    await ctx.channel.slowmode_delay(saniye)
    await ctx.send(f"⏱️ Yavaş mod {saniye} saniye.")

@bot.command(name="kullanıcı-bilgi")
async def kullanici_bilgi(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🔍 {member.name}", description=f"ID: {member.id}\nKatılım: {member.joined_at.strftime('%d/%m/%Y')}", color=discord.Color.dark_blue())
    await ctx.send(embed=embed)

@bot.command(name="öneri")
async def oneri(ctx, *, metin: str):
    await ctx.message.delete()
    kanal = discord.utils.get(ctx.guild.text_channels, name="öneri") or ctx.channel
    gonderilen = await kanal.send(embed=discord.Embed(title="💡 Öneri", description=metin, color=discord.Color.gold()))
    await gonderilen.add_reaction("👍")
    await gonderilen.add_reaction("👎")

@bot.command(name="kilit")
@commands.has_permissions(manage_channels=True)
async def kilit(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal kilitlendi.")

@bot.command(name="aç")
@commands.has_permissions(manage_channels=True)
async def ac(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kanal açıldı.")

@bot.command(name="tahmin")
async def tahmin(ctx):
    aktif_tahminler[ctx.channel.id] = random.randint(1, 100)
    await ctx.send("🎮 Sayı tahmin oyunu başladı (1-100)!")

@bot.command(name="seviye")
async def seviye(ctx, member: discord.Member = None):
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    await ctx.send(embed=discord.Embed(title=f"⭐ {member.name} Seviye", description=f"XP: {xp} (Seviye: {xp // 100})", color=discord.Color.orange()))

@bot.command(name="sunucu-bilgi")
async def sunucu_bilgi(ctx):
    g = ctx.guild
    await ctx.send(embed=discord.Embed(title=f"📊 {g.name}", description=f"Sahip: {g.owner}\nÜye: {g.member_count}", color=discord.Color.purple()))

@bot.command(name="profil")
async def profil(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(embed=discord.Embed(title=f"👤 {member.name}", description=f"Katılım: {member.joined_at.strftime('%d/%m/%Y')}", color=discord.Color.blue()))

@bot.command(name="zar")
async def zar(ctx):
    await ctx.send(f"🎲 Zar: **{random.randint(1, 6)}**")

@bot.command(name="yazıtura")
async def yazitura(ctx):
    await ctx.send(f"🪙 Sonuç: **{random.choice(['Yazı', 'Tura'])}**")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} atıldı.")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} yasaklandı.")

@bot.command(name="kanal-aç")
@commands.has_permissions(manage_channels=True)
async def kanal_ac(ctx, *, kanal_adi: str):
    await ctx.guild.create_text_channel(kanal_adi)
    await ctx.send(f"✅ {kanal_adi} açıldı!")

@bot.command(name="sil")
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int = 5):
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🧹 {miktar} mesaj silindi!", delete_after=5)

keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
