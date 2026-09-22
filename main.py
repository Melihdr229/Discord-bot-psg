import os
import random
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive
import google.generativeai as genai

# Gemini Yapay Zeka Yapılandırması (En güncel ve hatasız model: gemini-1.5-flash)
if os.environ.get("GEMINI_API_KEY"):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

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
    "🧠 **Günün Bilgi Sorusu:** Türkiye'nin başkenti Ankara hangi yılda resmi başkent ilan edilmiştir? (Cevap için tahminleri alalım!)",
    "🧠 **Günün Bilgi Sorusu:** Dünyanın en uzun nehri hangisidir?",
    "🧠 **Günün Bilgi Sorusu:** Osmanlı İmparatorluğu'nun kurucusu Osman Bey'in babası kimdir?",
    "🧠 **Günün Bilgi Sorusu:** Ay'a ilk ayak basan astronot kimdir ve hangi yıl gerçekleşmiştir?",
    "🧠 **Günün Bilgi Sorusu:** Kilometre cinsinden Güneş'e en yakın olan gezegen hangisidir?",
    "🧠 **Günün Bilgi Sorusu:** İstiklal Marşı'mızın şairi Mehmet Akif Ersoy'un şiirlerini topladığı kitabının adı nedir?"
]

mesaj_sayaci = 0

@bot.event
async def on_ready():
    print(f"Giriş yapıldı! Bot aktif: {bot.user}")

# --- 1. OTOMATİK ROL VE HOŞ GELDİN MESAJI ---
@bot.event
async def on_member_join(member):
    verilecek_rol_adi = sunucu_autorol.get(member.guild.id, "Üye")
    rol = discord.utils.get(member.guild.roles, name=verilecek_rol_adi)
    
    if rol:
        try:
            await member.add_roles(rol)
        except:
            pass

    channel = discord.utils.get(member.guild.text_channels, name="hosgeldin") or discord.utils.get(member.guild.text_channels, name="giriş")
    if channel:
        embed = discord.Embed(
            title="🎉 Sunucuya Biri Katıldı!",
            description=f"Aramıza hoş geldin, {member.mention}! Otomatik olarak **{verilecek_rol_adi}** rolün verildi. Seninle beraber **{member.guild.member_count}** kişi olduk.",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

# --- 2. SES KANALI OLUŞTURUCU VE SES SEVİYESİ (XP) TAKİBİ ---
@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

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

# --- 3. MESAJ KONTROLÜ (YAPAY ZEKA VE DİĞERLERİ) ---
@bot.event
async def on_message(message):
    global mesaj_sayaci
    if message.author.bot:
        return

    # Prefix olmadan Yapay Zeka Yanıtı (Bot etiketlendiğinde çalışır)
    if bot.user.mentioned_in(message):
        if gemini_model:
            soru = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
            if soru:
                async with message.channel.typing():
                    try:
                        response = gemini_model.generate_content(soru)
                        await message.reply(response.text)
                    except Exception as e:
                        await message.reply(f"🤖 Yapay zeka yanıt üretirken bir hata oluştu: `{e}`")
        else:
            await message.reply("⚠️ Yapay zeka API anahtarı (GEMINI_API_KEY) Render Environment Variables kısmında tanımlanmamış!")
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
                await message.channel.send(f"🎉 Tebrikler {message.author.mention}, doğru tahmin ettin! Sayı **{gizli_sayi}** idi. 🏆")
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

# --- 4. YARDIM MENÜSÜ ---
@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(
        title="🤖 Ultimate Mega Bot Komutları",
        description="Sunucuyu yönetmek ve eğlenmek için kullanabileceğin tüm komutlar:\n*(Not: Yapay zeka ile konuşmak için botu etiketleyerek mesaj atabilirsin!)*",
        color=discord.Color.green()
    )
    embed.add_field(name="!yardim", value="Komutları listeler.", inline=False)
    embed.add_field(name="@Bot <soru>", value="Prefix gerektirmeden yapay zeka ile sohbet edersin.", inline=False)
    embed.add_field(name="!ses-seviye [@kullanıcı]", value="Ses kanalı aktiflik puanını gösterir.", inline=False)
    embed.add_field(name="!kadro-kur [pozisyon]", value="20 TL bütçe ile 100+ oyunculuk kadro kurma oyunu!", inline=False)
    embed.add_field(name="!rastgele-kadro", value="Şansına rastgele bir 11 kurar.", inline=False)
    embed.add_field(name="!rol-mesaj @Rol <mesaj>", value="Roldeki herkese özelden mesaj atar (Yönetici).", inline=False)
    embed.add_field(name="!afk <sebep>", value="Uzakta modunu açar.", inline=False)
    embed.add_field(name="!öneri <mesaj>", value="Öneri gönderir.", inline=False)
    embed.add_field(name="!tahmin", value="Sayı tahmin oyunu başlatır.", inline=False)
    embed.add_field(name="!çekiliş <saniye> <ödül>", value="Çekiliş başlatır (Yönetici).", inline=False)
    embed.add_field(name="!profil [@kullanıcı]", value="Kullanıcı profili gösterir.", inline=False)
    embed.add_field(name="!kullanıcı-bilgi [@kullanıcı]", value="Detaylı kullanıcı bilgisi gösterir.", inline=False)
    embed.add_field(name="!seviye", value="Yazışma Seviye ve XP gösterir.", inline=False)
    embed.add_field(name="!sunucu-bilgi", value="Sunucu bilgilerini gösterir.", inline=False)
    embed.add_field(name="!zar / !yazıtura", value="Eğlence komutları.", inline=False)
    embed.add_field(name="!uyarı @kullanıcı <sebep>", value="Kullanıcıyı uyarır (Yönetici).", inline=False)
    embed.add_field(name="!uyarılar @kullanıcı", value="Uyarı geçmişini gösterir (Yönetici).", inline=False)
    embed.add_field(name="!uyarı-sil @kullanıcı", value="Kullanıcının son uyarısını siler (Yönetici).", inline=False)
    embed.add_field(name="!yavaşmod <saniye>", value="Kanalı yavaş moda alır (Yönetici).", inline=False)
    embed.add_field(name="!kilit / !aç", value="Kanalı kilitler/açar (Yönetici).", inline=False)
    embed.add_field(name="!autorol <rol>", value="Otomatik rol ayarlar (Yönetici).", inline=False)
    embed.add_field(name="!kanal-aç <isim>", value="Kanal açar (Yönetici).", inline=False)
    embed.add_field(name="!sil <sayı>", value="Mesaj siler (Yönetici).", inline=False)
    embed.add_field(name="!kick / !ban", value="Üye atar/yasaklar (Yönetici).", inline=False)
    await ctx.send(embed=embed)

# --- 5. SES SEVİYESİ / AKTİFLİK KOMUTU ---
@bot.command(name="ses-seviye")
async def ses_seviye(ctx, member: discord.Member = None):
    member = member or ctx.author
    puan = ses_xp.get(member.id, 0)
    embed = discord.Embed(title=f"🔊 {member.name} - Ses Seviyesi Bilgisi", color=discord.Color.blue())
    embed.add_field(name="Toplam Ses Puanı", value=f"{puan} Puan", inline=True)
    await ctx.send(embed=embed)

# --- 6. 100+ OYUNCULUK KADRO KURMA & YARDIMCI KOMUTLAR ---
@bot.command(name="kadro-kur")
async def kadro_kur(ctx, kategori: str = "genel"):
    kategori = kategori.lower()
    if kategori == "kaleci":
        embed = discord.Embed(title="🧤 Kaleci Havuzu", description="**9 TL:** Neuer, Courtois\n**7 TL:** Alisson, Ter Stegen\n**5 TL:** Ederson, Oblak\n**3 TL:** Maignan, Emiliano Martinez\n**1 TL:** Onana, Altay Bayındır", color=discord.Color.blue())
    elif kategori == "defans":
        embed = discord.Embed(title="🛡️ Defans Havuzu", description="**9 TL:** Sergio Ramos, Maldini\n**7 TL:** Van Dijk, Ruben Dias, Saliba\n**5 TL:** Marquinhos, Araujo, Rudiger\n**3 TL:** Hakimi, Theo Hernandez, Alexander-Arnold\n**1 TL:** Maguire, Eric Garcia, Holding", color=discord.Color.red())
    elif kategori == "orta":
        embed = discord.Embed(title="🎯 Orta Saha Havuzu", description="**9 TL:** Zidane, Iniesta, Modric\n**7 TL:** De Bruyne, Bellingham, Rodri, Kroos\n**5 TL:** Valverde, Odegaard, Bruno Fernandes\n**3 TL:** Pedri, Gavi, Barella\n**1 TL:** Antony, McTominay, Fred", color=discord.Color.gold())
    elif kategori == "forvet":
        embed = discord.Embed(title="⚡ Forvet Havuzu", description="**9 TL:** Messi, Ronaldo, Pelé, Maradona, Mbappé, Haaland\n**7 TL:** Neymar, Vinicius Jr, Salah, Harry Kane\n**5 TL:** Son, Lewandowski, Griezmann, Lautaro\n**3 TL:** Osimhen, Rafael Leao, Rashford\n**1 TL:** Werner, Michy Batshuayi, Serdar Dursun", color=discord.Color.purple())
    else:
        embed = discord.Embed(title="⚽ 20 TL ile Dev Futbolcu Alışverişi", description="Toplam **20 TL** bütçen var! Pozisyonuna göre detaylı havuz için:\n• `!kadro-kur kaleci`\n• `!kadro-kur defans`\n• `!kadro-kur orta`\n• `!kadro-kur forvet`", color=discord.Color.dark_green())
    embed.set_footer(text=f"{ctx.author.name} için kadro havuzu yüklendi 💸")
    await ctx.send(embed=embed)

@bot.command(name="rastgele-kadro")
async def rastgele_kadro(ctx):
    yildizlar = ["Messi", "Ronaldo", "Mbappé", "Haaland", "De Bruyne", "Bellingham", "Vinicius Jr", "Salah", "Modric", "Van Dijk", "Neuer"]
    secilenler = random.sample(yildizlar, 5)
    embed = discord.Embed(title="🎲 Rastgele 5'li Joker Kadro", description=f"1. **{secilenler[0]}**\n2. **{secilenler[1]}**\n3. **{secilenler[2]}**\n4. **{secilenler[3]}**\n5. **{secilenler[4]}**", color=discord.Color.orange())
    await ctx.send(embed=embed)

@bot.command(name="kadro-bilgi")
async def kadro_bilgi(ctx):
    await ctx.send("ℹ️ **Kadro Kurma Rehberi:** 20 TL sanal bütçeyle en iyi takımı kurmaya çalışırsın.")

# --- 7. DİĞER YÖNETİM VE EĞLENCE KOMUTLARI ---
@bot.command(name="rol-mesaj")
@commands.has_permissions(administrator=True)
async def rol_mesaj(ctx, role: discord.Role, *, mesaj: str):
    await ctx.message.delete()
    basarili = 0
    basarisiz = 0
    for member in role.members:
        if not member.bot:
            try:
                await member.send(f"📩 **{ctx.guild.name}** sunucusundan bir duyuru ({ctx.author.name}):\n\n{mesaj}")
                basarili += 1
            except:
                basarisiz += 1
    await ctx.send(f"✅ **{role.name}** roldeki **{basarili}** kişiye özelden mesaj gönderildi.", delete_after=10)

@bot.command(name="afk")
async def afk(ctx, *, sebep="Belirtilmedi"):
    afk_kullanicilar[ctx.author.id] = sebep
    await ctx.send(f"💤 {ctx.author.mention}, başarıyla AFK moduna geçtin. Sebep: *{sebep}*")

@bot.command(name="çekiliş")
@commands.has_permissions(administrator=True)
async def cekilis(ctx, sure: int, *, odul: str):
    await ctx.message.delete()
    embed = discord.Embed(title="🎉 ÇEKİLİŞ VAR! 🎉", description=f"Ödül: **{odul}**\nKatılmak için 🎉 emojisine tıkla!", color=discord.Color.magenta())
    embed.set_footer(text=f"Süre: {sure} saniye")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await asyncio.sleep(sure)
    yeni_msg = await ctx.channel.fetch_message(msg.id)
    reaction = discord.utils.get(yeni_msg.reactions, emoji="🎉")
    users = [u for u in await reaction.users().flatten() if not u.bot] if reaction else []
    if users:
        kazanan = random.choice(users)
        await ctx.send(f"🎊 Tebrikler {kazanan.mention}! **{odul}** çekilişini kazandın! 🏆")
    else:
        await ctx.send("❌ Çekilişe yeterli katılım olmadığından kazanan seçilemedi.")

@bot.command(name="uyarı")
@commands.has_permissions(manage_messages=True)
async def uyari(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    uyari_veritabani.setdefault(member.id, []).append(sebep)
    await ctx.send(f"⚠️ **{member.name}** uyaraldı! Sebep: {sebep} (Toplam: {len(uyari_veritabani[member.id])})")

@bot.command(name="uyarılar")
@commands.has_permissions(manage_messages=True)
async def uyarilar(ctx, member: discord.Member):
    sebepler = uyari_veritabani.get(member.id, [])
    if sebepler:
        liste = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sebepler)])
        await ctx.send(embed=discord.Embed(title=f"⚠️ {member.name} - Uyarı Geçmişi", description=liste, color=discord.Color.red()))
    else:
        await ctx.send(f"✅ {member.name} adlı kullanıcının hiç uyarısı yok.")

@bot.command(name="uyarı-sil")
@commands.has_permissions(manage_messages=True)
async def uyari_sil(ctx, member: discord.Member):
    if member.id in uyari_veritabani and uyari_veritabani[member.id]:
        uyari_veritabani[member.id].pop()
        await ctx.send(f"✅ **{member.name}** kullanıcısının son uyarısı silindi.")
    else:
        await ctx.send(f"❌ Silinebilecek uyarı yok.")

@bot.command(name="yavaşmod")
@commands.has_permissions(manage_channels=True)
async def yavasmod(ctx, saniye: int):
    await ctx.channel.slowmode_delay(saniye)
    await ctx.send(f"⏱️ Yavaş mod **{saniye}** saniye olarak ayarlandı.")

@bot.command(name="kullanıcı-bilgi")
async def kullanici_bilgi(ctx, member: discord.Member = None):
    member = member or ctx.author
    roller = ", ".join([r.mention for r in member.roles[1:]]) or "Rolü yok"
    embed = discord.Embed(title=f"🔍 Detaylı Bilgi: {member.name}", color=discord.Color.dark_blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Sunucuya Katılım", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Roller", value=roller, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="öneri")
async def oneri(ctx, *, metin: str):
    await ctx.message.delete()
    kanal = discord.utils.get(ctx.guild.text_channels, name="öneri") or ctx.channel
    gonderilen = await kanal.send(embed=discord.Embed(title="💡 Yeni Öneri", description=metin, color=discord.Color.gold()))
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
    await ctx.send("🎮 **Sayı Tahmin Oyunu Başladı!** 1-100 arası sayı tuttum, yaz bakalım!")

@bot.command(name="autorol")
@commands.has_permissions(administrator=True)
async def autorol(ctx, *, rol_adi: str):
    if discord.utils.get(ctx.guild.roles, name=rol_adi):
        sunucu_autorol[ctx.guild.id] = rol_adi
        await ctx.send(f"✅ Otomarol **{rol_adi}** olarak ayarlandı.")
    else:
        await ctx.send(f"❌ Böyle bir rol bulunamadı.")

@bot.command(name="seviye")
async def seviye(ctx, member: discord.Member = None):
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    await ctx.send(embed=discord.Embed(title=f"⭐ {member.name} - Mesaj Seviyesi", description=f"Toplam XP: {xp} (Seviye: {xp // 100})", color=discord.Color.orange()))

@bot.command(name="sunucu-bilgi")
async def sunucu_bilgi(ctx):
    g = ctx.guild
    await ctx.send(embed=discord.Embed(title=f"📊 {g.name}", description=f"Sahip: {g.owner}\nÜye: {g.member_count}\nKanal: {len(g.channels)}", color=discord.Color.purple()))

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
    await ctx.send(f"👢 {member.name} atıldı. Sebep: {sebep}")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} yasaklandı. Sebep: {sebep}")

@bot.command(name="kanal-aç")
@commands.has_permissions(manage_channels=True)
async def kanal_ac(ctx, *, kanal_adi: str):
    await ctx.guild.create_text_channel(kanal_adi)
    await ctx.send(f"✅ {kanal_adi} kanalı açıldı!")

@bot.command(name="sil")
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int = 5):
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🧹 Son {miktar} mesaj silindi!", delete_after=5)

keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
