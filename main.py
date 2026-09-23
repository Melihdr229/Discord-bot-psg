import os
import random
import asyncio
import discord
from discord.ext import commands, tasks
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
aktif_sorular = {}     
adam_asmaca_oyunlari = {} 
milyoner_oyunlari = {} 

OTO_CEVAPLAR = {
    "sa": "as",
    "selamun aleyküm": "aleyküm selam"
}

YASAKLI_KELIMELER = [
    "allahı sikeyim", "kuranı sikeyim", "allahı", "kuranı", 
    "küfür1", "küfür2"
]

# 3 Saatte Bir Sorulacak Zenginleştirilmiş Soru Havuzu
SAATLIK_BILGI_SORULARI = [
    {"soru": "Hangi futbol takımı, Şampiyonlar Ligi'ni en çok kazanan kulüptür?", "cevap": "real madrid"},
    {"soru": "Türkiye'nin yüz ölçümü bakımından en büyük şehri hangisidir?", "cevap": "konya"},
    {"soru": "Bilgisayar biliminin babası olarak bilinen ve yapay zekanın temellerini atan ünlü İngiliz matematikçi kimdir?", "cevap": "alan turing"},
    {"soru": "'Grand Line' hangi ünlü anime serisinde yer alan okyanus yoludur?", "cevap": "one piece"},
    {"soru": "Güneş sistemindeki en büyük gezegen hangisidir?", "cevap": "jüpiter"},
    {"soru": "İstanbul hangi yıl fethedilmiştir?", "cevap": "1453"},
    {"soru": "Periyodik tablonun ilk elementi ve evrende en bol bulunan kimyasal element hangisidir?", "cevap": "hidrojen"},
    {"soru": "Mona Lisa tablosunu çizen dünyaca ünlü İtalyan sanatçı kimdir?", "cevap": "leonardo da vinci"},
    {"soru": "Türkiye Cumhuriyeti hangi yıl kurulmuştur?", "cevap": "1923"},
    {"soru": "İnsan vücudundaki en büyük organ hangisidir?", "cevap": "deri"}
]

ASMACA_KATEGORILERI = {
    "lol": ["yasuo", "thresh", "lee sin", "lux", "ahri", "zed", "blitzcrank", "jinx", "kled", "warwick", "sett"],
    "valorant": ["jett", "reyna", "sage", "omen", "vandal", "phantom", "cypher", "sova", "spike", "bind", "ascent"],
    "minecraft": ["diamond", "creeper", "enderman", "obsidian", "nether", "redstone", "steve", "zombie", "pickaxe", "village"],
    "tarih": ["istanbul", "malazgirt", "osmanlı", "selçuklu", "cumhuriyet", "atatürk", "çanakkale", "fatih", "milli mücadele"],
    "matematik": ["türev", "integral", "geometri", "matris", "fonksiyon", "trigonometri", "logaritma", "olasılık", "parabol"]
}

MILYONER_VERITABANI = {
    "lol": [
        {"soru": "League of Legends oyununda 'Baron Nashor' katledildiğinde takıma hangi güçlendirme verilir?", "secenekler": ["A) Elixir of Iron", "B) Hand of Baron (Nashor Gücü)", "C) Aspect of the Dragon", "D) Crest of Cinders"], "cevap": "b"},
        {"soru": "Hangisi League of Legends evrelerinde bir orman kampı değildir?", "secenekler": ["A) Kurtlar", "B) Kayacıllar", "C) Ejderha", "D) Ejderha Yavrusu Yuvası"], "cevap": "d"},
        {"soru": "Blitzcrank karakterinin Q yeteneğinin adı nedir?", "secenekler": ["A) Rocket Grab", "B) Power Fist", "C) Static Field", "D) Overdrive"], "cevap": "a"},
        {"soru": "League of Legends'da dereceli sistemde Ustalık ile Şampiyonluk arasında yer alan lig hangisidir?", "secenekler": ["A) Elmas", "B) Üstadlık (Grandmaster)", "C) Zümrüt", "D) Demir"], "cevap": "b"},
        {"soru": "Faker kariyerindeki Dünya Şampiyonluklarını hangi takım altında kazanmıştır?", "secenekler": ["A) Gen.G", "B) T1 (SKT)", "C) Damwon", "D) KT Rolster"], "cevap": "b"}
    ],
    "valorant": [
        {"soru": "Valorant oyununda bomba olarak adlandırılan nesnenin resmi adı nedir?", "secenekler": ["A) C4", "B) Spike", "C) Bomb", "D) Dinamit"], "cevap": "b"},
        {"soru": "Ajan Brimstone hangi sınıfa (Role) aittir?", "secenekler": ["A) Düellocu", "B) Kontrol Uzmanı", "C) Öncü", "D) Gözcü"], "cevap": "b"},
        {"soru": "Hangisi Valorant'ın Öncü ajanlarından biri değildir?", "secenekler": ["A) Sova", "B) Skye", "C) Jett", "D) Fade"], "cevap": "c"},
        {"soru": "Valorant oyununda Spike'ı yerleştirmek normal şartlarda kaç saniye sürer?", "secenekler": ["A) 2 saniye", "B) 4 saniye", "C) 6 saniye", "D) 8 saniye"], "cevap": "b"},
        {"soru": "Valorant'ta en yüksek rekabetçi rütbe kademesi aşağıdakilerden hangisidir?", "secenekler": ["A) Yücelik", "B) Ölümsüzlük", "C) Radiant (Radyant)", "D) Elmas"], "cevap": "c"}
    ],
    "tarih": [
        {"soru": "İstanbul kaç yılında Fatih Sultan Mehmet tarafından fethedilmiştir?", "secenekler": ["A) 1299", "B) 1453", "C) 1517", "D) 1923"], "cevap": "b"},
        {"soru": "Türkiye Cumhuriyeti'nin ilk başbakanı kimdir?", "secenekler": ["A) İsmet İnönü", "B) Celâl Bayar", "C) Fevzi Çakmak", "D) Kazım Karabekir"], "cevap": "a"},
        {"soru": "Mustafa Kemal Atatürk'e 'Gazi' unvanı hangi savaştan sonra verilmiştir?", "secenekler": ["A) Çanakkale", "B) Sakarya Meydan Muharebesi", "C) Büyük Taarruz", "D) I. İnönü"], "cevap": "b"},
        {"soru": "Türk tarihinde 'Yurt Açan Savaş' olarak bilinen savaş hangisidir?", "secenekler": ["A) Miryokefalon", "B) Malazgirt", "C) Dandanakan", "D) Pasinler"], "cevap": "b"},
        {"soru": "Osmanlı İmparatorluğu'nun kuruluş yılı resmi olarak genellikle hangi yıl kabul edilir?", "secenekler": ["A) 1299", "B) 1302", "C) 1453", "D) 1071"], "cevap": "a"}
    ],
    "coğrafya": [
        {"soru": "Türkiye'nin yüz ölçümü bakımından en büyük ili hangisidir?", "secenekler": ["A) Ankara", "B) Sivas", "C) Konya", "D) Van"], "cevap": "c"},
        {"soru": "Türkiye'nin en yüksek dağı olan Ağrı Dağı hangi ilimiz sınırları içerisindedir?", "secenekler": ["A) Erzurum", "B) Van", "C) Iğdır / Ağrı", "D) Kars"], "cevap": "c"},
        {"soru": "Dünyanın en uzun nehirleri arasında gösterilen Nil Nehri hangi kıtada yer alır?", "secenekler": ["A) Asya", "B) Afrika", "C) Güney Amerika", "D) Avrupa"], "cevap": "b"},
        {"soru": "Hangi kıta yüz ölçümü bakımından dünyanın en küçük kıtasıdır?", "secenekler": ["A) Avrupa", "B) Antarktika", "C) Okyanusya (Avustralya)", "D) Güney Amerika"], "cevap": "c"},
        {"soru": "Dünyanın en derin okyanus çukuru olan 'Mariana Çukuru' hangi okyanusta yer alır?", "secenekler": ["A) Atlas", "B) Hint", "C) Pasifik (Büyük Okyanus)", "D) Arktik"], "cevap": "c"}
    ],
    "müzik": [
        {"soru": "Müzik notalarında 'sol anahtarı' portenin kaçıncı çizgisinden başlar?", "secenekler": ["A) 1. Çizgi", "B) 2. Çizgi", "C) 3. Çizgi", "D) 4. Çizgi"], "cevap": "b"},
        {"soru": "Aşağıdaki enstrümanlardan hangisi yaylı çalgılar grubuna girer?", "secenekler": ["A) Flüt", "B) Viyolonsel (Çello)", "C) Klarnet", "D) Trompet"], "cevap": "b"},
        {"soru": "Klasik batı müziğinde 'en yavaş' tempo terimi aşağıdakilerden hangisidir?", "secenekler": ["A) Allegro", "B) Andante", "C) Largo", "D) Presto"], "cevap": "c"},
        {"soru": "Türkiye'de 'Dönence' ve 'Aldırma Gönül' gibi unutulmaz eserlere imza atmış Anadolu Rock grubu hangisidir?", "secenekler": ["A) Duman", "B) Moğollar", "C) MFÖ", "D) Athena"], "cevap": "b"},
        {"soru": "Dünyaca ünlü 'Bohemian Rhapsody' şarkısı hangi efsanevi müzik grubuna aittir?", "secenekler": ["A) The Beatles", "B) Pink Floyd", "C) Queen", "D) Led Zeppelin"], "cevap": "c"}
    ],
    "futbol": [
        {"soru": "Bir futbol maçında kaleci dışında bir oyuncunun elle müdahale etmesi sonucu hakemin verdiği ceza atışı hangisidir?", "secenekler": ["A) Taç", "B) Korner", "C) Penaltı", "D) Endirekt Vuruş"], "cevap": "c"},
        {"soru": "Türkiye A Milli Futbol Takımı, FIFA Dünya Kupası tarihindeki en iyi derecesi olan üçüncülüğü hangi yılda elde etmiştir?", "secenekler": ["A) 1996", "B) 2002", "C) 2008", "D) 2020"], "cevap": "b"},
        {"soru": "Dünyada 'Kral' lakabıyla tanınan ve 3 kez Dünya Kupası kazanan efsanevi Brezilyalı futbolcu kimdir?", "secenekler": ["A) Maradona", "B) Pele", "C) Ronaldinho", "D) Ronaldo"], "cevap": "b"},
        {"soru": "Hangi futbol kulübü UEFA Şampiyonlar Ligi'ni tarihte en çok kazanan takımdır?", "secenekler": ["A) AC Milan", "B) Barcelona", "C) Real Madrid", "D) Bayern Munich"], "cevap": "c"},
        {"soru": "Resmi bir futbol maçında bir takımın sahada en az kaç oyuncusu kalırsa maç tatil edilir?", "secenekler": ["A) 5 oyuncu", "B) 6 oyuncu", "C) 7 oyuncu", "D) 9 oyuncu"], "cevap": "c"}
    ],
    "genel": [
        {"soru": "Güneş sistemindeki en büyük gezegen aşağıdakilerden hangisidir?", "secenekler": ["A) Satürn", "B) Jüpiter", "C) Neptün", "D) Mars"], "cevap": "b"},
        {"soru": "Mona Lisa tablosunu çizen dünyaca ünlü İtalyan sanatçı ve deha kimdir?", "secenekler": ["A) Donatello", "B) Leonardo da Vinci", "C) Michelangelo", "D) Raphael"], "cevap": "b"},
        {"soru": "Nobel Ödülleri hangi ülkede verilmektedir?", "secenekler": ["A) Almanya", "B) İsviçre", "C) İsveç", "D) Fransa"], "cevap": "c"},
        {"soru": "Periyodik tablonun ilk elementi ve evrende en bol bulunan kimyasal element hangisidir?", "secenekler": ["A) Helyum", "B) Oksijen", "C) Hidrojen", "D) Karbon"], "cevap": "c"},
        {"soru": "Dünyanın çevresini ilk kez dolaşan denizci kimdir?", "secenekler": ["A) Vasco da Gama", "B) Kristof Kolomb", "C) Juan Sebastián Elcano", "D) Amerigo Vespucci"], "cevap": "c"}
    ],
    "teknoloji": [
        {"soru": "İnternetin temelini oluşturan ve 'Ağların Ağı' anlamına gelen küresel sistemin kısaltması nedir?", "secenekler": ["A) WWW", "B) HTTP", "C) TCP", "D) LAN"], "cevap": "a"},
        {"soru": "Linux işletim sisteminin maskotu olan sevimli penguenin adı nedir?", "secenekler": ["A) Pingu", "B) Tux", "C) Linuxy", "D) Waddle"], "cevap": "b"},
        {"soru": "Yapay zeka alanında sıkça kullanılan 'ChatGPT' dil modelini geliştiren şirketin adı nedir?", "secenekler": ["A) Google", "B) Microsoft", "C) OpenAI", "D) Apple"], "cevap": "c"},
        {"soru": "Bilgisayarlarda veri depolamak için kullanılan ve elektrik kesildiğinde verileri silinmeyen kalıcı bellek hangisidir?", "secenekler": ["A) RAM", "B) Cache", "C) SSD / Sabit Disk", "D) Register"], "cevap": "c"},
        {"soru": "İlk programlanabilir elektronik bilgisayar olarak kabul edilen ve 1945 yılında geliştirilen devasa cihazın adı nedir?", "secenekler": ["A) ENIAC", "B) UNIVAC", "C) Altair 8800", "D) IBM 5100"], "cevap": "a"}
    ]
}

ODULLer = ["1.000 TL", "10.000 TL", "50.000 TL", "250.000 TL", "1.000.000 TL"]

@bot.event
async def on_ready():
    print(f"Giriş yapıldı! Bot aktif: {bot.user}")
    istatistik_guncelle.start()
    saatlik_soru_gonderici.start()

# --- 0. OTOMATİK İSTATİSTİK GÜNCELLEYİCİ LOOP ---
@tasks.loop(minutes=5)
async def istatistik_guncelle():
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            if "Toplam Üye:" in channel.name:
                try:
                    await channel.edit(name=f"📊 Toplam Üye: {guild.member_count}")
                except:
                    pass
            elif "Kullanıcı:" in channel.name:
                try:
                    uye_sayisi = len([m for m in guild.members if not m.bot])
                    await channel.edit(name=f"👤 Kullanıcı: {uye_sayisi}")
                except:
                    pass
            elif "Bot Sayısı:" in channel.name:
                try:
                    bot_sayisi = len([m for m in guild.members if m.bot])
                    await channel.edit(name=f"🤖 Bot Sayısı: {bot_sayisi}")
                except:
                    pass

# --- 0.1. HER 3 SAATTE BİR BİLGİ SORUSU GÖNDERİCİ ---
@tasks.loop(hours=3)
async def saatlik_soru_gonderici():
    secilen = random.choice(SAATLIK_BILGI_SORULARI)
    for guild in bot.guilds:
        hedef_kanal = discord.utils.get(guild.text_channels, name="sohbet") or discord.utils.get(guild.text_channels, name="genel")
        if not hedef_kanal:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    hedef_kanal = ch
                    break
        
        if hedef_kanal:
            aktif_sorular[hedef_kanal.id] = secilen["cevap"]
            try:
                await hedef_kanal.send(f"⏰ **3 Saatte Bir Gelen Bilgi Zamanı!**\n🧠 {secilen['soru']}\n*(Doğru cevabı yazarak 'Çok akıllısın maşallah!' övgüsünü kazan!)*")
            except:
                pass

@saatlik_soru_gonderici.before_loop
async def before_saatlik_soru():
    await bot.wait_until_ready()

# --- 1. OTOMATİK ROL VE HOŞ GELDİN MESAJI ---
@bot.event
async def on_member_join(member):
    verilecek_rol_adi = sunucu_autorol.get(member.guild.id, "Üye")
    rol = discord.utils.get(member.guild.roles, name=verilecek_rol_adi)
    
    if not rol:
        rol = discord.utils.get(member.guild.roles, name="Üye") or discord.utils.get(member.guild.roles, name="uye")

    if rol:
        try:
            await member.add_roles(rol)
        except:
            pass

    log_kanal = discord.utils.get(member.guild.text_channels, name="mod-log")
    if log_kanal:
        embed = discord.Embed(
            title="📥 Sunucuya Biri Katıldı",
            description=f"**Üye:** {member.mention} ({member.name})\n**Toplam Üye:** {member.guild.member_count}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await log_kanal.send(embed=embed)

    channel = discord.utils.get(member.guild.text_channels, name="hosgeldin") or discord.utils.get(member.guild.text_channels, name="giriş")
    if channel:
        embed = discord.Embed(
            title="🎉 Sunucuya Biri Katıldı!",
            description=f"Aramıza hoş geldin, {member.mention}! Otomatik olarak rolün verildi. Seninle beraber **{member.guild.member_count}** kişi olduk.",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

# --- 2. FULL KAPSAMLI MODERATÖR LOG SİSTEMİ ---
@bot.event
async def on_member_remove(member):
    if not member.guild:
        return
    log_kanal = discord.utils.get(member.guild.text_channels, name="mod-log")
    if not log_kanal:
        return

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

    embed = discord.Embed(
        title="📤 Sunucudan Ayrıldı",
        description=f"**Üye:** {member.mention} ({member.name})",
        color=discord.Color.dark_gray()
    )
    await log_kanal.send(embed=embed)

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

@bot.event
async def on_member_unban(guild, user):
    log_kanal = discord.utils.get(guild.text_channels, name="mod-log")
    if log_kanal:
        embed = discord.Embed(
            title="🔓 Üye Banı Kaldırıldı",
            description=f"**Affedilen Üye:** {user.mention} ({user.name})",
            color=discord.Color.blue()
        )
        await log_kanal.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return
    log_kanal = discord.utils.get(message.guild.text_channels, name="mod-log")
    if log_kanal:
        embed = discord.Embed(
            title="🗑️ Mesaj Silindi",
            description=f"**Kanal:** {message.channel.mention}\n**Yazan:** {message.author.mention}\n**İçerik:** `{message.content or 'İçerik yok/Medya'}`",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Kullanıcı ID: {message.author.id}")
        await log_kanal.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or not before.guild or before.content == after.content:
        return
    log_kanal = discord.utils.get(before.guild.text_channels, name="mod-log")
    if log_kanal:
        embed = discord.Embed(
            title="✏️ Mesaj Düzenlendi",
            description=f"**Kanal:** {before.channel.mention}\n**Yazan:** {before.author.mention}\n**Eski Hali:** `{before.content}`\n**Yeni Hali:** `{after.content}`",
            color=discord.Color.gold()
        )
        await log_kanal.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    log_kanal = discord.utils.get(before.guild.text_channels, name="mod-log")
    if not log_kanal:
        return

    if before.nick != after.nick:
        embed = discord.Embed(
            title="✍️ Kullanıcı Adı (Nick) Değişti",
            description=f"**Üye:** {after.mention}\n**Eski İsim:** `{before.nick or before.name}`\n**Yeni İsim:** `{after.nick or after.name}`",
            color=discord.Color.blue()
        )
        await log_kanal.send(embed=embed)

    if before.roles != after.roles:
        eklenen = [r for r in after.roles if r not in before.roles]
        silinen = [r for r in before.roles if r not in after.roles]
        
        if eklenen or silinen:
            islem_yapan = "Bilinmiyor / Bot"
            await asyncio.sleep(0.5)
            try:
                async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
                    if entry.target.id == after.id:
                        islem_yapan = entry.user.mention
                        break
            except:
                pass

            desc = f"**Üye:** {after.mention}\n**İşlemi Yapan Yetkili:** {islem_yapan}\n"
            if eklenen:
                desc += f"➕ **Eklenen Rol(ler):** {', '.join([r.name for r in eklenen])}\n"
            if silinen:
                desc += f"➖ **Alınan Rol(ler):** {', '.join([r.name for r in silinen])}\n"
            
            embed = discord.Embed(title="🏷️ Rol Güncellendi", description=desc, color=discord.Color.purple())
            await log_kanal.send(embed=embed)

# --- 3. SES KANALI VE OTOMATİK ODA SİSTEMİ ---
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

    if before.channel and ("in Odası" in before.channel.name or "Among Us Odası" in before.channel.name):
        if len(before.channel.members) == 0:
            if before.channel.id in kilitli_odalilar:
                kilitli_odalilar.remove(before.channel.id)
            try:
                await before.channel.delete()
            except:
                pass

    if after.channel and after.channel.name == "➕ Oda Oluştur":
        guild = member.guild
        category = after.channel.category
        oda_adi = f"🔊 | {member.name}'in Odası"
        yeni_kanal = await guild.create_voice_channel(oda_adi, category=category)
        await member.move_to(yeni_kanal)

    if after.channel and after.channel.name == "➕ Among Us Odası":
        guild = member.guild
        category = after.channel.category
        oda_adi = f"🚀 | {member.name}'in Among Us Odası"
        yeni_kanal = await guild.create_voice_channel(oda_adi, category=category, user_limit=12)
        await member.move_to(yeni_kanal)

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

# --- 4. MESAJ KONTROLÜ, KÜFÜR FİLTRESİ VE OYUNLAR ---
@bot.event
async def on_message(message):
    global mesaj_sayaci
    if message.author.bot:
        return

    mesaj_metni = message.content.lower().strip()
    
    # Kim Milyoner Olmak İster 5 Turlu Yarışma Kontrolü
    if message.channel.id in milyoner_oyunlari and mesaj_metni in ["a", "b", "c", "d"]:
        oyun = milyoner_oyunlari[message.channel.id]
        if message.author.id != oyun["oyuncu_id"]:
            return

        aktif_soru = oyun["sorular"][oyun["tur"]]
        if mesaj_metni == aktif_soru["cevap"]:
            oyun["tur"] += 1
            if oyun["tur"] >= 5:
                await message.channel.send(f"🏆 İNANILMAZ! {message.author.mention} tüm soruları doğru bildi ve **1.000.000 TL** Büyük Ödülü kazandı! **Çok akıllısın maşallah!** 👑✨")
                del milyoner_oyunlari[message.channel.id]
            else:
                sonraki_soru = oyun["sorular"][oyun["tur"]]
                secenekler_metni = "\n".join(sonraki_soru["secenekler"])
                odul_miktari = ODULLer[oyun["tur"]]
                embed = discord.Embed(
                    title=f"💰 Milyoner Yarışması | Soru {oyun['tur'] + 1} / 5",
                    description=f"✅ **Tebrikler, doğru bildin!** Sıradaki Ödül: **{odul_miktari}**\n\n**Soru:** {sonraki_soru['soru']}\n\n{secenekler_metni}\n\n*Cevap vermek için şıkkın harfini yaz (A, B, C, D)*",
                    color=discord.Color.gold()
                )
                await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"❌ Yanlış cevap! Yarışmadan elendin. Doğru cevap: **{aktif_soru['cevap'].upper()}** şıkkıydı.")
            del milyoner_oyunlari[message.channel.id]

    # Adam Asmaca Harf Tahmini Kontrolü
    if message.channel.id in adam_asmaca_oyunlari and len(mesaj_metni) == 1 and mesaj_metni.isalpha():
        oyun = adam_asmaca_oyunlari[message.channel.id]
        harf = mesaj_metni
        
        if harf in oyun["tahminler"]:
            await message.channel.send(f"⚠️ Bu harfi zaten söyledin, başka bir harf dene!", delete_after=4)
        elif harf in oyun["kelime"]:
            oyun["tahminler"].append(harf)
            gizli_goruntu = " ".join([h if h in oyun["tahminler"] or h == " " else "_" for h in oyun["kelime"]])
            if "_" not in gizli_goruntu:
                await message.channel.send(f"🎉 Tebrikler {message.author.mention}! Kelimeyi doğru bildin: **{oyun['kelime'].upper()}**. **Çok akıllısın maşallah!** 👑")
                del adam_asmaca_oyunlari[message.channel.id]
            else:
                await message.channel.send(f"✅ Doğru harf! Durum: `{gizli_goruntu}`\nSöylenenler: {', '.join(oyun['tahminler'])}")
        else:
            oyun["tahminler"].append(harf)
            oyun["can"] -= 1
            if oyun["can"] <= 0:
                await message.channel.send(f"💀 Oyunu kaybettin! Asıldın... Doğru kelime: **{oyun['kelime'].upper()}**")
                del adam_asmaca_oyunlari[message.channel.id]
            else:
                gizli_goruntu = " ".join([h if h in oyun['tahminler'] or h == " " else "_" for h in oyun['kelime']])
                await message.channel.send(f"❌ Yanlış harf! Kalan Can: **{oyun['can']}** ❤️\nDurum: `{gizli_goruntu}`")

    # 3 Saatlik Bilgi Sorusu Cevap Kontrolü
    if message.channel.id in aktif_sorular:
        dogru_cevap = aktif_sorular[message.channel.id]
        if dogru_cevap in mesaj_metni:
            await message.channel.send(f"🎉 Helal olsun {message.author.mention}, doğru bildin! **Çok akıllısın maşallah!** 👑")
            del aktif_sorular[message.channel.id]

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

    await bot.process_commands(message)

# --- 5. OYUN KOMUTLARI ---
@bot.command(name="milyoner")
async def milyoner(ctx, kategori: str = None):
    if ctx.channel.id in milyoner_oyunlari:
        await ctx.send("⚠️ Bu kanalda zaten devam eden bir Milyoner yarışması var!")
        return

    kategori = kategori.lower() if kategori else None
    tum_kategoriler = list(MILYONER_VERITABANI.keys())

    if kategori and kategori in tum_kategoriler:
        secilen_kat = kategori
    else:
        secilen_kat = random.choice(tum_kategoriler)

    kategori_sorulari = MILYONER_VERITABANI[secilen_kat]
    secilen_tur_sorulari = random.sample(kategori_sorulari, min(5, len(kategori_sorulari)))

    milyoner_oyunlari[ctx.channel.id] = {
        "oyuncu_id": ctx.author.id,
        "sorular": secilen_tur_sorulari,
        "tur": 0
    }

    ilk_soru = secilen_tur_sorulari[0]
    secenekler_metni = "\n".join(ilk_soru["secenekler"])
    
    embed = discord.Embed(
        title=f"💰 Kim Milyoner Olmak İster? ({secilen_kat.upper()})",
        description=f"🎯 Yarışmacı: {ctx.author.mention}\n1. Soru Ödülü: **{ODULLer[0]}**\n\n**Soru:** {ilk_soru['soru']}\n\n{secenekler_metni}\n\n*Cevap vermek için doğrudan şıkkın harfini yaz (A, B, C, D)*",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.command(name="adam-asmaca")
async def adam_asmaca(ctx, kategori: str = None):
    if ctx.channel.id in adam_asmaca_oyunlari:
        await ctx.send("⚠️ Bu kanalda zaten devam eden bir Adam Asmaca oyunu var!")
        return

    kategori = kategori.lower() if kategori else None
    if kategori and kategori in ASMACA_KATEGORILERI:
        secilen_kelime = random.choice(ASMACA_KATEGORILERI[kategori])
        kategori_adi = kategori.upper()
    else:
        tum_kategoriler = list(ASMACA_KATEGORILERI.keys())
        rastgele_kat = random.choice(tum_kategoriler)
        secilen_kelime = random.choice(ASMACA_KATEGORILERI[rastgele_kat])
        kategori_adi = rastgele_kat.upper()

    adam_asmaca_oyunlari[ctx.channel.id] = {
        "kelime": secilen_kelime,
        "tahminler": [],
        "can": 6
    }

    gizli_goruntu = " ".join(["_" if h != " " else "  " for h in secilen_kelime])
    embed = discord.Embed(
        title=f"🎮 Adam Asmaca Başladı! ({kategori_adi})",
        description=f"Kelimeyi bulmak için sohbetten tek harf yazarak tahmin et!\n\n**Kelime:** `{gizli_goruntu}`\n❤️ **Kalan Can:** 6",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name="tahmin")
async def tahmin(ctx):
    aktif_tahminler[ctx.channel.id] = random.randint(1, 100)
    await ctx.send("🎮 Sayı tahmin oyunu başladı (1-100)!")

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

@bot.command(name="zar")
async def zar(ctx):
    await ctx.send(f"🎲 Zar: **{random.randint(1, 6)}**")

@bot.command(name="yazıtura")
async def yazitura(ctx):
    await ctx.send(f"🪙 Sonuç: **{random.choice(['Yazı', 'Tura'])}**")

# --- 6. ÜYE & EĞLENCE KOMUTLARI ---
@bot.command(name="seviye")
async def seviye(ctx, member: discord.Member = None):
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    await ctx.send(embed=discord.Embed(title=f"⭐ {member.name} Seviye", description=f"XP: {xp} (Seviye: {xp // 100})", color=discord.Color.orange()))

@bot.command(name="ses-seviye")
async def ses_seviye(ctx, member: discord.Member = None):
    member = member or ctx.author
    puan = ses_xp.get(member.id, 0)
    await ctx.send(embed=discord.Embed(title=f"🔊 {member.name} - Ses Puanı", description=f"{puan} Puan", color=discord.Color.blue()))

@bot.command(name="afk")
async def afk(ctx, *, sebep="Belirtilmedi"):
    afk_kullanicilar[ctx.author.id] = sebep
    await ctx.send(f"💤 {ctx.author.mention} AFK moduna geçti. Sebep: *{sebep}*")

@bot.command(name="profil")
async def profil(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(embed=discord.Embed(title=f"👤 {member.name}", description=f"Katılım: {member.joined_at.strftime('%d/%m/%Y')}", color=discord.Color.blue()))

@bot.command(name="kullanıcı-bilgi")
async def kullanici_bilgi(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🔍 {member.name}", description=f"ID: {member.id}\nKatılım: {member.joined_at.strftime('%d/%m/%Y')}", color=discord.Color.dark_blue())
    await ctx.send(embed=embed)

@bot.command(name="sunucu-bilgi")
async def sunucu_bilgi(ctx):
    g = ctx.guild
    await ctx.send(embed=discord.Embed(title=f"📊 {g.name}", description=f"Sahip: {g.owner}\nÜye: {g.member_count}", color=discord.Color.purple()))

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

@bot.command(name="öneri")
async def oneri(ctx, *, metin: str):
    await ctx.message.delete()
    kanal = discord.utils.get(ctx.guild.text_channels, name="öneri") or ctx.channel
    gonderilen = await kanal.send(embed=discord.Embed(title="💡 Öneri", description=metin, color=discord.Color.gold()))
    await gonderilen.add_reaction("👍")
    await gonderilen.add_reaction("👎")

# --- 7. SES ODASI KONTROLÜ ---
@bot.command(name="git")
async def git(ctx, member: discord.Member):
    if not ctx.author.voice:
        await ctx.send("❌ Önce bir ses kanalına girmelisin!")
        return

    if not member.voice or not member.voice.channel:
        await ctx.send(f"❌ {member.mention} şu an herhangi bir ses kanalında değil!")
        return

    hedef_kanal = member.voice.channel
    
    if ctx.author.voice.channel == hedef_kanal:
        await ctx.send(f"⚠️ Zaten {member.mention} ile aynı kanaldasın!")
        return

    try:
        await ctx.author.move_to(hedef_kanal)
        await ctx.send(f"✅ Başarıyla {member.mention} kullanıcısının yanına (**{hedef_kanal.name}**) ışınlandın!")
    except Exception as e:
        await ctx.send(f"⚠️ Kullanıcının yanına gidilemedi. Yetkinin yeterli olduğundan emin ol. Hata: `{e}`")

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

# --- 8. YÖNETİM VE MODERATÖRLÜK KOMUTLARI ---
@bot.command(name="kurulum")
@commands.has_permissions(administrator=True)
async def kurulum(ctx):
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)
    }
    kategori = await guild.create_category("📊 İstatistikler")
    await guild.create_voice_channel(f"📊 Toplam Üye: {guild.member_count}", category=kategori, overwrites=overwrites)
    uye_sayisi = len([m for m in guild.members if not m.bot])
    await guild.create_voice_channel(f"👤 Kullanıcı: {uye_sayisi}", category=kategori, overwrites=overwrites)
    bot_sayisi = len([m for m in guild.members if m.bot])
    await guild.create_voice_channel(f"🤖 Bot Sayısı: {bot_sayisi}", category=kategori, overwrites=overwrites)
    await ctx.send("✅ Sunucu istatistik kanalları başarıyla kuruldu ve sayaçlar aktif edildi!")

@bot.command(name="autorol-ayarla")
@commands.has_permissions(administrator=True)
async def autorol_ayarla(ctx, *, rol_adi: str):
    bulunan_rol = discord.utils.get(ctx.guild.roles, name=rol_adi)
    if bulunan_rol:
        sunucu_autorol[ctx.guild.id] = rol_adi
        await ctx.send(f"✅ Yeni gelenler için otomatik verilecek rol **{rol_adi}** olarak güncellendi!")
    else:
        await ctx.send(f"❌ '{rol_adi}' adında bir rol bulunamadı.")

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

# --- 9. GELİŞMİŞ YARDIM MENÜSÜ ---
@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(
        title="🤖 Ultimate Mega Bot - Komut Merkezi",
        description="Sunucuyu yönetmek ve eğlenmek için kategorize edilmiş komut listesi:",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="🎮 1. Oyun & Eğlence",
        value=(
            "• `!milyoner [lol/valorant/tarih/coğrafya/müzik/futbol/genel/teknoloji]` - 5 turlu Milyoner yarışması\n"
            "• `!adam-asmaca [kategori]` - Adam asmaca oyunu\n"
            "• `!tahmin` - Sayı tahmin oyunu (1-100)\n"
            "• `!kadro-kur [pozisyon]` - 20 TL bütçeli futbol kadro oyunu\n"
            "• `!rastgele-kadro` - Rastgele 11 kurar\n"
            "• `!zar` / `!yazıtura` - Şans oyunları"
        ),
        inline=False
    )
    
    embed.add_field(
        name="👤 2. Üye & Profil",
        value=(
            "• `!seviye` - Mesaj XP ve seviyeni gösterir\n"
            "• `!ses-seviye` - Ses kanalı aktiflik puanını gösterir\n"
            "• `!profil` / `!kullanıcı-bilgi` - Kullanıcı bilgilerini gösterir\n"
            "• `!sunucu-bilgi` - Sunucu bilgilerini gösterir\n"
            "• `!sayaç` - 100 üye hedef ilerlemesini gösterir\n"
            "• `!afk <sebep>` - Uzakta moduna geçiş yapar\n"
            "• `!öneri <mesaj>` - Sunucuya öneri gönderir"
        ),
        inline=False
    )

    embed.add_field(
        name="🚪 3. Ses Odaları",
        value=(
            "• `!git @kullanıcı` - Belirttiğin kişinin ses kanalına ışınlanırsın\n"
            "• `!oda-kapat` - Kendi özel ses odanı kilitler\n"
            "• `!oda-aç` - Kilitli özel ses odanı açar\n"
            "• *Not: '➕ Oda Oluştur' veya '➕ Among Us Odası'na girerek özel oda açabilirsin.*"
        ),
        inline=False
    )

    embed.add_field(
        name="🛠️ 4. Yönetim & Yetkili Komutları",
        value=(
            "• `!kurulum` - İstatistik sayaç kanallarını kurar\n"
            "• `!autorol-ayarla <rol>` - Yeni gelenlere otomatik rol verir\n"
            "• `!çekiliş <saniye> <ödül>` - Ödüllü çekiliş başlatır\n"
            "• `!rol-mesaj <@rol> <mesaj>` - Roldeki herkese özelden mesaj atar\n"
            "• `!uyarı` / `!uyarılar` / `!uyarı-sil` - Üye uyarı sistemi\n"
            "• `!yavaşmod <saniye>` - Kanalı yavaş moda alır\n"
            "• `!kilit` / `!aç` - Kanalı mesajlara kapatır / açar\n"
            "• `!kanal-aç <isim>` - Yeni yazı kanalı açar\n"
            "• `!sil <sayı>` - Toplu mesaj siler\n"
            "• `!kick` / `!ban` - Üye atma ve yasaklama"
        ),
        inline=False
    )

    embed.set_footer(text="Gelişmiş Discord Botu • Her 3 saatte bir otomatik soru aktif!")
    await ctx.send(embed=embed)

keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
