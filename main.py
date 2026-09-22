import os
import random
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Hafıza Depoları
user_xp = {}
sunucu_autorol = {}  
aktif_tahminler = {}  
afk_kullanicilar = {}  
uyari_veritabani = {}  
aktif_kadro_oyunlari = {} # {user_id: [secilen_oyuncular, kalan_butce]}

# Güncellenmiş Oto-Cevap Sözlüğü (Agah ve Reap kaldırıldı)
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

# --- 2. SES KANALI OLUŞTURUCU (ÖZEL ODA) ---
@bot.event
async def on_voice_state_update(member, before, after):
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

# --- 3. MESAJ KONTROLÜ ---
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
        description="Sunucuyu yönetmek ve eğlenmek için kullanabileceğin tüm komutlar:",
        color=discord.Color.green()
    )
    embed.add_field(name="!yardim", value="Komutları listeler.", inline=False)
    embed.add_field(name="!kadro-kur", value="20 TL bütçe ile efsane futbolcuları seçerek kadro kurma oyunu!", inline=False)
    embed.add_field(name="!rol-mesaj @Rol <mesaj>", value="Etiketlenen roldeki herkese özelden (DM) mesaj atar (Yönetici).", inline=False)
    embed.add_field(name="!afk <sebep>", value="Uzakta modunu açar.", inline=False)
    embed.add_field(name="!öneri <mesaj>", value="Öneri gönderir.", inline=False)
    embed.add_field(name="!tahmin", value="Sayı tahmin oyunu başlatır.", inline=False)
    embed.add_field(name="!çekiliş <saniye> <ödül>", value="Çekiliş başlatır (Yönetici).", inline=False)
    embed.add_field(name="!profil [@kullanıcı]", value="Kullanıcı profili gösterir.", inline=False)
    embed.add_field(name="!kullanıcı-bilgi [@kullanıcı]", value="Detaylı kullanıcı bilgisi gösterir.", inline=False)
    embed.add_field(name="!seviye", value="Seviye ve XP gösterir.", inline=False)
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

# --- 5. YENİ OYUN: 20 TL İLE KADRO KURMA ---
@bot.command(name="kadro-kur")
async def kadro_kur(ctx):
    embed = discord.Embed(
        title="⚽ 20 TL ile Futbolcu Seçme Oyunu!",
        description="Toplam **20 TL** bütçen var! Aşağıdaki havuzdan bütçene uygun oyuncuları seçerek kadonu oluştur.\n\n"
                    "**🌟 9 TL'lik Yıldızlar:**\n• Messi\n• Ronaldo\n\n"
                    "**⭐ 7 TL'lik Yıldızlar:**\n• Neymar\n• Mbappe\n• De Bruyne\n\n"
                    "**💎 5 TL'lik Oyuncular:**\n• Salah\n• Bellingham\n• Vinicius Jr\n\n"
                    "**⚡ 3 TL'lik Oyuncular:**\n• Modric\n• Kroos\n• Son\n\n"
                    "**🛠️ 1 TL'lik Jokerler:**\n• Antony\n• Maguire\n• Onana\n\n"
                    "Nasıl oynanır? Seçtiğin oyuncuları kağıda yazabilir veya arkadaşlarınla paylaşabilirsin! Kendi 11'ini kur ve eğlen!",
        color=discord.Color.dark_green()
    )
    embed.set_footer(text=f"{ctx.author.name} için bütçe: 20 TL 💸")
    await ctx.send(embed=embed)

# --- 6. ROLDEKİLERE ÖZELDEN (DM) MESAJ ATMA ---
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

    await ctx.send(f"✅ İşlem tamamlandı! **{role.name}** roldeki **{basarili}** kişiye özelden mesaj gönderildi. (Ulaşılamayan: {basarisiz})", delete_after=10)

# --- 7. AFK SİSTEMİ ---
@bot.command(name="afk")
async def afk(ctx, *, sebep="Belirtilmedi"):
    afk_kullanicilar[ctx.author.id] = sebep
    await ctx.send(f"💤 {ctx.author.mention}, başarıyla AFK moduna geçtin. Sebep: *{sebep}*")

# --- 8. ÇEKİLİŞ SİSTEMİ ---
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
    
    users = []
    async for user in reaction.users():
        if not user.bot:
            users.append(user)

    if users:
        kazanan = random.choice(users)
        await ctx.send(f"🎊 Tebrikler {kazanan.mention}! **{odul}** çekilişini kazandın! 🏆")
    else:
        await ctx.send("❌ Çekilişe yeterli katılım olmadığından kazanan seçilemedi.")

# --- 9. UYARI SİSTEMİ ---
@bot.command(name="uyarı")
@commands.has_permissions(manage_messages=True)
async def uyari(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if member.id not in uyari_veritabani:
        uyari_veritabani[member.id] = []
    uyari_veritabani[member.id].append(sebep)
    
    toplam_uyari = len(uyari_veritabani[member.id])
    await ctx.send(f"⚠️ **{member.name}** uyaraldı! Sebep: {sebep} (Toplam Uyarı: {toplam_uyari})")

@bot.command(name="uyarılar")
@commands.has_permissions(manage_messages=True)
async def uyarilar(ctx, member: discord.Member):
    sebepler = uyari_veritabani.get(member.id, [])
    if sebepler:
        liste = "\n".join([f"{i+1}. {sebep}" for i, sebep in enumerate(sebepler)])
        embed = discord.Embed(title=f"⚠️ {member.name} - Uyarı Geçmişi", description=liste, color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"✅ {member.name} adlı kullanıcının hiç uyarısı yok.")

@bot.command(name="uyarı-sil")
@commands.has_permissions(manage_messages=True)
async def uyari_sil(ctx, member: discord.Member):
    if member.id in uyari_veritabani and uyari_veritabani[member.id]:
        silinen = uyari_veritabani[member.id].pop()
        kalan = len(uyari_veritabani[member.id])
        await ctx.send(f"✅ **{member.name}** adlı kullanıcının son uyarısı silindi! (Kalan Uyarı: {kalan})")
    else:
        await ctx.send(f"❌ {member.name} adlı kullanıcının silinebilecek uyarısı yok.")

# --- 10. YAVAŞ MOD ---
@bot.command(name="yavaşmod")
@commands.has_permissions(manage_channels=True)
async def yavasmod(ctx, saniye: int):
    await ctx.channel.slowmode_delay(saniye)
    if saniye == 0:
        await ctx.send("⏱️ Bu kanaldaki yavaş mod kapatıldı.")
    else:
        await ctx.send(f"⏱️ Bu kanalın yavaş mod süresi **{saniye}** saniye olarak ayarlandı.")

# --- 11. KULLANICI BİLGİ ---
@bot.command(name="kullanıcı-bilgi")
async def kullanici_bilgi(ctx, member: discord.Member = None):
    member = member or ctx.author
    roller = [role.mention for role in member.roles[1:]]
    roller_str = ", ".join(roller) if roller else "Rolü yok"
    
    embed = discord.Embed(title=f"🔍 Detaylı Kullanıcı Bilgisi: {member.name}", color=discord.Color.dark_blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Kullanıcı ID", value=member.id, inline=True)
    embed.add_field(name="Sunucuya Katılım", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Discord'a Kayıt", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name=f"Roller ({len(member.roles)-1})", value=roller_str, inline=False)
    await ctx.send(embed=embed)

# --- 12. DİĞER KOMUTLAR ---
@bot.command(name="öneri")
async def oneri(ctx, *, metin: str):
    await ctx.message.delete()
    kanal = discord.utils.get(ctx.guild.text_channels, name="öneri") or discord.utils.get(ctx.guild.text_channels, name="öneriler")
    embed = discord.Embed(title="💡 Yeni Bir Öneri Var!", description=metin, color=discord.Color.gold())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    if kanal:
        gonderilen = await kanal.send(embed=embed)
        await gonderilen.add_reaction("👍")
        await gonderilen.add_reaction("👎")
        await ctx.send(f"✅ Öneriniz başarıyla **#{kanal.name}** kanalına iletildi!", delete_after=5)
    else:
        gonderilen = await ctx.send(embed=embed)
        await gonderilen.add_reaction("👍")
        await gonderilen.add_reaction("👎")

@bot.command(name="kilit")
@commands.has_permissions(manage_channels=True)
async def kilit(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Bu kanal kilitlendi.")

@bot.command(name="aç")
@commands.has_permissions(manage_channels=True)
async def ac(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Bu kanal tekrar açıldı.")

@bot.command(name="tahmin")
async def tahmin(ctx):
    gizli_sayi = random.randint(1, 100)
    aktif_tahminler[ctx.channel.id] = gizli_sayi
    await ctx.send("🎮 **Sayı Tahmin Oyunu Başladı!** 1 ile 100 arasında bir sayı tuttum. Tahminini sohbete yaz!")

@bot.command(name="autorol")
@commands.has_permissions(administrator=True)
async def autorol(ctx, *, rol_adi: str):
    rol = discord.utils.get(ctx.guild.roles, name=rol_adi)
    if not rol:
        await ctx.send(f"❌ Sunucuda **'{rol_adi}'** adında rol bulunamadı!")
        return
    sunucu_autorol[ctx.guild.id] = rol_adi
    await ctx.send(f"✅ Otomarol **{rol_adi}** olarak ayarlandı!")

@bot.command(name="seviye")
async def seviye(ctx, member: discord.Member = None):
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    seviye_puani = xp // 100
    embed = discord.Embed(title=f"⭐ {member.name} - Seviye Bilgisi", color=discord.Color.orange())
    embed.add_field(name="Toplam XP", value=f"{xp} XP", inline=True)
    embed.add_field(name="Mevcut Seviye", value=f"Seviye {seviye_puani}", inline=True)
    await ctx.send(embed=embed)

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

@bot.command(name="profil")
async def profil(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.name} - Kullanıcı Profili", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Kullanıcı Adı", value=str(member), inline=True)
    embed.add_field(name="Sunucuya Katılım", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="zar")
async def zar(ctx):
    sayi = random.randint(1, 6)
    await ctx.send(f"🎲 Zar: **{sayi}**")

@bot.command(name="yazıtura")
async def yazitura(ctx):
    sonuc = random.choice(["Yazı 🪙", "Tura 🪙"])
    await ctx.send(f"🪙 Sonuç: **{sonuc}**")

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
