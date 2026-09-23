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

GUNCEL_SORULAR = [
    {"soru": "🧠 **Günün Bilgi Sorusu:** Hangi futbol takımı, Şampiyonlar Ligi'ni en çok kazanan kulüptür?", "cevap": "real madrid"},
    {"soru": "🧠 **Günün Bilgi Sorusu:** Türkiye'nin yüz ölçümü bakımından en büyük şehri hangisidir?", "cevap": "konya"},
    {"soru": "🧠 **Günün Bilgi Sorusu:** Bilgisayar biliminin babası olarak bilinen ve yapay zekanın temellerini atan ünlü İngiliz matematikçi kimdir?", "cevap": "alan turing"},
    {"soru": "🧠 **Günün Bilgi Sorusu:** 'Grand Line' hangi ünlü anime serisinde yer alan okyanus yoludur?", "cevap": "one piece"},
    {"soru": "🧠 **Günün Bilgi Sorusu:** Güneş sistemindeki en büyük gezegen hangisidir?", "cevap": "jüpiter"},
    {"soru": "🧠 **Günün Bilgi Sorusu:** İstanbul hangi yıl feth edilmiştir?", "cevap": "1453"}
]

ASMACA_KATEGORILERI = {
    "lol": ["yasuo", "thresh", "lee sin", "lux", "ahri", "zed", "blitzcrank", "jinx", "kled", "warwick", "sett"],
    "valorant": ["jett", "reyna", "sage", "omen", "vandal", "phantom", "cypher", "sova", "spike", "bind", "ascent"],
    "minecraft": ["diamond", "creeper", "enderman", "obsidian", "nether", "redstone", "steve", "zombie", "pickaxe", "village"],
    "tarih": ["istanbul", "malazgirt", "osmanlı", "selçuklu", "cumhuriyet", "atatürk", "çanakkale", "fatih", "milli mücadele"],
    "matematik": ["türev", "integral", "geometri", "matris", "fonksiyon", "trigonometri", "logaritma", "olasılık", "parabol"]
}

# HER KATEGORİ İÇİN 100 SORULUK DEVASA HAVUZ
MILYONER_VERITABANI = {
    "lol": [
        # 1.000 TL Soruları
        {"soru": "League of Legends oyununda haritada tarafsız canavarların doğduğu alanlara ne ad verilir?", "secenekler": ["A) Üs", "B) Orman", "C) Koridor", "D) Dükkan"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Summoner's Rift haritasında kaç adet koridor bulunur?", "secenekler": ["A) 1", "B) 2", "C) 3", "D) 4"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Hangisi bir League of Legends oyun modu değildir?", "secenekler": ["A) URF", "B) ARAM", "C) Teamfight Tactics", "D) Danger Zone"], "cevap": "d", "odul": "1.000 TL"},
        {"soru": "Oyuncuların oyun başında şampiyonlara altın vererek eşya aldığı yerin adı nedir?", "secenekler": ["A) Market", "B) Shop (Mağaza)", "C) Bank", "D) Base"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "League of Legends oyununun ana geliştiricisi ve yayımcısı olan şirket hangisidir?", "secenekler": ["A) Valve", "B) Riot Games", "C) Blizzard", "D) Epic Games"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Hangisi oyundaki temel harita türlerinden biridir?", "secenekler": ["A) Summoner's Rift", "B) Dust2", "C) Erangel", "D) Inferno"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Oyunda karakterlerin seviye sınırı normal oyun modlarında kaça kadardır?", "secenekler": ["A) 10", "B) 18", "C) 30", "D) 100"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Şampiyonların pasif ve aktif yeteneklerini kullanmak için harcadığı temel kaynak barının adı nedir?", "secenekler": ["A) Enerji / Mana", "B) Can", "C) Zırh", "D) Hız"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Karakterlerin haritada hızlıca üsse dönmesini sağlayan büyü veya kanal komutunun adı nedir?", "secenekler": ["A) Flash", "B) Teleport", "C) Recall (Geri Çağırma)", "D) Smite"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Oyun içerisindeki en yüksek dereceli lig adlarından biri hangisidir?", "secenekler": ["A) Challenger", "B) Global Elite", "C) Immortal", "D) Radiant"], "cevap": "a", "odul": "1.000 TL"},
        # 10.000 TL Soruları
        {"soru": "Blitzcrank karakterinin Q yeteneğinin adı nedir?", "secenekler": ["A) Rocket Grab", "B) Power Fist", "C) Static Field", "D) Overdrive"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Teemo karakterinin en bilinen ve haritaya yerleştirdiği gizli silahı nedir?", "secenekler": ["A) Mayın", "B) Mantar", "C) Bomba", "D) Tuzak"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Yasuo karakterinin pasif yeteneği ona ne kazandırır?", "secenekler": ["A) Can yenileme", "B) Kritik vuruş şansı ve kalkan", "C) Görünmezlik", "D) Hareket hızı"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Ejderha katledildiğinde takıma kalıcı güçlendirme veren ilk elementlerden biri hangisi değildir?", "secenekler": ["A) Alev", "B) Dağ", "C) Rüzgar", "D) Uzay"], "cevap": "d", "odul": "10.000 TL"},
        {"soru": "Katarina karakterinin ulti yeteneğinin adı nedir?", "secenekler": ["A) Death Lotus", "B) Shunpo", "C) Bouncing Blade", "D) Preparation"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Nasus karakterinin Q yeteneği ile minyon biçtikçe neyi artar?", "secenekler": ["A) Zırhı", "B) Hasarı (Yük biriktirir)", "C) Canı", "D) Saldırı hızı"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Lux karakterinin ulti yeteneği (R) nedir?", "secenekler": ["A) Final Spark", "B) Light Binding", "C) Prismatic Barrier", "D) Lucent Singularity"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Shaco karakterinin en belirgin özelliklerinden biri hangisidir?", "secenekler": ["A) Uçabilmesi", "B) Klon üretebilmesi ve görünmez olması", "C) Sınırsız canı olması", "D) Haritada ışınlanması"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Master Yi karakterinin Q yeteneği ile yaptığı hareket nedir?", "secenekler": ["A) Alfa Vuruşu (Alpha Strike)", "B) Meditasyon", "C) Wuju Stili", "D) Highlander"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Zed karakterinin temel mekaniği ne üzerine kuruludur?", "secenekler": ["A) Gölge (Shadow)", "B) Ateş", "C) Buz", "D) Yıldırım"], "cevap": "a", "odul": "10.000 TL"},
        # 50.000 TL Soruları
        {"soru": "Hangisi League of Legends evrelerinde bir orman kampı değildir?", "secenekler": ["A) Kurtlar", "B) Kayacıllar", "C) Ejderha", "D) Ejderha Yavrusu Yuvası"], "cevap": "d", "odul": "50.000 TL"},
        {"soru": "Rift Herald (Vadiin Sihirbazı) kuleleri yıkmak için çağrıldığında neyi hedefler?", "secenekler": ["A) Minyonlar", "B) Doğrudan kuleleri", "C) Ormancıları", "D) Ejderhayı"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Karthus karakterinin global ulti yeteneğinin adı nedir?", "secenekler": ["A) Requiem", "B) Lay Waste", "C) Defile", "D) Pain"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Kled karakterinin bindiği sadık kertenkele biniti dostunun adı nedir?", "secenekler": ["A) Rex", "B) Skaarl", "C) Draco", "D) Koko"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Ekko karakterinin ulti yeteneği ne işe yarar?", "secenekler": ["A) Zamanı birkaç saniye geriye sarar", "B) Görünmez olur", "C) Takım arkadaşını diriltir", "D) Haritayı patlatır"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Bard karakterinin topladığı haritadaki sarıimtırak nesnelerin adı nedir?", "secenekler": ["A) Çanlar (Chimes)", "B) Yıldızlar", "C) Ruhlar", "D) Altınlar"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Kalista karakterinin bağ kurduğu takım arkadaşına verilen özel eşyanın adı nedir?", "secenekler": ["A) Kara Balta", "B) Kara Mızrak", "C) Kalbin İntikamı", "D) Ruh Gömleği"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Mordekaiser'in ulti yeteneği rakiplerini nereye hapseder?", "secenekler": ["A) Ölüler Diyarına (Death Realm)", "B) Gölge Dünyasına", "C) Mağaraya", "D) Üsse"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Kindred karakteri kimlerden oluşan bir çifttir?", "secenekler": ["A) Kurt ve Kuzu", "B) Ejderha ve Şövalye", "C) Kedi ve Köpek", "D) Kartal ve Yılan"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Pyke karakterinin rolü ağırlıklı olarak hangi koridorda/pozisyonda oynanır?", "secenekler": ["A) Üst Koridor", "B) Destek (Support)", "C) Ormancı", "D) Orta Koridor"], "cevap": "b", "odul": "50.000 TL"},
        # 250.000 TL Soruları
        {"soru": "League of Legends'da dereceli sistemde Ustalık ile Şampiyonluk arasında yer alan lig hangisidir?", "secenekler": ["A) Elmas", "B) Üstadlık (Grandmaster)", "C) Zümrüt", "D) Demir"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "LoL e-spor tarihinde ilk Dünya Şampiyonasını (Worlds 2011) kazanan takım hangisidir?", "secenekler": ["A) T1 (SKT)", "B) Fnatic", "C) Invictus Gaming", "D) EDward Gaming"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Aurelion Sol karakterinin ilk çıkış versiyonunda pasif olarak etrafında dönen cisimler neydi?", "secenekler": ["A) Yıldızlar", "B) Gezegenler", "C) Kılıçlar", "D) Küreler"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "LoL evresinde 'Runeterra' dünyasında Noxus imparatorluğunun başkenti neresidir?", "secenekler": ["A) Demacia", "B) Piltover", "C) Noxus (Başkent Noxus City)", "D) Ionia"], "cevap": "c", "odul": "250.000 TL"},
        {"soru": "Taric karakterinin rework öncesi eski ikonik tiplemesi ve özellikleriyle bilinen meme hareketi neydi?", "secenekler": ["A) Taş kesilmesi", "B) Muazzam pembe zırhı ve 'Truly Outrageous' repliği", "C) Kalkan fırlatması", "D) Ejderha çağırması"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Singed karakterinin sırtında taşıdığı zehir bidonunun sızdırdığı gazın izlediği yolda rakiplere verdiği etki nedir?", "secenekler": ["A) Yavaşlatma", "B) Zehirleme ve hasar", "C) Sersemletme", "D) Susturma"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "LoL'de ilk çıkan efsanevi (Legendary) kostüm serilerinden biri olan ve Cho'Gath'ın sahip olduğu devasa canavar kostümü hangisidir?", "secenekler": ["A) Öldveren Cho'Gath", "B) Gentleman Cho'Gath", "C) Battle Boss Cho'Gath", "D) Prehistoric Cho'Gath"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Yorick karakterinin mezardan çıkardığı küçük hayaletimsi yaratıkların adı nedir?", "secenekler": ["A) Hortlaklar (Mist Walkers)", "B) Zombiler", "C) İskeletler", "D) Goblinler"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Illaoi karakterinin tapındığı tanrının adı nedir?", "secenekler": ["A) Nagakaboruos", "B) Shurima Tanrısı", "C) Freljord Ruhu", "D) Darkin Tanrısı"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "LoL'de 'Hextech' teknolojisiyle bilinen iki ikiz şehir hangisidir?", "secenekler": ["A) Piltover ve Zaun", "B) Demacia ve Noxus", "C) Ionia ve Shurima", "D) Bilgewater ve Shadow Isles"], "cevap": "a", "odul": "250.000 TL"},
        # 1.000.000 TL Soruları
        {"soru": "League of Legends oyununda 'Baron Nashor' katledildiğinde takıma hangi kalıcı güçlendirme verilir?", "secenekler": ["A) Elixir of Iron", "B) Hand of Baron (Nashor Gücü)", "C) Aspect of the Dragon", "D) Crest of Cinders"], "cevap": "b", "odul": "1.000.000 TL"},
        {"soru": "Faker (Lee Sanghyeok) profesyonel LoL kariyerinde tüm Dünya Şampiyonluklarını hangi tek organizasyon çatısı altında kazanmıştır?", "secenekler": ["A) Gen.G", "B) SK Telecom T1 (T1)", "C) Damwon KIA", "D) KT Rolster"], "cevap": "b", "odul": "1.000.000 TL"},
        {"soru": "LoL evreninde Void (Hiçlik) varlıklarından biri olmayan şampiyon hangisidir?", "secenekler": ["A) Vel'Koz", "B) Kog'Maw", "C) Kha'Zix", "D) Viktor"], "cevap": "d", "odul": "1.000.000 TL"},
        {"soru": "LoL'ün ilk yıllarında oyundan kaldırılan ve daha sonra efsaneleşen, haritada hız bonusu veren eşyanın adı nedir?", "secenekler": ["A) Force of Nature", "B) Heart of Gold", "C) Innervating Locket", "D) DFG (Deathfire Grasp)"], "cevap": "d", "odul": "1.000.000 TL"},
        {"soru": "Riot Games'in LoL evrenini genişletmek için çıkardığı ve Jinx ile Vi'ın hikayesini anlatan Emmy ödüllü animasyon dizisinin adı nedir?", "secenekler": ["A) DOTA: Dragon's Blood", "B) Arcane", "C) Cyberpunk", "D) Castlevania"], "cevap": "b", "odul": "1.000.000 TL"},
        {"soru": "LoL'ün kökeni olan ve ilk haritanın dayandığı orijinal DotA modunun yapımcısı olan efsanevi harita tasarımcısı kimdir?", "secenekler": ["A) Guinsoo", "B) IceFrog", "C) Euls", "D) Hepsi sırasıyla katkıda bulunmuştur"], "cevap": "d", "odul": "1.000.000 TL"},
        {"soru": "Shurima imparatorluğunun göksel güçlerle yeniden doğan imparatoru ve Azir'in baş düşmanı olan karakter kimdir?", "secenekler": ["A) Xerath", "B) Nasus", "C) Renekton", "D) Rammus"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "LoL şampiyonu Jhin'in karakter tasarımı ve yetenek seti özellikle hangi sayı teması üzerine kurulmuştur?", "secenekler": ["A) 3", "B) 4", "C) 7", "D) 9"], "cevap": "b", "odul": "1.000.000 TL"},
        {"soru": "Targon Dağı'nın zirvesine tırmanıp Aspect (Görünüm) güçleriyle birleşen ilk mortal (ölümlü) savaşçılardan biri olan ve Pantheon'un bedenini ele geçiren eski savaşçının adı nedir?", "secenekler": ["A) Atreus", "B) Leona", "C) Diana", "D) Taric"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "LoL'de 'True Damage' (Gerçek Hasar) türü, hedef karakterin hangi özelliğini tamamen yok sayarak hasar verir?", "secenekler": ["A) Sadece canını", "B) Zırh ve büyü direncini", "C) Sadece hareket hızını", "D) Yetenek cooldown süresini"], "cevap": "b", "odul": "1.000.000 TL"}
    ],
    "valorant": [
        # 1.000 TL Soruları
        {"soru": "Valorant oyununda bomba olarak adlandırılan nesnenin resmi adı nedir?", "secenekler": ["A) C4", "B) Spike", "C) Bomb", "D) Dinamit"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Valorant oyununda takımlar kaçar kişiden oluşur?", "secenekler": ["A) 3", "B) 4", "C) 5", "D) 6"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Standart rekabetçi modda bir maçı kazanmak için kaç tur (round) almak gerekir?", "secenekler": ["A) 10", "B) 13", "C) 16", "D) 21"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Oyunda en popüler tek atışlık (headshot) ağır tüfeğin adı nedir?", "secenekler": ["A) Vandal", "B) Phantom", "C) Operator", "D) Bulldog"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Ajanların haritada yetenek satın almak için kullandığı para biriminin adı nedir?", "secenekler": ["A) Altın", "B) Kredi (Creds)", "C) Dolar", "D) Puan"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Valorant oyununun yapımcısı olan şirket hangisidir?", "secenekler": ["A) Riot Games", "B) Valve", "C) Ubisoft", "D) EA Sports"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Hangisi Valorant'ta bulunan bir harita değildir?", "secenekler": ["A) Bind", "B) Ascent", "C) Mirage", "D) Haven"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Ajanların oyundaki özel güçlerine verilen genel ad nedir?", "secenekler": ["A) Perk", "B) Yetenek (Ability)", "C) Skill", "D) Magic"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Saldırı etabındaki takımın temel amacı nedir?", "secenekler": ["A) Süre bitene kadar beklemek", "B) Spike'ı yerleştirmek veya rakipleri yok etmek", "C) Sadece bıçakla vurmak", "D) Haritadan kaçmak"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Oyunda hafif makineli tabancalar arasında en bilinenlerden biri hangisidir?", "secenekler": ["A) Stinger", "B) Vandal", "C) Sheriff", "D) Odin"], "cevap": "a", "odul": "1.000 TL"},
        # 10.000 TL Soruları
        {"soru": "Ajan Brimstone hangi sınıfa (Role) aittir?", "secenekler": ["A) Düellocu", "B) Kontrol Uzmanı (Controller)", "C) Öncü", "D) Gözcü"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Sova ajanının keşif yapmak için kullandığı temel alet nedir?", "secenekler": ["A) Keşif Oku (Recon Bolt)", "B) Drone", "C) Kamera", "D) Sensör"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Sage ajanının takım arkadaşlarına yaptığı temel yardım nedir?", "secenekler": ["A) Zırh vermek", "B) Can basmak ve diriltmek", "C) Hızlandırmak", "D) Görünmez yapmak"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Cypher ajanının haritaya yerleştirdiği ve rakiplerin yerini gösteren temel ekipmanı nedir?", "secenekler": ["A) Kamera", "B) Mayın", "C) Bomba", "D) Kalkan"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Omen ajanının rakipleri kör etmek için attığı yeteneğin adı nedir?", "secenekler": ["A) Paranoia", "B) Dark Cover", "C) Shrouded Step", "D) From the Shadows"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Vandal ve Phantom silahları arasındaki en büyük temel fark nedir?", "soru_duzelt": "Vandal ve Phantom arasındaki temel fark nedir?", "secenekler": ["A) Vandal mesafeden bağımsız tek kafada öldürür, Phantom'un hasarı mesafeyle düşer", "B) Phantom daha pahalıdır", "C) Vandal dürbünlüdür", "D) Hiçbiri"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Reyna karakteri rakiplerini vurduktan sonra can yenilemek veya ne kazanmak için küreleri emer?", "secenekler": ["A) Görünmezlik", "B) Özet (Devour / Dismiss - Yırtıcı / Süzülme)", "C) Ekstra mermi", "D) Zırh"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Killjoy ajanının otomatik olarak rakiplere hasar veren küçük robotik cihazının adı nedir?", "secenekler": ["A) Turret (Taret)", "B) Drone", "C) Bot", "D) Kapan"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Jett ajanının havada süzülmesini sağlayan pasif tuşu hangisidir?", "secenekler": ["A) Space (Zıplama tuşu basılı tutma)", "B) Shift", "C) Ctrl", "D) E"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Brimstone'un ulti yeteneği haritanın belirli bir bölgesine ne yağdırır?", "secenekler": ["A) Lazer / Uydu Saldırısı", "B) Bomba", "C) Sis", "D) Ateş topu"], "cevap": "a", "odul": "10.000 TL"},
        # 50.000 TL Soruları
        {"soru": "Hangisi Valorant'ın 'Öncü (Initiator)' ajanlarından biri değildir?", "secenekler": ["A) Sova", "B) Skye", "C) Jett", "D) Fade"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Valorant'ta maçlarda taraflar (Saldırı / Savunma) kaçıncı turda yer değiştirir?", "secenekler": ["A) 6. turda", "B) 12. turda", "C) 15. turda", "D) 8. turda"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Ajan Viper'ın yeteneklerini kullanırken tükettiği özel kaynağın adı nedir?", "secenekler": ["A) Zehir / Yakıt (Fuel)", "B) Mana", "C) Enerji", "D) Can"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Kay/o ajanının ulti yeteneği aktifken etrafındaki rakiplere ve kendisine ne sağlar?", "secenekler": ["A) Rakiplerin yetenek kullanımını engeller (Suppress)", "B) Görünmez yapar", "C) Ölümsüz kılar", "D) Can doldurur"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Fade ajanının attığı ve rakiplerin yerini açığa çıkarıp sağır eden kabus küresinin adı nedir?", "secenekler": ["A) Haunt (Musallat)", "B) Prowler", "C) Seize", "D) Nightfall"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Neon ajanı elektrik güçleriyle ne yapabilme yeteneğine sahiptir?", "secenekler": ["A) Çok hızlı koşabilme ve kayabilme", "B) Uçabilme", "C) Duvarların içinden geçebilme", "D) Işınlanabilme"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Haritalarda bulunan ve üzerinden geçildiğinde ulti puanı veren kürenin adı nedir?", "secenekler": ["A) Ulti Küresi (Ultimate Orb)", "B) Bonus Küre", "C) Para Küresi", "D) Can Küresi"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Ajan Chamber'ın kendi elleriyle çıkardığı ve tek atışta öldürebilen özel keskin nişancı tüfeğinin adı nedir?", "secenekler": ["A) Tour De Force", "B) Headhunter", "C) Sheriff", "D) Guardian"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Ajan Breach'in duvarların arkasından bile geçerek rakipleri sersemleten yeteneğinin adı nedir?", "secenekler": ["A) Fault Line", "B) Flashpoint", "C) Aftershock", "D) Rolling Thunder"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Deadlock ajanı hangi sınıfa mensuptur?", "secenekler": ["A) Gözcü (Sentinel)", "B) Düellocu", "C) Kontrol Uzmanı", "D) Öncü"], "cevap": "a", "odul": "50.000 TL"},
        # 250.000 TL Soruları
        {"soru": "Valorant oyununda Spike'ı yerleştirmek (plant) normal şartlarda kaç saniye sürer?", "secenekler": ["A) 2 saniye", "B) 4 saniye", "C) 6 saniye", "D) 8 saniye"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Valorant'ın ilk VCT (Valorant Champions Tour) dünya turnuvasını 2021 yılında kazanan espor takımı hangisidir?", "secenekler": ["A) Gambit Esports", "B) Acend", "C) Sentinels", "D) Fnatic"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Valorant evreninde ajanların güçlerini aldığı gizemli ve felaket niteliğindeki küresel olayın adı nedir?", "secenekler": ["A) First Light (İlk Işık)", "B) The Big Bang", "C) The Collapse", "D) Void Storm"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Ajan Skye'ın takım arkadaşlarını iyileştirmek için kullandığı havada uçan sembolün şekli nedir?", "secenekler": ["A) Şahin / Kuş", "B) Kurt", "C) Aslan", "D) Timsah"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Breeze haritasının en belirgin coğrafi ve stratejik özelliği nedir?", "secenekler": ["A) Çok geniş açık alanlar ve ortadaki devasa kapı mekanizması", "B) Dar koridorlar", "C) Halat hatları", "D) Işınlayıcılar"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Valorant'ta 'Eco' round ne anlama gelir?", "secenekler": ["A) Para harcamayıp ekonomik oynamak", "B) En pahalı silahları almak", "C) Sadece bomba kurmak", "D) Sürekli koşmak"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Ajan Clove hangi yenilikçi özelliğiyle diğer ajanlardan ayrılır?", "secenekler": ["A) Öldükten sonra bile sis atabilmesi ve ultisiyle dirilebilmesi", "B) Uçabilmesi", "C) Görünmez olması", "D) Silah çalabilmesi"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Icebox haritasında oyuncuların bölgeler arası hızlı geçiş için kullandığı mekanik nedir?", "secenekler": ["A) Zipline (Halatlar)", "B) Işınlayıcılar", "C) Asansörler", "D) Tramplenler"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Valorant'ta 'Smurf' kelimesi neyi ifade eder?", "secenekler": ["A) Yüksek rütbeli bir oyuncunun düşük rütbeli yan hesapla oynaması", "B) Yeni başlayan oyuncu", "C) Hileci", "D) Takım kaptanı"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Ajan Iso'nun ulti yeteneği rakiplerini nereye çekerek birebir düelloya sokar?", "secenekler": ["A) Arenaya (Birebir boyut)", "B) Üsse", "C) Haritanın dışına", "D) Sis içine"], "cevap": "a", "odul": "250.000 TL"},
        # 1.000.000 TL Soruları
        {"soru": "Valorant'ta en yüksek rekabetçi rütbe kademesi aşağıdakilerden hangisidir?", "secenekler": ["A) Yücelik", "B) Ölümsüzlük", "C) Radiant (Radyant)", "D) Elmas"], "cevap": "c", "odul": "1.000.000 TL"},
        {"soru": "Valorant'ın ana hikayesinde Omega ve Alpha dünyaları arasındaki çatışmanın temel sebebi nedir?", "secenekler": ["A) Kaynak (Radianit) kıtlığı ve kontrolü", "B) Toprak anlaşmazlığı", "C) Siyasi rejimler", "D) Uzaylı istilası"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Valorant'ta 'First Blood' (İlk Kan) istatistiği bir turda ne zaman verilir?", "secenekler": ["A) Turdaki ilk rakip öldürmesini gerçekleştiren oyuncuya", "B) İlk ölene", "C) İlk spike kurana", "D) İlk yetenek kullananaya"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Riot Games'in Valorant'ı geliştirmek için kullandığı oyun motoru (Game Engine) hangisidir?", "secenekler": ["A) Unreal Engine 4", "B) Unity", "C) Source 2", "D) CryEngine"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Valorant'ın antireklam ve hile koruma sisteminin resmi adı nedir?", "secenekler": ["A) Vanguard", "B) Easy Anti-Cheat", "C) BattlEye", "D) VAC"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Ajan Viper'ın gerçek adı ve protokole katışmadan önceki mesleki kökeni nedir?", "secenekler": ["A) Dr. Sabine - Biyokimyager", "B) Mei Ling - Asker", "C) Marta - Casus", "D) Elena - Mühendis"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Valorant'ta 'Flawless' (Kusursuz) yazısı ekranda ne zaman beliri?", "secenekler": ["A) Savunma veya saldırı takımından hiç kimse ölmeden turu kazandığında", "B) Sadece bıçakla kazanıldığında", "C) Süre bittiğinde", "D) Tek mermiyle herkes vurulduğunda"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Valorant protokolünün kurucusu ve lideri olan gizemli karakter kimdir?", "secenekler": ["A) Brimstone", "B) Viper", "C) Cypher", "D) Killjoy"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Lotus haritasının en belirgin harita mimari özelliği nedir?", "secenekler": ["A) Üç adet spike bölgesi (A, B, C) ve dönen taş duvarlar", "B) Teleportlar", "C) Asansörler", "D) Su kanalları"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Valorant espor sahnesinde bir maçta 'Ace' yapmak ne anlama gelir?", "secenekler": ["A) Rakip takımın 5 oyuncusunun tamamını tek bir oyuncunun öldürmesi", "B) Maçı kazanmak", "C) Spike çözmek", "D) En çok parayı toplamak"], "cevap": "a", "odul": "1.000.000 TL"}
    ],
    "tarih": [
        # 1.000 TL Soruları
        {"soru": "İstanbul kaç yılında Fatih Sultan Mehmet tarafından fethedilmiştir?", "secenekler": ["A) 1299", "B) 1453", "C) 1517", "D) 1923"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Türkiye Cumhuriyeti hangi yıl kurulmuştur?", "secenekler": ["A) 1919", "B) 1920", "C) 1923", "D) 1938"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Çanakkale Deniz Zaferi hangi ay ve günde kutlanır?", "secenekler": ["A) 18 Mart", "B) 23 Nisan", "C) 19 Mayıs", "D) 30 Ağustos"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Osmanlı Devleti'nin kurucusu kimdir?", "secenekler": ["A) Orhan Bey", "B) Osman Bey", "C) Ertuğrul Gazi", "D) I. Murad"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Türkiye Büyük Millet Meclisi (TBMM) hangi ilimizde açılmıştır?", "secenekler": ["A) İstanbul", "B) İzmir", "C) Ankara", "D) Sivas"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "İstiklal Marşı'mızın şairi kimdir?", "secenekler": ["A) Mehmet Akif Ersoy", "B) Namık Kemal", "C) Yahya Kemal", "D) Ziya Gökalp"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Atatürk'ün doğduğu şehir hangisidir?", "secenekler": ["A) Ankara", "B) Selanik", "C) İstanbul", "D) İzmir"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Cumhuriyetin ilk yıllarında başkent neresi olmuştur?", "secenekler": ["A) İstanbul", "B) İzmir", "C) Ankara", "D) Bursa"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "30 Ağustos Zafer Bayramı hangi büyük savaştan sonra kutlanmaya başlanmıştır?", "secenekler": ["A) Sakarya", "B) Büyük Taarruz (Dumlupınar Meydan Muharebesi)", "C) İnönü", "D) Çanakkale"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Türk kadınlarına seçme ve seçilme hakkı hangi yıl verilmiştir?", "secenekler": ["A) 1923", "B) 1930", "C) 1934", "D) 1926"], "cevap": "c", "odul": "1.000 TL"},
        # 10.000 TL Soruları
        {"soru": "Türkiye Cumhuriyeti'nin ilk başbakanı kimdir?", "secenekler": ["A) İsmet İnönü", "B) Celâl Bayar", "C) Fevzi Çakmak", "D) Kazım Karabekir"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Osmanlı Devleti'nde ilk basımevi (matbaa) hangi padişah döneminde kurulmuştur?", "secenekler": ["A) Kanuni Sultan Süleyman", "B) III. Ahmet (Lale Devri)", "C) II. Mahmut", "D) Yavuz Sultan Selim"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "I. Dünya Savaşı'nı resmi olarak sona erdiren anlaşma hangisidir?", "secenekler": ["A) Sevr", "B) Lozan", "C) Versay", "D) Paris"], "cevap": "c", "odul": "10.000 TL"},
        {"soru": "Ankara hangi yıl Türkiye Cumhuriyeti'nin başkenti ilan edilmiştir?", "secenekler": ["A) 1920", "B) 1922", "C) 1923", "D) 1924"], "cevap": "c", "odul": "10.000 TL"},
        {"soru": "Osmanlı'nın balkanlardaki hakimiyetini büyük ölçüde kesinleştiren savaş hangisidir?", "secenekler": ["A) Kosova Savaşı", "B) Niğbolu Savaşı", "C) Varna Savaşı", "D) Sırpsındığı Savaşı"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Hatay anavatana hangi yıl katılmıştır?", "secenekler": ["A) 1923", "B) 1938", "C) 1939", "D) 1945"], "cevap": "c", "odul": "10.000 TL"},
        {"soru": "Türkiye'nin çok partili siyasi hayata geçiş sürecinde kurulan ilk muhalefet partisi hangisidir?", "secenekler": ["A) Demokrat Parti", "B) Serbest Cumhuriyet Fırkası", "C) Terakkiperver Cumhuriyet Fırkası", "D) Millet Partisi"], "cevap": "c", "odul": "10.000 TL"},
        {"soru": "Kurtuluş Savaşı'nı kazandıran ve Doğu sınırımızı çizen anlaşma hangisidir?", "secenekler": ["A) Gümrü Anlaşması", "B) Moskova Anlaşması", "C) Kars Anlaşması", "D) Hepsi"], "cevap": "d", "odul": "10.000 TL"},
        {"soru": "Osmanlı İmparatorluğu'nda 'Nizami Cedid' askeri reformunu başlatan padişah kimdir?", "secenekler": ["A) III. Selim", "B) II. Mahmud", "C) Abdülaziz", "D) IV. Murad"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Türk tarihinde demiryolu ağlarının devletleştirilmesi ve milli iktisat politikalarıyla bilinen dönem hangisidir?", "secenekler": ["A) Meşrutiyet Dönemi", "B) Atatürk Dönemi (1923-1938)", "C) Tanzimat Dönemi", "D) Fetret Devri"], "cevap": "b", "odul": "10.000 TL"},
        # 50.000 TL Soruları
        {"soru": "Mustafa Kemal Atatürk'e 'Gazi' unvanı hangi savaştan sonra verilmiştir?", "secenekler": ["A) Çanakkale Savaşı", "B) Sakarya Meydan Muharebesi", "C) Büyük Taarruz", "D) I. İnönü Savaşı"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Kanuni Sultan Süleyman'ın hayatını kaybettiği ve tahttan inmeden önceki son seferi hangisidir?", "secenekler": ["A) Mohaç", "B) Zigetvar Seferi", "C) Viyana Kuşatması", "D) Rodos Seferi"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Osmanlı Devleti'nde 'Senedi İttifak' hangi padişah zamanında ayanlarla imzalanmıştır?", "secenekler": ["A) II. Mahmut", "B) III. Selim", "C) Abdülmecid", "D) Abdülaziz"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Milli Mücadele döneminde Amasya Genelgesi'nde yer alan hangi karar ihtilal bildirisi niteliğindedir?", "secenekler": ["A) Vatanın bütünlüğü milletin bağımsızlığı tehlikededir", "B) İstanbul hükümeti sorumluluğunu taşımaktadır", "C) Milletin bağımsızlığını yine milletin azim ve kararı kurtaracaktır", "D) Sivas'ta kongre toplanacaktır"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Osmanlı Devleti'nin dağılma döneminde azınlıklara geniş haklar tanıyarak dağılmayı önlemeyi amaçlayan ferman hangisidir?", "secenekler": ["A) Tanzimat Fermanı", "B) Islahat Fermanı", "C) Senedi İttifak", "D) Kanunu Esasi"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Trablusgarp Savaşı'nda Mustafa Kemal ve diğer Türk subayları gizlice kılıç kılıkta hangi takma adlarla savaşmıştır?", "secenekler": ["A) Gazeteci Şerif / Binbaşı Enver", "B) Doktor Şerif", "C) Ali Çavuş", "D) Ahmet Efendi"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Lozan Barış Antlaşması'nda Türkiye'yi temsil eden baş murahhas (baş delege) kimdir?", "secenekler": ["A) İsmet İnönü", "B) Rauf Orbay", "C) Celal Bayar", "D) Yusuf Kemal Bey"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Osmanlı Devleti'nin ilk yazılı anayasası olan 'Kanun-i Esasi' hangi yıl ilan edilmiştir?", "secenekler": ["A) 1839", "B) 1856", "C) 1876", "D) 1908"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "II. Abdülhamit döneminde tahttan indirilmesine yol açan ve 31 Mart Vakası'nı bastıran ordunun adı nedir?", "secenekler": ["A) Hareket Ordusu", "B) Yıldırım Ordusu", "C) Kuva-yı Milliye", "D) Nizam-ı Cedid"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Büyük Taarruz sırasında başkomutanlık yetkisini üstlenen Mustafa Kemal Paşa'nın bu görevi süresiz olarak ilk kez uzatıldığı yer neresidir?", "secenekler": ["A) Ankara", "B) Akşehir", "C) Afyon", "D) İzmir"], "cevap": "b", "odul": "50.000 TL"},
        # 250.000 TL Soruları
        {"soru": "Türk tarihinde 'Yurt Açan Savaş' olarak bilinen ve Anadolu'nun kapılarını Türklere açan savaş hangisidir?", "secenekler": ["A) Miryokefalon", "B) Malazgirt", "C) Dandanakan", "D) Pasinler"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Anadolu'da Türk siyasi birliğini ilk kez büyük ölçüde sağlayan ve Osmanlı'ya Ankara Savaşı'nı kazandıran Timur ile Yıldırım Bayezid'in savaştığı yer neresidir?", "secenekler": ["A) Çubuk Ovası", "B) Sazlıdere", "C) Otlukbeli", "D) Varna"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Osmanlı Devleti'nde 17. yüzyılda maliyeyi düzeltmek için ilk kez denk bütçe hazırlayan ve saray masraflarını kısıtlayan ünlü sadrazam kimdir?", "secenekler": ["A) Köprülü Fazıl Ahmed Paşa", "B) Tarhuncu Ahmet Paşa", "C) Sokollu Mehmet Paşa", "D) Merzifonlu Kara Mustafa Paşa"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Mustafa Kemal Paşa'nın Samsun'a çıkış görev emrinde kendisine verilen resmi unvan nedir?", "secenekler": ["A) 9. Ordu Müfettişi", "B) Yıldırım Orduları Komutanı", "C) Anadolu Generali", "D) Başkomutan"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "1921 Anayasası'nın (Teşkilat-ı Esasiye) en önemli özelliklerinden biri hangisidir?", "secenekler": ["A) Laikliği benimsemesi", "B) Güçler ayrılığı ilkesini savunması", "C) Güçler birliği ve Meclis hükümeti sistemini benimsemesi", "D) Kadınlara seçme hakkı vermesi"], "cevap": "c", "odul": "250.000 TL"},
        {"soru": "Osmanlı Devleti'nde 'Gedik' sistemi neyi ifade eder?", "secenekler": ["A) Askeri ocak sistemi", "B) Esnaf ve dükkan açma ruhsatı / tekel hakkı", "C) Toprak dağıtım sistemi", "D) Vergi toplama hakkı"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Milli Mücadele yıllarında Batı Cephesi komutanlığı ikiye ayrıldığında Kuzey Cephesi komutanı kim olmuştur?", "secenekler": ["A) İsmet İnönü", "B) Refet Bele", "C) Ali Fuat Cebesoy", "D) Fevzi Çakmak"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Osmanlı İmparatorluğu'nda ilk kez 'Mebusan Meclisi'nin açılmasına imkan veren dönemin fikir akımı hangisidir?", "secenekler": ["A) Türkçülük", "B) Osmanlıcılık", "C) İslamcılık", "D) Batıcılık"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "1936 yılında boğazların egemenliğini Türkiye'ye tam olarak veren uluslararası antlaşma hangisidir?", "secenekler": ["A) Montrö Boğazlar Sözleşmesi", "B) Lozan Barış Antlaşması", "C) Sevr Antlaşması", "D) Londra Boğazlar Sözleşmesi"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "II. Mahmud döneminde yeniçeri ocağının kaldırılması olayı tarihte ne olarak anılır?", "secenekler": ["A) Vakayı Hayriye (Hayırlı Olay)", "B) 31 Mart Vakası", "C) Kuleli Vakası", "D) Çınar Vakası"], "cevap": "a", "odul": "250.000 TL"},
        # 1.000.000 TL Soruları
        {"soru": "Osmanlı İmparatorluğu'nun kuruluş yılı resmi olarak genellikle hangi yıl kabul edilir?", "secenekler": ["A) 1299", "B) 1302", "C) 1453", "D) 1071"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Osmanlı Devleti'nde padişahın mutlak yetkilerini sınırlandıran ve tahta çıkışını yasalarla bağlayan ilk ve tek belge hangisidir?", "secenekler": ["A) Senedi İttifak", "B) Tanzimat Fermanı", "C) Islahat Fermanı", "D) Kanun-i Esasi"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Tarihte 'Yüzyıl Savaşları' hangi iki devlet arasında gerçekleşmiştir?", "secenekler": ["A) İngiltere ve Fransa", "B) Osmanlı ve Venedik", "C) Rusya ve İsveç", "D) İspanya ve Portekiz"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Bizans İmparatorluğu'nun son toprak parçasını oluşturan ve Fatih Sultan Mehmet tarafından 1461'de fethedilen Rum İmparatorluğu hangisidir?", "secenekler": ["A) Trabzon İmparatorluğu", "B) İznik İmparatorluğu", "C) Mora Despotluğu", "D) Epir Despotluğu"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Kurtuluş Savaşı sırasında İtalyanların işgal edip sonradan hiç dirençle karşılaşmadan terk ettiği stratejik Güneybatı şehri hangisidir?", "secenekler": ["A) Antalya / Bodrum bölgesi", "B) Adana", "C) Antep", "D) Maraş"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Osmanlı Devleti'nde 'İltizam' sisteminin kaldırılmasıyla birlikte vergilerin devlet memurları eliyle doğrudan toplanması sistemine ne ad verilmiştir?", "secenekler": ["A) Muhassıllık sistemi", "B) Tımar sistemi", "C) Malikane sistemi", "D) Dirlik sistemi"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Tarihte ilk yazılı antlaşma olan ve Hititler ile Mısırlılar arasında imzalanan antlaşmanın adı nedir?", "secenekler": ["A) Kadeş Antlaşması", "B) Apameia Antlaşması", "C) Zitvatorok Antlaşması", "D) Küçük Kaynarca"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Mustafa Kemal Atatürk'ün Nutuk adlı eserini hangi yılları arasını kapsayacak şekilde kaleme almıştır?", "secenekler": ["A) 1919 - 1927", "B) 1920 - 1930", "C) 1914 - 1923", "D) 1923 - 1938"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Dünya tarihini değiştiren Fransız İhtilali hangi yıl gerçekleşmiştir?", "secenekler": ["A) 1789", "B) 1489", "C) 1815", "D) 1776"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Osmanlı Devleti'nde 'Şeyhülislam'lık makamı ilk kez hangi padişah döneminde kurulmuştur?", "secenekler": ["A) I. Murad", "B) Orhan Bey", "C) Yıldırım Bayezid", "D) Fatih Sultan Mehmet"], "cevap": "b", "odul": "1.000.000 TL"}
    ],
    "coğrafya": [
        # 1.000 TL Soruları
        {"soru": "Türkiye'nin yüz ölçümü bakımından en büyük ili hangisidir?", "secenekler": ["A) Ankara", "B) Sivas", "C) Konya", "D) Van"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Türkiye'nin başkenti neresidir?", "secenekler": ["A) İstanbul", "B) İzmir", "C) Ankara", "D) Bursa"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Dünya'nın şekli kutuplardan basık, ekvatordan şişkin olan bu kendine has geometrik biçimine ne ad verilir?", "secenekler": ["A) Küre", "B) Geoit", "C) Elips", "D) Silindir"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Türkiye'nin hangi bölgesi en çok yağış alır?", "secenekler": ["A) İç Anadolu", "B) Karadeniz", "C) Güneydoğu Anadolu", "D) Ege"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Yeryüzündeki en büyük okyanus hangisidir?", "secenekler": ["A) Atlas Okyanusu", "B) Hint Okyanusu", "C) Pasifik (Büyük Okyanus)", "D) Arktik Okyanusu"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Türkiye'nin komşularından biri olmayan ülke hangisidir?", "secenekler": ["A) Yunanistan", "B) İran", "C) Mısır", "D) Bulgaristan"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Van Gölü hangi coğrafi bölgemizde yer alır?", "secenekler": ["A) İç Anadolu", "B) Doğu Anadolu", "C) Akdeniz", "D) Karadeniz"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Haritalarda yükseltisi aynı olan noktaları birleştiren eğrilere ne ad verilir?", "secenekler": ["A) İzohips", "B) Ekvator", "C) Meridyen", "D) Paralel"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Türkiye'nin en uzun akarsuyu hangisidir?", "secenekler": ["A) Kızılırmak", "B) Fırat", "C) Yeşilırmak", "D) Sakarya"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Dünya üzerinde kaç ana yön vardır?", "secenekler": ["A) 2", "B) 4", "C) 8", "D) 12"], "cevap": "b", "odul": "1.000 TL"},
        # 10.000 TL Soruları
        {"soru": "Türkiye'nin en yüksek dağı olan Ağrı Dağı hangi ilimiz sınırları içerisindedir?", "secenekler": ["A) Erzurum", "B) Van", "C) Iğdır / Ağrı", "D) Kars"], "cevap": "c", "odul": "10.000 TL"},
        {"soru": "Akdeniz ikliminin görüldüğü yerlerde yaz mevsimi nasıl geçer?", "secenekler": ["A) Sıcak ve kurak", "B) Ispanaklı ve yağışlı", "C) Soğuk ve karlı", "D) Sürekli sisli"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Türkiye'nin en büyük gölü olan Van Gölü hangi tür bir göldür?", "secenekler": ["A) Tektonik göl", "B) Volkanik set gölü", "C) Heyelan set gölü", "D) Karstik göl"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Avrupa ile Asya kıtalarını birbirinden ayıran doğal dağ sırası hangisidir?", "secenekler": ["A) Alpler", "B) Toroslar", "C) Ural Dağları", "D) Himalaya Dağları"], "cevap": "c", "odul": "10.000 TL"},
        {"soru": "Türkiye'nin en çok buğday üreten bölgesi hangisidir?", "secenekler": ["A) Karadeniz", "B) İç Anadolu", "C) Ege", "D) Akdeniz"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Dünyanın en tuzlu deniz veya göllerinden biri olan ve su üstünde batmadan durulabilen 'Ölüdeniz' (Lut Gölü) hangi ülkeler arasındadır?", "secenekler": ["A) Mısır - Libya", "B) İsrail - Ürdün", "C) Türkiye - Yunanistan", "D) İtalya - İspanya"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Türkiye'nin en batı ucunda yer alan ilçe hangisidir?", "secenekler": ["A) Gökçeada", "B) Çeşme", "C) Bozcaada", "D) Datça"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Muson iklimi dünyada en belirgin hangi kıtada görülür?", "secenekler": ["A) Avrupa", "B) Güney ve Güneydoğu Asya", "C) Kuzey Amerika", "D) Avustralya"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Türkiye'de çay tarımı en çok hangi bölgemizde ve ilimizde yapılır?", "secenekler": ["A) Akdeniz / Antalya", "B) Karadeniz / Rize", "C) Ege / Aydın", "D) Marmara / Yalova"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Dünya'nın kendi ekseni etrafındaki dönüş yönü batıdan doğuya doğrudur. Bu durumun sonuçlarından biri hangisidir?", "secenekler": ["A) Güneş'in doğuda daha erken doğması", "B) Mevsimlerin oluşması", "C) Gece gündüz süresinin değişmesi", "D) Muson rüzgarları"], "cevap": "a", "odul": "10.000 TL"},
        # 50.000 TL Soruları
        {"soru": "Dünyanın en uzun nehirleri arasında gösterilen Nil Nehri hangi kıtada yer alır?", "secenekler": ["A) Asya", "B) Afrika", "C) Güney Amerika", "D) Avrupa"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Türkiye'de karstik arazilerin (kireçtaşı, jips) en yaygın olduğu bölgemiz hangisidir?", "secenekler": ["A) Marmara", "B) Akdeniz Bölgesi", "C) Doğu Anadolu", "D) Karadeniz"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Fay hatları ile sıcak su kaynaklarının (jeotermal) en yoğun olduğu bölgemiz hangisidir?", "secenekler": ["A) Ege Bölgesi", "B) İç Anadolu", "C) Karadeniz", "D) Güneydoğu Anadolu"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Atmosferin yerden yükseldikçe sıcaklığın her 100 metrede ortalama 0.5 derece azalmasının temel sebebi nedir?", "secenekler": ["A) Güneş'e yaklaşmak", "B) Yerden yansıyan ısı ile ısınması", "C) Rüzgar hızı", "D) Nem oranı"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Türkiye'nin en çok ihracat yaptığı limanlardan biri olan ve körfeziyle bilinen Ege limanı hangisidir?", "secenekler": ["A) İzmir Limanı", "B) Samsun Limanı", "C) Sinop Limanı", "D) Trabzon Limanı"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Dünya üzerinde sürekli esen ters alizeler ile alizeler arasında kalan ve çöllerin bulunduğu kuşak genel olarak hangi enlemlerdir?", "secenekler": ["A) Ekvator", "B) 30 derece enlemleri (Dönenceler çevresi)", "C) Kutuplar", "D) 60 derece enlemleri"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Türkiye'nin maden çeşitliliği bakımından en zengin bölgesi hangisidir?", "secenekler": ["A) Doğu Anadolu Bölgesi", "B) Marmara", "C) Ege", "D) Karadeniz"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Sibirya yüksek basınç merkezinin kış aylarında Türkiye üzerinde etkili olması ne tür hava koşullarına yol açar?", "secenekler": ["A) Aşırı soğuk, ayaz ve kar yağışı", "B) Bol yağmur ve lodos", "C) Sıcak ve kurak hava", "D) Fırtına"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Yeryüzünde volkanik patlamalarla oluşan toprakların tarımsal açıdan çok verimli olmasının sebebi nedir?", "secenekler": ["A) Bol mineral ve kül içermesi", "B) Çok tuzlu olması", "C) Sürekli ıslak kalması", "D) Kumu çok az olması"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Türkiye'nin en çok rüzgar enerjisi santraline (RES) sahip olan coğrafi bölgesi hangisidir?", "secenekler": ["A) Ege Bölgesi", "B) Karadeniz", "C) Akdeniz", "D) İç Anadolu"], "cevap": "a", "odul": "50.000 TL"},
        # 250.000 TL Soruları
        {"soru": "Hangi kıta yüz ölçümü bakımından dünyanın en küçük kıtasıdır?", "secenekler": ["A) Avrupa", "B) Antarktika", "C) Okyanusya (Avustralya)", "D) Güney Amerika"], "cevap": "c", "odul": "250.000 TL"},
        {"soru": "Dünya üzerinde 'Tarih Değiştirme Çizgisi' hangi meridyen üzerinden geçer?", "secenekler": ["A) 0 derece Greenwich", "B) 180 derece meridyeni", "C) 90 derece doğu", "D) 45 derece batı"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Türkiye'de fiziki haritalarda 'kahverengi' ve tonları neyi ifade eder?", "secenekler": ["A) 1500 metre ve üzeri yüksek dağlık alanları", "B) Ormanları", "C) Denizleri", "D) Ovaları"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Aşağıdaki akarsulardan hangisi Türkiye dışından doğup Türkiye sınırları içerisinden denize dökülür?", "secenekler": ["A) Kızılırmak", "B) Çoruh", "C) Aras", "D) Meriç"], "cevap": "d", "odul": "250.000 TL"},
        {"soru": "Amazon Ormanları dünyada en çok hangi iklim tipinin etkisindedir?", "secenekler": ["A) Ekvatoral İklim", "B) Savan İklimi", "C) Tundra", "D) Akdeniz İklimi"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Türkiye'nin en genç volkanik dağı olarak bilinen ve Manisa'da yer alan dağ hangisidir?", "secenekler": ["A) Kula Volkanları (Menatepeler)", "B) Ağrı Dağı", "C) Erciyes", "D) Nemrut"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Dünya üzerinde okyanus akıntılarının oluşmasında en temel faktörlerden biri hangisidir?", "secenekler": ["A) Sürekli rüzgarlar (Alizeler) ve Dünya'nın dönmesi", "B) Ay'ın çekim gücü", "C) Depremler", "D) Bulutlar"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Türkiye'de 'Bölgesel Kalkınma Projeleri' arasında yer alan ve GAP'tan sonra hayata geçirilen en büyük projelerden biri olan DOKAP hangi bölgeyi kapsar?", "secenekler": ["A) Doğu Karadeniz Projesi", "B) Doğu Anadolu Projesi", "C) Konya Ovası Projesi", "D) Yeşilırmak Havzası"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Norveç ve Şili kıyılarında görülen, buzul aşındırmasıyla oluşmuş derin körfezli kıyı tiplerine ne ad verilir?", "secenekler": ["A) Fiyortlı kıyı", "B) Haliçli kıyı", "C) Ria tipi kıyı", "D) Dalmaçya tipi kıyı"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Türkiye'de orman varlığımızın en az olduğu coğrafi bölgemiz hangisidir?", "secenekler": ["A) İç Anadolu Bölgesi", "B) Güneydoğu Anadolu", "C) Doğu Anadolu", "D) Marmara"], "cevap": "b", "odul": "250.000 TL"},
        # 1.000.000 TL Soruları
        {"soru": "Dünyanın en derin okyanus çukuru olan 'Mariana Çukuru' hangi okyanusta yer alır?", "secenekler": ["A) Atlas Okyanusu", "B) Hint Okyanusu", "C) Pasifik (Büyük) Okyanus", "D) Arktik Okyanusu"], "cevap": "c", "odul": "1.000.000 TL"},
        {"soru": "Alfred Wegener'in ortaya atıp kıtaların kaymasını savunan ünlü teorisinin adı nedir?", "secenekler": ["A) Kıta Sürüklenmesi (Pangea / Levha Tektoniği teorisi)", "B) Atmosferik Basınç Teorisi", "C) Küresel Isınma Modeli", "D) Okyanus Akıntıları Teorisi"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Dünya üzerinde 'Sargasso Denizi'ni diğer denizlerden ayıran en büyük ve ilginç coğrafi özellik nedir?", "secenekler": ["A) Kıyısı olmayan, devasa yosunlarla kaplı okyanus ortasındaki deniz olması", "B) Dünyanın en tuzlu yeri olması", "C) Tamamen donmuş olması", "D) Çok derin bir çukur olması"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Türkiye'nin en kuzey noktası olan Sinop İnceburun ile en güney noktası Hatay Beysun arasındaki kuş uçuşu mesafe yaklaşık kaç kilometredir?", "secenekler": ["A) 666 km", "B) 1000 km", "C) 1250 km", "D) 1500 km"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Güneş ışınlarının yılda iki kez (21 Mart ve 23 Eylül'de) dik açıyla düştüğü özel enlemin adı nedir?", "secenekler": ["A) Ekvator", "B) Yengeç Dönencesi", "C) Oğlak Dönencesi", "D) Kutup Dairesi"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Cebelitarık Boğazı hangi iki su kütlesini birbirine bağlar?", "secenekler": ["A) Atlas Okyanusu ile Akdeniz", "B) Karadeniz ile Ege", "C) Kızıldeniz ile Hint Okyanusu", "D) Pasifik ile Atlas"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Dünya'nın merkezindeki çekirdeğin katı olmasındaki ana fiziksel etken nedir?", "secenekler": ["A) Devasa basınç altında kalması", "B) Çok soğuk olması", "C) Saf demirden oluşmaması", "D) Manyetik alan olmaması"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Antarktika kıtasında bulunan ve buzulların altında yer alan dünyanın en büyük subglacial gölünün adı nedir?", "secenekler": ["A) Vostok Gölü", "B) Baikal Gölü", "C) Titicaca Gölü", "D) Superior Gölü"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Türkiye'nin matematik konumuna göre yıl içinde yaşadığı mevsim değişmelerinin temel nedeni nedir?", "secenekler": ["A) Eksen Eğikliği ve Yıllık Hareket", "B) Günlük hareket", "C) Yükselti", "D) Karasallık"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Dünya haritasında en az bozulma gösteren harita projeksiyon yöntemi hangisidir?", "secenekler": ["A) Silindirik / Merkator projeksiyonu", "B) Düzlem projeksiyon", "C) Konik projeksiyon", "D) Küresel projeksiyon"], "cevap": "a", "odul": "1.000.000 TL"}
    ],
    "müzik": [
        # 1.000 TL Soruları
        {"soru": "Müzik notalarında 'sol anahtarı' portenin kaçıncı çizgisinden başlar?", "secenekler": ["A) 1. Çizgi", "B) 2. Çizgi", "C) 3. Çizgi", "D) 4. Çizgi"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Müzikte en temel nota serisi (Do, Re, Mi...) toplam kaç tanedir?", "secenekler": ["A) 5", "B) 7", "C) 8", "D) 12"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Gitar kaç telli bir müzik aletidir (standart akustik/klasik)?", "secenekler": ["A) 4", "B) 6", "C) 8", "D) 12"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Piyanoda toplam kaç tuş bulunur (standart)?", "secenekler": ["A) 64", "B) 88", "C) 100", "D) 120"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Bağlama (saz) hangi çalgı grubuna aittir?", "secenekler": ["A) Telli çalgılar", "B) Vurmalı", "C) Üflemeli", "D) Yaylı"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Müzikte hızı ve tempoyu belirten İtalyanca terimlere ne denir?", "secenekler": ["A) Ritim", "B) Tempo / Metronom", "C) Nota", "D) Akor"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Türk halk müziğinin en önemli üflemeli çalgılarından biri hangisidir?", "secenekler": ["A) Kaval / Zurna", "B) Keman", "C) Piyano", "D) Bateri"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Rock müzikte ritmi ve tempoyu tutan temel vurmalı çalgı seti nedir?", "secenekler": ["A) Bateri (Davul)", "B) Flüt", "C) Saz", "D) Çello"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Pop müzik ne anlama gelir?", "secenekler": ["A) Popüler müzik", "B) Klasik müzik", "C) Caz müziği", "D) Opera"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Bir eserin en yüksek sesli halini ifade eden müzik terimi nedir?", "secenekler": ["A) Fortissimo (ff)", "B) Pianissimo (pp)", "C) Allegro", "D) Largo"], "cevap": "a", "odul": "1.000 TL"},
        # 10.000 TL Soruları
        {"soru": "Aşağıdaki enstrümanlardan hangisi yaylı çalgılar grubuna girer?", "secenekler": ["A) Flüt", "B) Viyolonsel (Çello)", "C) Klarnet", "D) Trompet"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Türk sanat müziğinde makamları yöneten ve baş çalgıcı olan sanatçıya ne denir?", "secenekler": ["A) Solist", "B) Başkement", "C) Sazende / Neyzen", "D) Şef / Konser Masteri"], "cevap": "d", "odul": "10.000 TL"},
        {"soru": "Mozart hangi dönem müzik akımının en büyük dehalarından biridir?", "secenekler": ["A) Klasik Dönem", "B) Romantik Dönem", "C) Modern Dönem", "D) Barok Dönem"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Beethoven'ın sağır olmasına rağmen bestelediği ve içinde 'Neşeye Övgü' korosunun bulunduğu ünlü senfonisi hangisidir?", "secenekler": ["A) 5. Senfoni", "B) 9. Senfoni", "C) 3. Senfoni", "D) 7. Senfoni"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Müzikte aynı anda seslendirilen üç veya daha fazla notanın oluşturduğu uyumlu ses kümesine ne denir?", "secenekler": ["A) Akor", "B) Melodi", "C) Ritim", "D) Solfej"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Türk halk müziğinde türkülerin derlenmesinde ve bağlama üstadlığında çığır açmış 'Yalan Dünya' gibi eserlerin sahibi halk ozanı kimdir?", "secenekler": ["A) Neşet Ertaş", "B) Aşık Veysel", "C) Barış Manço", "D) Cem Karaca"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Caz müziğinin doğduğu ülke ve şehir neresidir?", "secenekler": ["A) ABD / New Orleans", "B) Fransa / Paris", "C) İngiltere / Londra", "D) İtalya / Venedik"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Opera eserlerinde orkestrayı yöneten sanatçıya ne ad verilir?", "secenekler": ["A) Kondüktör (Şef)", "B) Prodüktör", "C) Tenor", "D) Soprano"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Dört telli küçük gitar benzeri ve Hawaii kökenli çalgının adı nedir?", "secenekler": ["A) Ukulele", "B) Banjo", "C) Mandolin", "D) Arp"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Müzikte seslerin tizleştiğini veya pesleştiğini gösteren işaretlere ne denir?", "secenekler": ["A) Diyez (#) ve Bemol (b)", "B) Nokta", "C) Çizgi", "D) Ünlem"], "cevap": "a", "odul": "10.000 TL"},
        # 50.000 TL Soruları
        {"soru": "Klasik batı müziğinde 'en yavaş' tempo terimi aşağıdakilerden hangisidir?", "secenekler": ["A) Allegro", "B) Andante", "C) Largo", "D) Presto"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Barok müziğin en büyük dâhilerinden biri olan ve 'Toccata ve Fuga' eserleriyle bilinen Alman besteci kimdir?", "secenekler": ["A) J. S. Bach", "B) Vivaldi", "C) Chopin", "D) Liszt"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Türk müziğinde 'Aşık Veysel'in gözlerini kaybetmesine sebep olan çocukluk hastalığı nedir?", "secenekler": ["A) Kızamık", "B) Çiçek hastalığı", "C) Suçiçeği", "D) Verem"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Senfoni orkestralarında üflemeli çalgılar grubunun en tiz sesli metal üyesi hangisidir?", "secenekler": ["A) Flüt / Obua", "B) Trompet", "C) Korno", "D) Tuba"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Müzikte 'polifoni' terimi ne anlama gelir?", "secenekler": ["A) Çok seslilik", "B) Tek seslilik", "C) Hızlı çalma", "D) Sessiz olma"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Gitarda tellere tırnak veya pena ile vurularak yapılan hızlı çalma tekniğine ne denir?", "secenekler": ["A) Strumming / Picking", "B) Slap", "C) Bending", "D) Hammer-on"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Antonio Vivaldi'nin en ünlü keman konçertosu serisi hangisidir?", "secenekler": ["A) Dört Mevsim", "B) Gece Müzikleri", "C) Fırtına", "D) Requiem"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Türk sanat müziğinde 'Dede Efendi' olarak bilinen ve klasik eserleriyle tanınan bestecinin asıl adı nedir?", "secenekler": ["A) Hammamizade İhsan", "B) İsmail Dede Efendi (Hammamizade İsmail Efendi)", "C) Itri", "D) Zekai Dede"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Piyanoda siyah tuşların dizilimi klavyede nasıl bir düzene sahiptir?", "secenekler": ["A) İkili ve üçlü gruplar halinde", "B) Tek tek aralıklı", "C) Sadece ortada", "D) Tamamen rastgele"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Müzik teorisinde bir oktav içinde kaç adet yarı ton (yarım ses) bulunur?", "secenekler": ["A) 6", "B) 8", "C) 12", "D) 24"], "cevap": "c", "odul": "50.000 TL"},
        # 250.000 TL Soruları
        {"soru": "Türkiye'de 'Dönence' ve 'Aldırma Gönül' gibi unutulmaz eserlere imza atmış Anadolu Rock grubu hangisidir?", "secenekler": ["A) Duman", "B) Moğollar", "C) MFÖ", "D) Athena"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Frédéric Chopin piyano için yazdığı eserlerin neredeyse tamamında hangi enstrümana odaklanmıştır?", "secenekler": ["A) Piyano", "B) Keman", "C) Çello", "D) Flüt"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Geleneksel Türk müziğinde kullanılan ve çeyrek sesleri (komaları) veren en küçük perde birimine ne ad verilir?", "secenekler": ["A) Koma", "B) Diyez", "C) Nota", "D) Perde"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Rock müziğin efsanevi gitaristlerinden biri olan ve dişleriyle gitar çalarak ün salan 'Purple Haze' şarkısının sahibi kimdir?", "secenekler": ["A) Jimi Hendrix", "B) Eric Clapton", "C) Jimmy Page", "D) Slash"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Müzikte bir eserin yavaş yavaş sesinin açılması (kısık sesten yükseğe) terimine ne denir?", "secenekler": ["A) Crescendo", "B) Decrescendo", "C) Staccato", "D) Legato"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Ünlü Alman besteci Richard Wagner'in opera eserlerinde sıklıkla kullandığı ve belirli bir karaktere veya nesneye atlettiği kısa müzik cümlelerine ne denir?", "secenekler": ["A) Leitmotif", "B) Aria", "C) Overture", "D) Rondo"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Türk müzik tarihinde 'Devlet Sanatçısı' unvanını alan ilk kadın opera sanatçımız kimdir?", "secenekler": ["A) Semiha Berksoy", "B) Leyla Gencer", "C) Suna Korad", "D) Pervin Çakar"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Müzik teorisinde iki nota arasındaki frekans oranının bir oktav olması durumunda frekanslar arasındaki matematiksel oran nasıldır?", "secenekler": ["A) Frekans iki katına çıkar (2:1 oranı)", "B) Frekans yarıya düşer", "C) Aynı kalır", "D) Dört katına çıkar"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Pink Floyd'un ikonik albümü 'The Dark Side of the Moon' kapağındaki optik olay nedir?", "secenekler": ["A) Prizmadan geçen beyaz ışığın gökkuşağı renklerine ayrılması", "B) Ay tutulması", "C) Karanlık oda", "D) Lazer yansıması"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Geleneksel Türk tasavvuf müziğinde Mevlevi ayinlerinde dönerek yapılan ibadetin en önemli eşlikçisi olan üflemeli çalgı hangisidir?", "secenekler": ["A) Ney", "B) Ud", "C) Kanun", "D) Tanbur"], "cevap": "a", "odul": "250.000 TL"},
        # 1.000.000 TL Soruları
        {"soru": "Dünyaca ünlü 'Bohemian Rhapsody' şarkısı hangi efsanevi müzik grubuna aittir?", "secenekler": ["A) The Beatles", "B) Pink Floyd", "C) Queen", "D) Led Zeppelin"], "cevap": "c", "odul": "1.000.000 TL"},
        {"soru": "Johann Sebastian Bach'ın ölümünden sonra uzun süre unutulup 19. yüzyılda 'Matheus Passion' eserini yeniden sahneleyerek Bach'ı dünyaya tekrar tanıtan ünlü Alman besteci kimdir?", "secenekler": ["A) Felix Mendelssohn", "B) Robert Schumann", "C) Johannes Brahms", "D) Franz Schubert"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Osmanlı sarayında 'Muzıka-yı Hümayun' adı verilen bando ve orkestranın gelişiminde en büyük paya sahip olan ve Donizetti Paşa'yı saraya davet eden padişah kimdir?", "secenekler": ["A) II. Mahmut", "B) III. Selim", "C) Abdülaziz", "D) II. Abdülhamit"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Müzik tarihinde 'Atonal' müziğin babası olarak bilinen ve 12 ton sistemini geliştiren Avusturyalı modernist besteci kimdir?", "secenekler": ["A) Arnold Schoenberg", "B) Igor Stravinsky", "C) Claude Debussy", "D) Bela Bartok"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Geleneksel bando ve mehter takımlarında yer alan ve iki küçük zilin birbirine vurulmasıyla çalınan vurmalı çalgının geleneksel adı nedir?", "secenekler": ["A) Zil (Çال)", "B) Davul", "C) Kös", "D) Nakkaş"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "İtalyan müzik terminolojisinde 'ritardando' terimi ne anlama gelir?", "secenekler": ["A) Temponun yavaş yavaş yavaşlaması", "B) Temponun hızlanması", "C) Sesin yükselmesi", "D) Tekrar çalınması"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Dünya müzik tarihinde ilk nota isimlerini (Ut, Re, Mi...) bulan ve ilahi metinlerinin baş harflerinden bu sistemi geliştiren İtalyan müzik teorisyeni rahip kimdir?", "secenekler": ["A) Guido d'Arezzo", "B) Papa Gregorius", "C) Thomas Aquinas", "D) Leonardo da Vinci"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Ludwig van Beethoven'ın tamamı sağır olduktan sonra sesini dahi duyamadan yazıp ilk kez seslendirildiğinde arkasını dönüp alkışları göremediği anlı şanlı eseri hangisidir?", "secenekler": ["A) 9. Senfoni", "B) Moonlight Sonata", "C) Für Elise", "D) Eroica"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Türk müzikolojisinde pentatonik dizilerin Anadolu halk müziğindeki kullanımını inceleyen ve Türk pentatonizmini teorileştiren ünlü müzikolog ve bestecimiz kimdir?", "secenekler": ["A) Ahmet Adnan Saygun", "B) Ulvi Cemal Erkin", "C) Cemal Reşit Rey", "D) Necil Kazım Akses"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Klasik batı müziğinde birden fazla bağımsız sesin veya melodinin aynı anda uyum içinde seslendirilmesi sanatına ne denir?", "secenekler": ["A) Kontrpuan (Polyphony)", "B) Monofoni", "C) Homofoni", "D) Akor dizisi"], "cevap": "a", "odul": "1.000.000 TL"}
    ],
    "futbol": [
        # 1.000 TL Soruları
        {"soru": "Bir futbol maçında kaleci dışında bir oyuncunun elle müdahale etmesi sonucu hakemin verdiği ceza atışı hangisidir?", "secenekler": ["A) Taç", "B) Korner", "C) Penaltı", "D) Endirekt Vuruş"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Resmi bir futbol maçında sahada her iki takımdan toplam kaç futbolcu yer alır?", "secenekler": ["A) 11", "B) 18", "C) 22", "D) 24"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Futbol maçlarında hakemlerin oyunculara gösterdiği cezai kartlar hangi renktendir?", "secenekler": ["A) Kırmızı ve Sarı", "B) Mavi ve Yeşil", "C) Siyah ve Beyaz", "D) Turuncu ve Mor"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Bir futbol maçının normal süresi toplam kaç dakikadır?", "secenekler": ["A) 45 dakika", "B) 60 dakika", "C) 90 dakika", "D) 120 dakika"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Topun kalenin iki direk arasından ve üst direğin altından geçerek çizgiyi tamamen aşması durumunda ne ilan edilir?", "secenekler": ["A) Taç", "B) Gol", "C) Korner", "D) Ofsayt"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Futbolda maçın başlamasını veya duran topları kullandıran hakem çaldığı düdükle neyi başlatır?", "secenekler": ["A) Oyunu", "B) Saati", "C) Skoru", "D) Devreyi"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Bir oyuncu maçta iki sarı kart gördüğünde hakem tarafından hangi kartla cezalandırılır?", "secenekler": ["A) Direkt Kırmızı kart", "B) Mavi kart", "C) Uyarı", "D) Beyaz kart"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Futbol sahasının ortasında yer alan ve başlama vuruşunun yapıldığı dairenin çapı kaç metredir?", "secenekler": ["A) 9.15 metre (Yarıçap)", "B) 5 metre", "C) 20 metre", "D) 15 metre"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Köşe vuruşu (korner) sahanın hangi köşesinden kullanılır?", "secenekler": ["A) Taç çizgisiyle kale çizgisinin kesiştiği köşe", "B) Orta saha", "C) Ceza sahası dışı", "D) Kalenin önü"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Futbolda elle oynamayan tek saha oyuncusu kural olarak kimdir?", "secenekler": ["A) Kaptan", "B) Kaleci", "C) Stoper", "D) Santrafor"], "cevap": "b", "odul": "1.000 TL"},
        # 10.000 TL Soruları
        {"soru": "Türkiye A Milli Futbol Takımı, FIFA Dünya Kupası tarihindeki en iyi derecesi olan üçüncülüğü hangi yılda elde etmiştir?", "secenekler": ["A) 1996", "B) 2002", "C) 2008", "D) 2020"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "UEFA Şampiyonlar Ligi kupasını kazanan ilk ve tek Türk futbol takımı hangisidir?", "secenekler": ["A) Galatasaray", "B) Fenerbahçe", "C) Beşiktaş", "D) Hiçbiri (Türk takımı kazanmadı)"], "cevap": "d", "odul": "10.000 TL"},
        {"soru": "Süper Lig tarihinde en çok şampiyonluk kazanan takım hangisidir?", "secenekler": ["A) Fenerbahçe", "B) Galatasaray", "C) Beşiktaş", "D) Trabzonspor"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Dünya Kupası'nı tarihinde en çok kazanan ülke milli takımı hangisidir?", "secenekler": ["A) Almanya", "B) Arjantin", "C) Brezilya", "D) İtalya"], "cevap": "c", "odul": "10.000 TL"},
        {"soru": "Avrupa Futbol Şampiyonası'nı (EURO 2008) kazanan milli takım hangisidir?", "secenekler": ["A) İspanya", "B) Almanya", "C) Türkiye", "D) İtalya"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Futbolda bir takvim yılında en çok gol atan oyuncuya verilen ödülün adı nedir?", "secenekler": ["A) Altın Top (Ballon d'Or)", "B) Puskas Ödülü", "C) Altın Ayakkabı (European Golden Shoe)", "D) FIFA Yılın Oyuncusu"], "cevap": "c", "odul": "10.000 TL"},
        {"soru": "Fenerbahçe'nin efsanevi golcüsü ve Türk futbolunun 'Lefter' lakaplı unutulmaz oyuncusunun tam adı nedir?", "secenekler": ["A) Lefter Küçükandonyadis", "B) Metin Oktay", "C) Can Bartu", "D) Şenol Güneş"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Galatasaray'ın efsane golcüsü 'Taçsız Kral' lakaplı unutulmaz futbolcusu kimdir?", "secenekler": ["A) Metin Oktay", "B) Hakan Şükür", "C) Arif Erdem", "D) Tanju Çolak"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Dünya futbolunda 'El Clasico' olarak bilinen rekabet hangi iki kulüp arasında oynanır?", "secenekler": ["A) Real Madrid - Barcelona", "B) AC Milan - Inter", "C) Boca Juniors - River Plate", "D) Manchester United - Liverpool"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Futbol maçlarında ofsayt kuralının temel amacı nedir?", "secenekler": ["A) Hücum oyuncusunun rakip kaleye çok yakın beklemesini (avlanmasını) engellemek", "B) Maçı hızlandırmak", "C) Gol sayısını artırmak", "D) Faulleri önlemek"], "cevap": "a", "odul": "10.000 TL"},
        # 50.000 TL Soruları
        {"soru": "Dünyada 'Kral' lakabıyla tanınan ve 3 kez Dünya Kupası kazanan efsanevi Brezilyalı futbolcu kimdir?", "secenekler": ["A) Maradona", "B) Pele", "C) Ronaldinho", "D) Ronaldo Nazario"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Arjantinli efsanevi futbolcu Diego Maradona'nın 1986 Dünya Kupası'nda İngiltere'ye attığı ve el ile vurduğu ünlü gol ne olarak anılır?", "secenekler": ["A) Tanrı'nın Eli (Hand of God)", "B) Yüzyılın Golü", "C) Hayalet Gol", "D) Asrın Vuruşu"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Türkiye'de Süper Lig'de bir sezonda en çok gol atma rekorunu elinde bulunduran futbolcu kimdir?", "secenekler": ["A) Tanju Çolak", "B) Hakan Şükür", "C) Alex de Souza", "D) Mario Jardel"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Avrupa kupalarında kupa kazanan ilk Türk futbol kulübü hangisidir?", "secenekler": ["A) Galatasaray (UEFA Kupası)", "B) Fenerbahçe", "C) Beşiktaş", "D) Trabzonspor"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Dünya futbolunda 'Yılın En Güzel Golü'ne verilen prestijli ödülün adı nedir?", "secenekler": ["A) Puskas Ödülü", "B) Ballon d'Or", "C) Lev Yashin Ödülü", "D) Kopa Ödülü"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "İngiltere Premier Lig'de hiçbir maç kaybetmeden (Yenilgisiz) şampiyon olan ve 'The Invincibles' olarak anılan kulüp hangisidir?", "secenekler": ["A) Arsenal", "B) Manchester United", "C) Chelsea", "D) Manchester City"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Futbolun kurallarını belirleyen ve uluslararası yönetimi üstlenen kuruluşun kısaltılmış adı nedir?", "secenekler": ["A) FIFA", "B) UEFA", "C) IFAB", "D) TFF"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Şampiyonlar Ligi tarihinde en çok gol atan oyuncu kimdir?", "secenekler": ["A) Cristiano Ronaldo", "B) Lionel Messi", "C) Robert Lewandowski", "D) Karim Benzema"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "İtalya Serie A'da bir sezonda en çok gol atma rekorunu kırarak efsaneleşen Arjantinli golcü kimdir?", "secenekler": ["A) Gonzalo Higuain / Ciro Immobile", "B) Gabriel Batistuta", "C) Hernan Crespo", "D) Mauro Icardi"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Futbol oyun kurallarına göre bir taç atışı doğrudan hangi noktadan kullanılmalıdır?", "secenekler": ["A) Topun çıktığı yerden", "B) Orta sahadan", "C) İstediğimiz yerden", "D) Ceza sahasından"], "cevap": "a", "odul": "50.000 TL"},
        # 250.000 TL Soruları
        {"soru": "Hangi futbol kulübü UEFA Şampiyonlar Ligi'ni tarihte en çok kazanan takımdır?", "secenekler": ["A) AC Milan", "B) Barcelona", "C) Real Madrid", "D) Bayern Munich"], "cevap": "c", "odul": "250.000 TL"},
        {"soru": "Galatasaray'ın 2000 yılında Arsenal'i yenerek UEFA Kupası'nı kazandığı final maçı hangi şehirde oynanmıştır?", "secenekler": ["A) Kopenhag", "B) Londra", "C) Paris", "D) Madrid"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "1994 Dünya Kupası finalinde penaltı atışlarında topu auta atarak Brezilya'ya kupayı kazandıran trajik İtalyan futbolcu kimdir?", "secenekler": ["A) Roberto Baggio", "B) Paolo Maldini", "C) Franco Baresi", "D) Alessandro Del Piero"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Futbol tarihinde 'Panenka' penaltısı olarak bilinen ve topun altına hafifçe vurularak kalecinin üzerinden aşırtılması tekniğini ilk kez dünya sahnesine çıkaran futbolcu kimdir?", "secenekler": ["A) Antonin Panenka", "B) Zinedine Zidane", "C) Johan Cruyff", "D) Andrea Pirlo"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Süper Lig'de 'Unvanlı / Yenilgisiz' şampiyon olan ilk takım hangisidir?", "secenekler": ["A) Beşiktaş (1991-1992 sezonu)", "B) Galatasaray", "C) Fenerbahçe", "D) Trabzonspor"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Dünya Kupası tarihinde bir maçta tek başıma 5 gol atma rekorunu elinde bulunduran Rus futbolcu kimdir?", "secenekler": ["A) Oleg Salenko", "B) Gerd Müller", "C) Miroslav Klose", "D) Ronaldo"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Johan Cruyff'un önderliğinde Ajax ve Barcelona'da ekol olan, tüm sahada alan paylaşımına dayalı efsanevi taktik sistemin adı nedir?", "secenekler": ["A) Total Futbol", "B) Catenaccio", "C) Tiki-Taka", "D) Gegenpressing"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Avrupa Şampiyonası tarihinde grup aşamasından çıkıp mucizevi şekilde kupayı kaldıran 'Danimarka Peribocası' hangi yılda gerçekleşmiştir?", "secenekler": ["A) 1992", "B) 2004", "C) 1988", "D) 1976"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Real Madrid'in efsanevi başkanı ve kulübe 'Galacticos' (Yıldızlar topluluğu) dönemini yaşatan efsanevi başkan kimdir?", "secenekler": ["A) Florentino Pérez", "B) Santiago Bernabéu", "C) Joan Laporta", "D) Ramon Calderon"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Futbolda kalecilere geri pas kuralı (kalecinin ayağıyla oynayabilmesi, eliyle tutamaması) FIFA tarafından resmi olarak hangi yıl getirilmiştir?", "secenekler": ["A) 1992", "B) 1986", "C) 1998", "D) 2000"], "cevap": "a", "odul": "250.000 TL"},
        # 1.000.000 TL Soruları
        {"soru": "Uluslararası Futbol Birliği Kurulu kurallarına göre resmi bir maçta bir takımın sahada en az kaç oyuncusu kalırsa maç tatil edilir?", "secenekler": ["A) 5 oyuncu", "B) 6 oyuncu", "C) 7 oyuncu", "D) 9 oyuncu"], "cevap": "c", "odul": "1.000.000 TL"},
        {"soru": "Futbol tarihinde 'Altın Gol' (Golden Goal) kuralının ilk kez resmi bir turnuvada uygulandığı ve uygulayan takımın kazandığı turnuva hangisidir?", "secenekler": ["A) EURO 1996 (Almanya - Çek Cumhuriyeti / Oliver Bierhoff)", "B) Dünya Kupası 1998", "C) EURO 2000", "D) Dünya Kupası 2002"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Brezilya milli takımının efsanevi 1970 Dünya Kupası kadrosunda sağ bek pozisyonunda oynayıp finalde şahane bir gol atan ve kaptanlık yapan futbolcu kimdir?", "secenekler": ["A) Carlos Alberto", "B) Cafu", "C) Dani Alves", "D) Roberto Carlos"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Real Madrid'in Şampiyonlar Ligi'nde üst üste 3 kez (2016, 2017, 2018) kupayı kazandığı dönemin teknik direktörü kimdir?", "secenekler": ["A) Zinedine Zidane", "B) Carlo Ancelotti", "C) Jose Mourinho", "D) Pep Guardiola"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Dünya Kupası tarihinin en erken golünü 2002 yılında Güney Kore'ye karşı 11. saniyede atan milli futbolcumuz kimdir?", "secenekler": ["A) Hakan Şükür", "B) İlhan Mansız", "C) Ümit Davala", "D) Hasan Şaş"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Futbolda 'Catenaccio' taktiğinin temellerini atıp İtalyan savunma kültürünü dünya futboluna kazdıran efsanevi Arjantinli/Fransız teknik direktör kimdir?", "secenekler": ["A) Helenio Herrera", "B) Arrigo Sacchi", "C) Marcello Lippi", "D) Giovanni Trapattoni"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Avrupa Kupa Galipleri Kupası'nı tarihinde kazanan tek İngiliz kulübü olmayıp aynı zamanda bu kupayı müzesine götüren takım hangisidir?", "secenekler": ["A) West Ham United / Manchester City vb. (Kupa 1999'da kapatılmıştır)", "B) Nottingham Forest", "C) Aston Villa", "D) Leeds United"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "1958 Dünya Kupası'nda henüz 17 yaşındayken Brezilya formasıyla gol atıp turnuvaya damga vuran efsane kimdir?", "secenekler": ["A) Pele", "B) Maradona", "C) Eusebio", "D) Cruyff"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Futbol oyun kurallarını denetleyen ve kural değişikliklerini onaylayan IFAB kurulunda toplam kaç üye federasyon/kurum oy hakkına sahiptir?", "secenekler": ["A) 8 üye (4 FIFA, 4 İngiltere/İskoçya/Galler/K.İrlanda)", "B) 4 üye", "C) 12 üye", "D) 20 üye"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Şampiyonlar Ligi finalinde 3-0 öndeyken devre arasında yakalanıp penaltılarda Liverpool'a kaybeden efsanevi İtalyan kulübü hangisidir (İstanbul'daki 2005 mucizesi)?", "secenekler": ["A) AC Milan", "B) Juventus", "C) Inter", "D) Roma"], "cevap": "a", "odul": "1.000.000 TL"}
    ],
    "genel": [
        # 1.000 TL Soruları
        {"soru": "Güneş sistemindeki en büyük gezegen aşağıdakilerden hangisidir?", "secenekler": ["A) Satürn", "B) Jüpiter", "C) Neptün", "D) Mars"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "İnsan vücudundaki en büyük organ hangisidir?", "secenekler": ["A) Kalp", "B) Karaciğer", "C) Deri (Cilt)", "D) Beyin"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Suyun kimyasal formülü nedir?", "secenekler": ["A) H2O", "B) CO2", "C) NaCl", "D) O2"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Bir yıl kaç günden oluşur (artık yıl hariç)?", "secenekler": ["A) 360", "B) 365", "C) 366", "D) 370"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Güneş'e en yakın gezegen hangisidir?", "secenekler": ["A) Venüs", "B) Merkür", "C) Mars", "D) Dünya"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Dünya'nın uydusu olan gök cismi hangisidir?", "secenekler": ["A) Güneş", "B) Ay", "C) Mars", "D) Titan"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Atmosferin yüzde kaçından fazlası Azot (Nitrojenden) oluşur?", "secenekler": ["A) %21", "B) %50", "C) %78", "D) %90"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Türkiye'nin plaka kodu 34 olan ili hangisidir?", "secenekler": ["A) Ankara", "B) İzmir", "C) İstanbul", "D) Bursa"], "cevap": "c", "odul": "1.000 TL"},
        {"soru": "Hangi hayvan memeliler sınıfından olmasına rağmen uçabilir?", "secenekler": ["A) Tavuk", "B) Yarasa", "C) Penguen", "D) Devekuşu"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Futbol topunun rengi klasik olarak siyah ve hangi renktendir?", "secenekler": ["A) Kırmızı", "B) Beyaz", "C) Sarı", "D) Mavi"], "cevap": "b", "odul": "1.000 TL"},
        # 10.000 TL Soruları
        {"soru": "Mona Lisa tablosunu çizen dünyaca ünlü İtalyan sanatçı ve deha kimdir?", "secenekler": ["A) Donatello", "B) Leonardo da Vinci", "C) Michelangelo", "D) Raphael"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Hücrenin enerji merkezi olarak bilinen organelin adı nedir?", "secenekler": ["A) Ribozom", "B) Mitokondri", "C) Kloroplast", "D) Lizozom"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Radyaktiveyi keşfeden ve Nobel ödülü kazanan ilk kadın bilim insanı kimdir?", "secenekler": ["A) Marie Curie", "B) Rosalind Franklin", "C) Ada Lovelace", "D) Jane Goodall"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Türk dilinin ilk sözlüğü ve ansiklopedisi olan eser Kaşgarlı Mahmud tarafından yazılan hangisidir?", "secenekler": ["A) Divanü Lügati't-Türk", "B) Kutadgu Bilig", "C) Atabetü'l-Hakayık", "D) Siyasetname"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Işık yılı neyi ölçmek için kullanılan bir birimdir?", "secenekler": ["A) Zaman", "B) Uzaklık / Mesafe", "C) Hız", "D) Işık şiddeti"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "İnsan vücudundaki en küçük kemik hangi bölgede yer alır?", "secenekler": ["A) Burun", "B) Kulak (Üzengi kemiği)", "C) Serçe parmak", "D) Topuk"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Dünya Sağlık Örgütü'nün uluslararası kısaltması nedir?", "secenekler": ["A) UNESCO", "B) WHO (DSÖ)", "C) UNICEF", "D) NATO"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Hangi elementin simgesi 'Fe' harfleridir?", "secenekler": ["A) Bakır", "B) Demir", "C) Altın", "D) Gümüş"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Dante Alighieri'nin ünlü eseri İlahi Komedya'da cehennemden sonra geçilen arınma yeri neresidir?", "secenekler": ["A) Araf (Purgatorio)", "B) Cennet", "C) Dünya", "D) Okyanus"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Fotoğrafçılıkta ve optikte kullanılan 'lazer' kelimesi aslında neyin kısaltmasıdır?", "secenekler": ["A) Uyarılmış radyasyon emisyonuyla ışık güçlendirmesi", "B) Hızlı renk taraması", "C) Dijital odaklama", "D) Optik yansıma"], "cevap": "a", "odul": "10.000 TL"},
        # 50.000 TL Soruları
        {"soru": "Nobel Ödülleri hangi ülkede verilmektedir?", "secenekler": ["A) Almanya", "B) İsviçre", "C) İsveç", "D) Fransa"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Hangi kan grubu 'Genel Alıcı' olarak bilinen ve diğer tüm gruplardan kan alabilen gruptur?", "secenekler": ["A) 0 Rh(-)", "B) AB Rh(+)", "C) A Rh(+)", "D) B Rh(-)"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Yunan mitolojisinde gökyüzü ve tanrıların kralı olan Zeus'un Romalı mitolojisindeki karşılığı nedir?", "secenekler": ["A) Mars", "B) Jüpiter", "C) Neptün", "D) Plüton"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Dünya'nın atmosfer tabakalarında meteorların yanarak yok olduğu katmanın adı nedir?", "secenekler": ["A) Troposfer", "B) Stratosfer", "C) Mezosfer", "D) Termosfer"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Kitapların başındaki yazar ve künye bilgilerinin yer aldığı sayfaya ne denir?", "secenekler": ["A) Önsöz", "B) İçindekiler", "C) Künye / Kolofon", "D) Sonsöz"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Hangi vitamin güneşi gördüğümüzde vücudumuzda sentezlenir?", "secenekler": ["A) A Vitamini", "B) C Vitamini", "C) D Vitamini", "D) K Vitamini"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Tiyatroda yazılmamış, anlık ve doğaçlama yapılan oyun türünün adı nedir?", "secenekler": ["A) Trajedi", "B) Komedi", "C) Mim / Tuluat (Doğaçlama)", "D) Melodram"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Güneş tutulması sırasında hangi gök cismi hangisinin önüne geçer?", "secenekler": ["A) Dünya, Güneş'in önüne geçer", "B) Ay, Güneş ile Dünya arasına girer", "C) Mars, Ay'ın önüne geçer", "D) Güneş, Ay'ın önüne geçer"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "Dünyanın en yüksek şelalesi olan Angel Şelalesi hangi ülkede yer alır?", "secenekler": ["A) Brezilya", "B) Venezuela", "C) ABD", "D) Kanada"], "cevap": "b", "odul": "50.000 TL"},
        {"soru": "İnsan beyninde denge ve hareket koordinasyonunu sağlayan küçük beyin bölümünün adı nedir?", "secenekler": ["A) Omirilik", "B) Serebellum (Cenecik / Beyincik)", "C) Talamus", "D) Hipotalamus"], "cevap": "b", "odul": "50.000 TL"},
        # 250.000 TL Soruları
        {"soru": "Periyodik tablonun ilk elementi ve evrende en bol bulunan kimyasal element hangisidir?", "secenekler": ["A) Helyum", "B) Oksijen", "C) Hidrojen", "D) Karbon"], "cevap": "c", "odul": "250.000 TL"},
        {"soru": "Albert Einstein'ın İzafiyet (Görecelik) Teorisi'ni özetleyen dünyaca ünlü formül hangisidir?", "secenekler": ["A) E = mc^2", "B) F = ma", "C) PV = nRT", "D) a^2 + b^2 = c^2"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "DNA molekülünün ikili sarmal (double helix) yapısını 1953 yılında çözen bilim insanları kimlerdir?", "secenekler": ["A) Watson ve Crick", "B) Newton ve Leibniz", "C) Curie çifti", "D) Darwin ve Wallace"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Antik Yunan filozofu Sokrates'in hiç yazılı eser bırakmamasına rağmen tüm felsefesini günümüze aktaran en ünlü öğrencisi kimdir?", "secenekler": ["A) Aristo", "B) Platon (Eflatun)", "C) Epikür", "D) Diojen"], "cevap": "b", "odul": "250.000 TL"},
        {"soru": "Kuşkusuz dünyanın en ünlü ressamlarından biri olan Vincent van Gogh'un kulağını kestikten sonra yaptığı en bilinen tablosu hangisidir?", "secenekler": ["A) Yıldızlı Gece (The Starry Night)", "B) Çığlık", "C) Guernica", "D) Son Akşam Yemeği"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Fizikte 'Mutlak Sıfır' sıcaklığı Celsius ölçeğinde tam olarak kaç derecedir?", "secenekler": ["A) 0 °C", "B) -100 °C", "C) -273.15 °C", "D) -500 °C"], "cevap": "c", "odul": "250.000 TL"},
        {"soru": "Nobel ödülünü reddeden ilk ve tek yazar olan ünlü 'Bulantı' romanının yazar varoluşçu filozof kimdir?", "secenekler": ["A) Jean-Paul Sartre", "B) Albert Camus", "C) Friedrich Nietzsche", "D) Fyodor Dostoyevski"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Kuantum mekaniğinde gözlemcinin durumu değiştirdiğini anlatan ünlü düşünce deneyi olan kedi paradoksunun sahibi fizikçi kimdir?", "secenekler": ["A) Erwin Schrödinger", "B) Werner Heisenberg", "C) Niels Bohr", "D) Max Planck"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Dünya dışı akıllı yaşam arayışını ifade eden SETI projesinde sinyallerin taranmasında kullanılan bilgisayar ağı programının adı nedir?", "secenekler": ["A) BOINC / SETI@home", "B) DeepMind", "C) Watson", "D) Skynet"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Rönesans döneminde siyaset felsefesinin kurucusu kabul edilen ve 'Amaca ulaşmak için her yol mübahtır' mantığıyla bilinen 'Prens' kitabının yazarı kimdir?", "secenekler": ["A) Niccolò Machiavelli", "B) Thomas Hobbes", "C) John Locke", "D) Montesquieu"], "cevap": "a", "odul": "250.000 TL"},
        # 1.000.000 TL Soruları
        {"soru": "Dünyanın çevresini ilk kez dolaşan ve Magellan'ın seferini tamamlayan denizci kimdir?", "secenekler": ["A) Vasco da Gama", "B) Kristof Kolomb", "C) Juan Sebastián Elcano", "D) Amerigo Vespucci"], "cevap": "c", "odul": "1.000.000 TL"},
        {"soru": "Matematikte tüm zamanların en büyük dâhilerinden biri kabul edilen ve asal sayılar üzerine yazdığı hipotezi hâlâ çözülemeyen Alman matematikçi kimdir?", "secenekler": ["A) Bernhard Riemann", "B) Leonhard Euler", "C) Carl Friedrich Gauss", "D) Pierre de Fermat"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Evrenin genişlediğini gözlemleyen ve uzak galaksilerin bizden uzaklaşma hızını hesaplayan ünlü astronom kimdir?", "secenekler": ["A) Edwin Hubble", "B) Carl Sagan", "C) Stephen Hawking", "D) Galileo Galilei"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Antik Mısır'da hiyeroglif yazısının çözülmesinde kilit rol oynayan ve üç farklı dil yazısı içeren tarihi taşın adı nedir?", "secenekler": ["A) Rosetta Taşı", "B) Hammurabi Kanunları", "C) Behistun Yazıtı", "D) Narmer Paleti"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Termodinamiğin İkinci Yasası'na göre evrende sürekli olarak artan ve geri döndürülemez olan fiziksel nicelik nedir?", "secenekler": ["A) Entropi", "B) Entalpi", "C) Kinetik enerji", "D) Momentüm"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Tarihte ilk kez sıfır (0) rakamını sayı sistemine kazandıran ve cebir bilminin temellerini atan ünlü İslam bilgin kimdir?", "secenekler": ["A) Harezmi", "B) İbn Sina", "C) Biruni", "D) Ömer Hayyam"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Biyolojide evrim teorisini doğal seçilim mekanizmasıyla birlikte Charles Darwin'den bağımsız olarak aynı dönemde keşfeden İngiliz doğa bilimci kimdir?", "secenekler": ["A) Alfred Russel Wallace", "B) Gregor Mendel", "C) Jean-Baptiste Lamarck", "D) Thomas Huxley"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Felsefede 'Saf Aklın Eleştirisi' kitabını yazarak epistemoloji ve ahlak felsefesinde devrim yaratan Alman filozof kimdir?", "secenekler": ["A) Immanuel Kant", "B) Georg Wilhelm Friedrich Hegel", "C) Arthur Schopenhauer", "D) Karl Marx"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Kuantum fiziğinde taneciklerin aynı anda hem dalga hem parça özelliği gösterdiğini ifade eden temel ilkenin adı nedir?", "secenekler": ["A) Dalga-Parçacık İkiliği (De Broglie hipotezi)", "B) Heisenberg Belirsizlik İlkesi", "C) Pauli Dışlama İlkesi", "D) Fotoelektrik Etki"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Sanat tarihine damga vuran ve optik illüzyonlar, imkansız yapılar çizen ünlü Hollandalı grafik sanatçısı kimdir?", "secenekler": ["A) M. C. Escher", "B) Rembrandt", "C) Johannes Vermeer", "D) Piet Mondrian"], "cevap": "a", "odul": "1.000.000 TL"}
    ],
    "teknoloji": [
        # 1.000 TL Soruları
        {"soru": "İnternetin temelini oluşturan ve 'Ağların Ağı' anlamına gelen küresel sistemin kısaltması nedir?", "secenekler": ["A) WWW", "B) HTTP", "C) TCP", "D) LAN"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Bilgisayarlarda veri girişi yapmak için kullanılan temel donanım birimi nedir?", "secenekler": ["A) Monitör", "B) Klavye", "C) Hoparlör", "D) Yazıcı"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Akıllı telefonlarda ve bilgisayarlarda çalışan uygulamalara genel olarak ne ad verilir?", "secenekler": ["A) Donanım", "B) Yazılım (Software)", "C) İşlemci", "D) Devre"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Google arama motorunun temel kurucularından biri kimdir?", "secenekler": ["A) Bill Gates", "B) Larry Page", "C) Steve Jobs", "D) Mark Zuckerberg"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Wi-Fi teknolojisi neyi kablosuz olarak sağlamaya yarar?", "secenekler": ["A) Elektrik iletimi", "B) İnternet bağlantısı ve yerel ağ", "C) Telefon şarjı", "D) Görüntülü arama kalitesi"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Microsoft şirketinin kurucusu dünyaca ünlü teknoloji lideri kimdir?", "secenekler": ["A) Bill Gates", "B) Elon Musk", "C) Jeff Bezos", "D) Tim Cook"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "Apple şirketinin simgesi olan meyve hangisidir?", "secenekler": ["A) Armut", "B) Elma", "C) Muz", "D) Çilek"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Sosyal medya platformu Twitter'ın (X) güncel logo simgesindeki ana hayvan figürü nedir?", "secenekler": ["A) Kuş (Eski logo)", "B) X harfi", "C) Kedi", "D) Köpek"], "cevap": "b", "odul": "1.000 TL"},
        {"soru": "Bilgisayarlarda ekrana görüntü aktaran ana çıkış birimi nedir?", "secenekler": ["A) Monitör", "B) Mouse", "C) Harddisk", "D) RAM"], "cevap": "a", "odul": "1.000 TL"},
        {"soru": "PDF dosya formatını geliştiren ve yaygınlaştıran şirketin adı nedir?", "secenekler": ["A) Adobe", "B) Microsoft", "C) Google", "D) Oracle"], "cevap": "a", "odul": "1.000 TL"},
        # 10.000 TL Soruları
        {"soru": "Linux işletim sisteminin maskotu olan sevimli penguenin adı nedir?", "secenekler": ["A) Pingu", "B) Tux", "C) Linuxy", "D) Waddle"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Bilgisayarlarda geçici verilerin tutulduğu ve bilgisayar kapandığında içindeki veriler silinen bellek birimi nedir?", "secenekler": ["A) RAM", "B) SSD", "C) HDD", "D) ROM"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Python programlama dilinin simgesi olan iki hayvan hangisidir?", "secenekler": ["A) Kedi ve Köpek", "B) İki Yılan", "C) Kartal ve Aslan", "D) Kunduz"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "Dünyanın ilk elektronik e-postası hangi on yılda gönderilmiştir?", "secenekler": ["A) 1960'lar", "B) 1970'ler", "C) 1980'ler", "D) 1990'lar"], "cevap": "b", "odul": "10.000 TL"},
        {"soru": "QR kodun açılımı olan İngilizce terim nedir?", "secenekler": ["A) Quick Response (Hızlı Yanıt)", "B) Quality Region", "C) Quantum Reader", "D) Query Routing"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Bluetooth teknolojisi adını tarihi hangi iskandinav kralından almıştır?", "secenekler": ["A) Harald Bluetooth (Kral Gormson)", "B) Ragnar Lothbrok", "C) Canute", "D) Olaf"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "HTML kısaltması web siteleri için ne anlama gelir?", "secenekler": ["A) HyperText Markup Language", "B) High Transfer Machine Language", "C) Hyper Tool Multi Language", "D) Home Text Modern Link"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Veritabanı yönetim sistemlerinde veri sorgulamak için en yaygın kullanılan dilin adı nedir?", "secenekler": ["A) SQL", "B) HTML", "C) CSS", "D) JSON"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "Sabit disklerde verilerin okunmasını sağlayan dönen manyetik plakaların hız birimi nedir?", "secenekler": ["A) RPM (Dakika başına devir)", "B) GHz", "C) MB/s", "D) PPI"], "cevap": "a", "odul": "10.000 TL"},
        {"soru": "USB standardının tam açılımı nedir?", "secenekler": ["A) Universal Serial Bus", "B) Ultra Speed Board", "C) Unified System Block", "D) Useful Signal Bridge"], "cevap": "a", "odul": "10.000 TL"},
        # 50.000 TL Soruları
        {"soru": "Yapay zeka alanında sıkça kullanılan 'ChatGPT' dil modelini geliştiren şirketin adı nedir?", "secenekler": ["A) Google", "B) Microsoft", "C) OpenAI", "D) Apple"], "cevap": "c", "odul": "50.000 TL"},
        {"soru": "Kripto para birimi Bitcoin'in yaratıcısı olarak bilinen gizemli kişi veya grubun takma adı nedir?", "secenekler": ["A) Satoshi Nakamoto", "B) Vitalik Buterin", "C) Alan Turing", "D) Linus Torvalds"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Açık kaynak kodlu ve ücretsiz işletim sistemi çekirdeği olan Linux'u 1991 yılında geliştiren isim kimdir?", "secenekler": ["A) Linus Torvalds", "B) Bill Gates", "C) Steve Wozniak", "D) Richard Stallman"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "İnternet tarayıcılarında güvenli bağlantı kurmayı sağlayan protokolün güvenli versiyonunun kısaltması nedir?", "secenekler": ["A) HTTPS", "B) FTP", "C) SMTP", "D) UDP"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Yapay zeka modellerinin eğitilmesinde kullanılan ve insan beynindeki nöron ağlarını taklit eden yapıya ne denir?", "secenekler": ["A) Yapay Sinir Ağları (Artificial Neural Networks)", "B) Mantıksal Devreler", "C) Bayte Matrisleri", "D) Komut Yığınları"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Blokzincir (Blockchain) teknolojisinde bir bloğun doğrulanması ve ağa eklenmesi sürecine ne ad verilir?", "secenekler": ["A) Madencilik (Mining) / Konsensüs", "B) Şifreleme", "C) Derleme (Compile)", "D) Seed İşlemi"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Bilgisayar bilimlerinde 'Open Source' (Açık Kaynak) felsefesinin öncüsü olan ve özgür yazılım hareketini başlatan kişi kimdir?", "secenekler": ["A) Richard Stallman", "B) Dennis Ritchie", "C) Ken Thompson", "D) Guido van Rossum"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "C programlama dilinin ve Unix işletim sisteminin geliştirildiği ünlü araştırma laboratuvarının adı nedir?", "secenekler": ["A) Bell Labs", "B) MIT", "C) CERN", "D) PARC"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Görsel yapay zeka modellerinin metin açıklamalarından görsel üretmesine ne ad verilir?", "secenekler": ["A) Metinden Görsele Üretim (Text-to-Image / Generative AI)", "B) Piksel Dönüşümü", "C) Renderleme", "D) Vektörizasyon"], "cevap": "a", "odul": "50.000 TL"},
        {"soru": "Bulut bilişim (Cloud Computing) mimarisinde altyapının hizmet olarak sunulmasının endüstrideki standart kısaltması nedir?", "secenekler": ["A) IaaS (Infrastructure as a Service)", "B) SaaS", "C) PaaS", "D) DaaS"], "cevap": "a", "odul": "50.000 TL"},
        # 250.000 TL Soruları
        {"soru": "Bilgisayarlarda veri depolamak için kullanılan ve elektrik kesildiğinde verileri silinmeyen kalıcı bellek hangisidir?", "secenekler": ["A) RAM", "B) Cache", "C) SSD / Sabit Disk", "D) Register"], "cevap": "c", "odul": "250.000 TL"},
        {"soru": "Tarihteki ilk elektronik genel amaçlı bilgisayar olan ENIAC hangi yılda çalıştırılmaya başlanmıştır?", "secenekler": ["A) 1945", "B) 1950", "C) 1939", "D) 1961"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Bilişim dünyasında 'P=NP' problemi hangi ana bilim dalının en büyük çözülememiş Millennium problemlerinden biridir?", "secenekler": ["A) Bilgisayar Bilimleri / Kompleksite Teorisi", "B) Kuantum Fiziği", "C) Sayılar Teorisi", "D) Kriptografi"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "İnternetin ilk atası olarak bilinen ve ABD Savunma Bakanlığı tarafından kurulan erken dönem bilgisayar ağının adı nedir?", "secenekler": ["A) ARPANET", "B) NSFNET", "C) MILNET", "D) DARPANET"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Programlama dillerinde kodun okunabilirliğini artırmak ve makine diline çevrilmeden doğrudan satır satır çalıştırılmasını sağlayan çevirmen türüne ne denir?", "secenekler": ["A) Yorumlayıcı (Interpreter)", "B) Derleyici (Compiler)", "C) Bağlayıcı (Linker)", "D) Debugger"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Kuantum bilgisayarların klasik bilgisayarlardaki bitler yerine kullandığı temel bilgi biriminin adı nedir?", "secenekler": ["A) Qubit (Kuantum Bit)", "B) Superbit", "C) Megabit", "D) Nanobit"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Bilişim güvenliğinde 'Man-in-the-Middle' (Ortadaki Adam) saldırısı neyi hedefler?", "secenekler": ["A) İki taraf arasındaki iletişimi gizlice dinlemek veya değiştirmek", "B) Sunucuyu çökertmek", "C) Şifreleri kaba kuvvetle kırmak", "D) Sabit diski biçimlendirmek"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Yapay zeka tarihinde insan şampiyon Garry Kasparov'u yenen IBM geliştirеcisi ünlü satranç süper bilgisayarının adı nedir?", "secenekler": ["A) Deep Blue", "B) AlphaGo", "C) Watson", "D) DeepMind"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Modern şifrelemenin temel taşlarından biri olan RSA algoritması hangi üç matematikçinin soyadından türetilmiştir?", "secenekler": ["A) Rivest, Shamir ve Adleman", "B) Ron, Smith, Alan", "C) Russell, Stokes, Abel", "D) Riemann, Schwarz, Atiyah"], "cevap": "a", "odul": "250.000 TL"},
        {"soru": "Ethernet teknolojisinin ve yerel ağların (LAN) mucidi olan ve PARC laboratuvarlarında çalışan ünlü mühendis kimdir?", "secenekler": ["A) Robert Metcalfe", "B) Vint Cerf", "C) Tim Berners-Lee", "D) Ray Tomlinson"], "cevap": "a", "odul": "250.000 TL"},
        # 1.000.000 TL Soruları
        {"soru": "İlk programlanabilir elektronik bilgisayar olarak kabul edilen ve 1945 yılında geliştirilen devasa cihazın adı nedir?", "secenekler": ["A) ENIAC", "B) UNIVAC", "C) Altair 8800", "D) IBM 5100"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Bilişim ve hesaplamalı kuramın babası kabul edilen ve yapay zekanın test kriterini belirleyen trajik kahraman matematikçi kimdir?", "secenekler": ["A) Alan Turing", "B) John von Neumann", "C) Claude Shannon", "D) Alonzo Church"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "World Wide Web (WWW) sistemini ve ilk web tarayıcısı ile sunucusunu 1989 yılında CERN'de icat eden mucit kimdir?", "secenekler": ["A) Tim Berners-Lee", "B) Vint Cerf", "C) Marc Andreessen", "D) Bob Kahn"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Bilgisayar mimarisinde verilerin ve komutların aynı bellek alanında saklandığı evrensel standart mimarinin adı nedir?", "secenekler": ["A) Von Neumann Mimarisi", "B) Harvard Mimarisi", "C) Turing Mimarisi", "D) RISC Mimarisi"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Bilgi teorisinin (Information Theory) kurucusu olan ve entropi kavramını bilişim dünyasına kazandıran matematikçi kimdir?", "secenekler": ["A) Claude Shannon", "B) Norbert Wiener", "C) Alan Turing", "D) John Nash"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Kriptografide 'Sıfır Bilgi Kanıtı' (Zero-Knowledge Proof) kavramını ilk kez ortaya atan ve modern gizlilik protokollerinin önünü açan MIT bilim insanı kimdir?", "secenekler": ["A) Shafi Goldwasser / Silvio Micali", "B) Whitfield Diffie", "C) Bruce Schneier", "D) Phil Zimmermann"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Yapay zeka devriminde derin öğrenme (Deep Learning) algoritmalarının önünü açan AlexNet mimarisini tasarlayan ve 'Yapay Zekanın Godfather'ı' olarak bilinen bilim insanı kimdir?", "secenekler": ["A) Geoffrey Hinton", "B) Yann LeCun", "C) Yoshua Bengio", "D) Demis Hassabis"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Bilişim dünyasında 'Unix Zamanı' (Unix Epoch) hesaplamalarına göre zaman milat olarak tam hangi tarihte 0 saniye olarak başlatılmıştır?", "secenekler": ["A) 1 Ocak 1970", "B) 1 Ocak 1980", "C) 1 Ocak 1960", "D) 31 Aralık 1999"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Geliştirdiği dikey entegrasyonlu roketlerle uzay teknolojisinde devrim yaratan SpaceX şirketinin kurucusu ve baş mühendisi kimdir?", "secenekler": ["A) Elon Musk", "B) Jeff Bezos", "C) Richard Branson", "D) Peter Beck"], "cevap": "a", "odul": "1.000.000 TL"},
        {"soru": "Kuantum hesaplama alanında kuantum algoritmalarının (örneğin büyük sayıları çarpanlarına ayıran Shor algoritması) temelini atan matematikçi kimdir?", "secenekler": ["A) Peter Shor", "B) David Deutsch", "C) Richard Feynman", "D) John Preskill"], "cevap": "a", "odul": "1.000.000 TL"}
    ]
}

mesaj_sayaci = 0

@bot.event
async def on_ready():
    print(f"Giriş yapıldı! Bot aktif: {bot.user}")
    istatistik_guncelle.start()

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
                embed = discord.Embed(
                    title=f"💰 Milyoner Yarışması | Soru {oyun['tur'] + 1} / 5",
                    description=f"✅ **Tebrikler, doğru bildin!** Sıradaki Ödül: **{sonraki_soru['odul']}**\n\n**Soru:** {sonraki_soru['soru']}\n\n{secenekler_metni}\n\n*Cevap vermek için şıkkın harfini yaz (A, B, C, D)*",
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

    # Günün Sorusu Kontrolü
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

    mesaj_sayaci += 1
    if mesaj_sayaci >= 15:
        mesaj_sayaci = 0
        secilen = random.choice(GUNCEL_SORULAR)
        aktif_sorular[message.channel.id] = secilen["cevap"]
        await message.channel.send(secilen["soru"])

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

    # Seçilen kategorideki 100 sorudan o tur için rastgele zorluklarına göre 5 soru seç
    tum_sorular = MILYONER_VERITABANI[secilen_kat]
    
    # 5 farklı zorluk seviyesinden (her 20 soruda bir zorluk artar) birer soru seçelim
    secilen_tur_sorulari = []
    for i in range(5):
        grup = tum_sorular[i*20 : (i+1)*20]
        secilen_tur_sorulari.append(random.choice(grup))

    milyoner_oyunlari[ctx.channel.id] = {
        "oyuncu_id": ctx.author.id,
        "sorular": secilen_tur_sorulari,
        "tur": 0
    }

    ilk_soru = secilen_tur_sorulari[0]
    secenekler_metni = "\n".join(ilk_soru["secenekler"])
    
    embed = discord.Embed(
        title=f"💰 Kim Milyoner Olmak İster? ({secilen_kat.upper()})",
        description=f"🎯 Yarışmacı: {ctx.author.mention}\n1. Soru Ödülü: **{ilk_soru['odul']}**\n\n**Soru:** {ilk_soru['soru']}\n\n{secenekler_metni}\n\n*Cevap vermek için doğrudan şıkkın harfini yaz (A, B, C, D)*",
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
            "• `!milyoner [lol/valorant/tarih/coğrafya/müzik/futbol/genel/teknoloji]` - 100'er soruluk havuzdan 5 turlu Milyoner yarışması\n"
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
        name="🚪 3. Ses Kanalı & Odalar",
        value=(
            "• `!git <kanal adı>` - Oda boşsa gider, doluysa ✅ onayı ister\n"
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

    embed.set_footer(text="Gelişmiş Discord Botu • Her kategoride 100 soru aktif!")
    await ctx.send(embed=embed)

keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
