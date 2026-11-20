import os
import json
import time
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

VERI_DOSYASI = "bot_verileri.json"


def tr_lower(metin: str) -> str:
    return metin.replace("İ", "i").replace("I", "ı").lower()


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
hizli_yaz_oyunlari = {}
refleks_oyunlari = {}
soru_kanallari = {}
refleks_kanallari = {}
dm_kapali_kullanicilar = set()
rol_mesaj_sistemi_kapali = set()


def veri_kaydet():
    try:
        veri = {
            "user_xp": {str(k): v for k, v in user_xp.items()},
            "ses_xp": {str(k): v for k, v in ses_xp.items()},
            "sunucu_autorol": {str(k): v for k, v in sunucu_autorol.items()},
            "uyari_veritabani": {str(k): v for k, v in uyari_veritabani.items()},
            "soru_kanallari": {str(k): v for k, v in soru_kanallari.items()},
            "refleks_kanallari": {str(k): v for k, v in refleks_kanallari.items()},
            "dm_kapali_kullanicilar": list(dm_kapali_kullanicilar),
            "rol_mesaj_sistemi_kapali": list(rol_mesaj_sistemi_kapali),
        }
        with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Veri kaydetme hatası: {e}")


def veri_yukle():
    global user_xp, ses_xp, sunucu_autorol, uyari_veritabani
    global soru_kanallari, refleks_kanallari, dm_kapali_kullanicilar, rol_mesaj_sistemi_kapali
    if not os.path.exists(VERI_DOSYASI):
        return
    try:
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            veri = json.load(f)
        user_xp = {int(k): v for k, v in veri.get("user_xp", {}).items()}
        ses_xp = {int(k): v for k, v in veri.get("ses_xp", {}).items()}
        sunucu_autorol = {int(k): v for k, v in veri.get("sunucu_autorol", {}).items()}
        uyari_veritabani = {int(k): v for k, v in veri.get("uyari_veritabani", {}).items()}
        soru_kanallari = {int(k): v for k, v in veri.get("soru_kanallari", {}).items()}
        refleks_kanallari = {int(k): v for k, v in veri.get("refleks_kanallari", {}).items()}
        dm_kapali_kullanicilar = set(veri.get("dm_kapali_kullanicilar", []))
        rol_mesaj_sistemi_kapali = set(veri.get("rol_mesaj_sistemi_kapali", []))
    except Exception as e:
        print(f"Veri yükleme hatası: {e}")


veri_yukle()

OTO_CEVAPLAR = {
    "sa": "as",
    "selamun aleyküm": "aleyküm selam",
    "selamın aleyküm": "aleyküm selam",
}

ESPRILER = [
    "Adamın biri gülmüş, karısı da lahana demiş. 🥬",
    "Geçen gün taksi çevirdim, hala dönüyor. 🚖",
    "Temel kalkmış, musluk oturmuş. 🚰",
    "Kelebeğin ömrü bir gün derler, seninkisi ne zaman bitiyor acaba? 🦋",
    "Aydan gelen misafire ne denir? Ay-nasıl geldin? 🌕",
    "Beni horoz mu tırmaladı, yoksa sen her zamanki gibi komik mi sanıyorsun kendini? 🐓",
    "Denizde balık yan yan yürür, senin bu yürüyüş neyin nesi? 🐟",
    "Hayat boştu, bisiklete biniyorum artık. 🚲",
    "Gözlerim kör oldu formattan sonra, ekranı sildim düzeldi. 💻",
    "Neden matematiğim kötü? Çünkü hayatın kendisi bir problem! 📐",
]

KANAL_ESPRILERI = [
    "Kaynıyor ☕",
    "Gülmekten Öldük 💀",
    "Taksi Dönüyor 🚖",
    "Lahana Bahçesi 🥬",
    "Musluk Oturdu 🚰",
    "Boş Yapma Sesleri 🎙️",
    "Dedikodu Kazanı 🍲",
    "Hayat Boş Bisiklet 🚲",
]

REFLEKS_KELIMELERI = [
    "!basla", "!hizli", "!yakala", "!tikla", "!vur",
    "!kac", "!atla", "!tut", "!cek", "!tetik",
    "!firlat", "!dokun", "!vurur", "!zip", "!kos",
    "!savur", "!patlat", "!carp", "!uyan", "!yakalaaz",
]

YASAKLI_KELIMELER = [
    "allahı sikeyim", "kuranı sikeyim", "allahı", "kuranı",
    "küfür1", "küfür2",
]

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
    {"soru": "İnsan vücudundaki en büyük organ hangisidir?", "cevap": "deri"},
]

ASMACA_KATEGORILERI = {
    "lol": ["yasuo", "thresh", "lee sin", "lux", "ahri", "zed", "blitzcrank", "jinx", "kled", "warwick", "sett"],
    "valorant": ["jett", "reyna", "sage", "omen", "vandal", "phantom", "cypher", "sova", "spike", "bind", "ascent"],
    "minecraft": ["diamond", "creeper", "enderman", "obsidian", "nether", "redstone", "steve", "zombie", "pickaxe", "village"],
    "tarih": ["istanbul", "malazgirt", "osmanlı", "selçuklu", "cumhuriyet", "atatürk", "çanakkale", "fatih", "milli mücadele"],
    "matematik": ["türev", "integral", "geometri", "matris", "fonksiyon", "trigonometri", "logaritma", "olasılık", "parabol"],
}

HIZLI_YAZ_METINLERI = [
    "discord sunucusunun en hizli ve en dikkatli yazari kim?",
    "programlama ogrenmek sabir ve surekli pratik gerektirir.",
    "yapay zeka teknolojileri gelecegin dunyasini sekillendiriyor.",
    "kim milyoner olmak ister yarismasinda buyuk odule ulasabilecek misin?",
    "hizli yazma yarismasinda parmaklarini konusturma vakti geldi!",
]

MILYONER_VERITABANI = {
    "lol": [
        {"soru": "League of Legends oyununda 'Baron Nashor' katledildiğinde takıma hangi güçlendirme verilir?", "secenekler": ["A) Elixir of Iron", "B) Hand of Baron (Nashor Gücü)", "C) Aspect of the Dragon", "D) Crest of Cinders"], "cevap": "b"},
        {"soru": "Hangisi League of Legends evrelerinde bir orman kampı değildir?", "secenekler": ["A) Kurtlar", "B) Kayacıllar", "C) Ejderha", "D) Ejderha Yavrusu Yuvası"], "cevap": "d"},
        {"soru": "Blitzcrank karakterinin Q yeteneğinin adı nedir?", "secenekler": ["A) Rocket Grab", "B) Power Fist", "C) Static Field", "D) Overdrive"], "cevap": "a"},
        {"soru": "League of Legends'da dereceli sistemde Ustalık ile Şampiyonluk arasında yer alan lig hangisidir?", "secenekler": ["A) Elmas", "B) Üstadlık (Grandmaster)", "C) Zümrüt", "D) Demir"], "cevap": "b"},
        {"soru": "Faker kariyerindeki Dünya Şampiyonluklarını hangi takım altında kazanmıştır?", "secenekler": ["A) Gen.G", "B) T1 (SKT)", "C) Damwon", "D) KT Rolster"], "cevap": "b"},
    ],
    "valorant": [
        {"soru": "Valorant oyununda bomba olarak adlandırılan nesnenin resmi adı nedir?", "secenekler": ["A) C4", "B) Spike", "C) Bomb", "D) Dinamit"], "cevap": "b"},
        {"soru": "Ajan Brimstone hangi sınıfa (Role) aittir?", "secenekler": ["A) Düellocu", "B) Kontrol Uzmanı", "C) Öncü", "D) Gözcü"], "cevap": "b"},
        {"soru": "Hangisi Valorant'ın Öncü ajanlarından biri değildir?", "secenekler": ["A) Sova", "B) Skye", "C) Jett", "D) Fade"], "cevap": "c"},
        {"soru": "Valorant oyununda Spike'ı yerleştirmek normal şartlarda kaç saniye sürer?", "secenekler": ["A) 2 saniye", "B) 4 saniye", "C) 6 saniye", "D) 8 saniye"], "cevap": "b"},
        {"soru": "Valorant'ta en yüksek rekabetçi rütbe kademesi aşağıdakilerden hangisidir?", "secenekler": ["A) Yücelik", "B) Ölümsüzlük", "C) Radiant (Radyant)", "D) Elmas"], "cevap": "c"},
    ],
    "tarih": [
        {"soru": "İstanbul kaç yılında Fatih Sultan Mehmet tarafından fethedilmiştir?", "secenekler": ["A) 1299", "B) 1453", "C) 1517", "D) 1923"], "cevap": "b"},
        {"soru": "Türkiye Cumhuriyeti'nin ilk başbakanı kimdir?", "secenekler": ["A) İsmet İnönü", "B) Celâl Bayar", "C) Fevzi Çakmak", "D) Kazım Karabekir"], "cevap": "a"},
        {"soru": "Mustafa Kemal Atatürk'e 'Gazi' unvanı hangi savaştan sonra verilmiştir?", "secenekler": ["A) Çanakkale", "B) Sakarya Meydan Muharebesi", "C) Büyük Taarruz", "D) I. İnönü"], "cevap": "b"},
        {"soru": "Türk tarihinde 'Yurt Açan Savaş' olarak bilinen savaş hangisidir?", "secenekler": ["A) Miryokefalon", "B) Malazgirt", "C) Dandanakan", "D) Pasinler"], "cevap": "b"},
        {"soru": "Osmanlı İmparatorluğu'nun kuruluş yılı resmi olarak genellikle hangi yıl kabul edilir?", "secenekler": ["A) 1299", "B) 1302", "C) 1453", "D) 1071"], "cevap": "a"},
    ],
    "coğrafya": [
        {"soru": "Türkiye'nin yüz ölçümü bakımından en büyük ili hangisidir?", "secenekler": ["A) Ankara", "B) Sivas", "C) Konya", "D) Van"], "cevap": "c"},
        {"soru": "Türkiye'nin en yüksek dağı olan Ağrı Dağı hangi ilimiz sınırları içerisindedir?", "secenekler": ["A) Erzurum", "B) Van", "C) Iğdır / Ağrı", "D) Kars"], "cevap": "c"},
        {"soru": "Dünyanın en uzun nehirleri arasında gösterilen Nil Nehri hangi kıtada yer alır?", "secenekler": ["A) Asya", "B) Afrika", "C) Güney Amerika", "D) Avrupa"], "cevap": "b"},
        {"soru": "Hangi kıta yüz ölçümü bakımından dünyanın en küçük kıtasıdır?", "secenekler": ["A) Avrupa", "B) Antarktika", "C) Okyanusya (Avustralya)", "D) Güney Amerika"], "cevap": "c"},
        {"soru": "Dünyanın en derin okyanus çukuru olan 'Mariana Çukuru' hangi okyanusta yer alır?", "secenekler": ["A) Atlas", "B) Hint", "C) Pasifik (Büyük Okyanus)", "D) Arktik"], "cevap": "c"},
    ],
    "müzik": [
        {"soru": "Müzik notalarında 'sol anahtarı' portenin kaçıncı çizgisinden başlar?", "secenekler": ["A) 1. Çizgi", "B) 2. Çizgi", "C) 3. Çizgi", "D) 4. Çizgi"], "cevap": "b"},
        {"soru": "Aşağıdaki enstrümanlardan hangisi yaylı çalgılar grubuna girer?", "secenekler": ["A) Flüt", "B) Viyolonsel (Çello)", "C) Klarnet", "D) Trompet"], "cevap": "b"},
        {"soru": "Klasik batı müziğinde 'en yavaş' tempo terimi aşağıdakilerden hangisidir?", "secenekler": ["A) Allegro", "B) Andante", "C) Largo", "D) Presto"], "cevap": "c"},
        {"soru": "Türkiye'de 'Dönence' ve 'Aldırma Gönül' gibi unutulmaz eserlere imza atmış Anadolu Rock grubu hangisidir?", "secenekler": ["A) Duman", "B) Moğollar", "C) MFÖ", "D) Athena"], "cevap": "b"},
        {"soru": "Dünyaca ünlü 'Bohemian Rhapsody' şarkısı hangi efsanevi müzik grubuna aittir?", "secenekler": ["A) The Beatles", "B) Pink Floyd", "C) Queen", "D) Led Zeppelin"], "cevap": "c"},
    ],
    "futbol": [
        {"soru": "Bir futbol maçında kaleci dışında bir oyuncunun elle müdahale etmesi sonucu hakemin verdiği ceza atışı hangisidir?", "secenekler": ["A) Taç", "B) Korner", "C) Penaltı", "D) Endirekt Vuruş"], "cevap": "c"},
        {"soru": "Türkiye A Milli Futbol Takımı, FIFA Dünya Kupası tarihindeki en iyi derecesi olan üçüncülüğü hangi yılda elde etmiştir?", "secenekler": ["A) 1996", "B) 2002", "C) 2008", "D) 2020"], "cevap": "b"},
        {"soru": "Dünyada 'Kral' lakabıyla tanınan ve 3 kez Dünya Kupası kazanan efsanevi Brezilyalı futbolcu kimdir?", "secenekler": ["A) Maradona", "B) Pele", "C) Ronaldinho", "D) Ronaldo"], "cevap": "b"},
        {"soru": "Hangi futbol kulübü UEFA Şampiyonlar Ligi'ni tarihte en çok kazanan takımdır?", "secenekler": ["A) AC Milan", "B) Barcelona", "C) Real Madrid", "D) Bayern Munich"], "cevap": "c"},
        {"soru": "Resmi bir futbol maçında bir takımın sahada en az kaç oyuncusu kalırsa maç tatil edilir?", "secenekler": ["A) 5 oyuncu", "B) 6 oyuncu", "C) 7 oyuncu", "D) 9 oyuncu"], "cevap": "c"},
    ],
    "genel": [
        {"soru": "Güneş sistemindeki en büyük gezegen aşağıdakilerden hangisidir?", "secenekler": ["A) Satürn", "B) Jüpiter", "C) Neptün", "D) Mars"], "cevap": "b"},
        {"soru": "Mona Lisa tablosunu çizen dünyaca ünlü İtalyan sanatçı ve deha kimdir?", "secenekler": ["A) Donatello", "B) Leonardo da Vinci", "C) Michelangelo", "D) Raphael"], "cevap": "b"},
        {"soru": "Nobel Ödülleri hangi ülkede verilmektedir?", "secenekler": ["A) Almanya", "B) İsviçre", "C) İsveç", "D) Fransa"], "cevap": "c"},
        {"soru": "Periyodik tablonun ilk elementi ve evrende en bol bulunan kimyasal element hangisidir?", "secenekler": ["A) Helyum", "B) Oksijen", "C) Hidrojen", "D) Karbon"], "cevap": "c"},
        {"soru": "Dünyanın çevresini ilk kez dolaşan denizci kimdir?", "secenekler": ["A) Vasco da Gama", "B) Kristof Kolomb", "C) Juan Sebastián Elcano", "D) Amerigo Vespucci"], "cevap": "c"},
    ],
    "teknoloji": [
        {"soru": "İnternetin temelini oluşturan ve 'Ağların Ağı' anlamına gelen küresel sistemin kısaltması nedir?", "secenekler": ["A) WWW", "B) HTTP", "C) TCP", "D) LAN"], "cevap": "a"},
        {"soru": "Linux işletim sisteminin maskotu olan sevimli penguenin adı nedir?", "secenekler": ["A) Pingu", "B) Tux", "C) Linuxy", "D) Waddle"], "cevap": "b"},
        {"soru": "Yapay zeka alanında sıkça kullanılan 'ChatGPT' dil modelini geliştiren şirketin adı nedir?", "secenekler": ["A) Google", "B) Microsoft", "C) OpenAI", "D) Apple"], "cevap": "c"},
        {"soru": "Bilgisayarlarda veri depolamak için kullanılan ve elektrik kesildiğinde verileri silinmeyen kalıcı bellek hangisidir?", "secenekler": ["A) RAM", "B) Cache", "C) SSD / Sabit Disk", "D) Register"], "cevap": "c"},
        {"soru": "İlk programlanabilir elektronik bilgisayar olarak kabul edilen ve 1945 yılında geliştirilen devasa cihazın adı nedir?", "secenekler": ["A) ENIAC", "B) UNIVAC", "C) Altair 8800", "D) IBM 5100"], "cevap": "a"},
    ],
}

ODULLER = ["1.000 TL", "10.000 TL", "50.000 TL", "250.000 TL", "1.000.000 TL"]


@bot.event
async def on_ready():
    print(f"Giriş yapıldı! Bot aktif: {bot.user}")
    if not istatistik_guncelle.is_running():
        istatistik_guncelle.start()
    if not saatlik_soru_gonderici.is_running():
        saatlik_soru_gonderici.start()
    if not on_dakika_tarama_ve_refleks.is_running():
        on_dakika_tarama_ve_refleks.start()


# --- GENEL HATA YAKALAYICI (Komutların sessiz kalmasını önler) ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Eksik bilgi girdin! Doğru kullanım için `!yardım` yazabilirsin. *(Eksik parametre: `{error.param.name}`)*")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ Bu komutu kullanmak için yeterli sunucu yetkin yok!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("⚠️ Botun bu işlemi yapabilmesi için gerekli sunucu yetkisi eksik! Bot rolüne **Yönetici** veya **Kanalları/Rolleri Yönet** yetkisi verin.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Belirttiğin kullanıcı sunucuda bulunamadı! Kullanıcıyı `@etiket` şeklinde seçmelisin.")
    elif isinstance(
