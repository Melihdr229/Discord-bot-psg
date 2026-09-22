import discord
from discord.ext import commands
import os
import google.generativeai as genai
from keep_alive import keep_alive
import yt_dlp
import asyncio

# Yapay zeka API anahtarın
genai.configure(api_key="AQ.Ab8RN6KwEvUbtwL6rH1McKBH2lDQqISnSoAtjm57F2j7dVN2EQ")
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True

# Prefix (komut ön eki) ! olarak ayarlandı
bot = commands.Bot(command_prefix='!', intents=intents)

# Müzik ayarları
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_options = {'options': '-vn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı! Müzik ve Yapay Zeka aktif.')

# --- YAPAY ZEKA KOMUTU ---
@bot.command(name='sor')
async def yapay_zeka(ctx, *, soru: str):
    async with ctx.typing():
        try:
            cevap = model.generate_content(soru)
            await ctx.reply(cevap.text)
        except Exception as e:
            await ctx.reply("Şu an düşünemiyorum, bir hata oluştu.")

# --- MÜZİK KOMUTLARI ---
@bot.command(name='çal')
async def cal(ctx, *, sarki_adi: str):
    if not ctx.message.author.voice:
        await ctx.send("Önce bir ses kanalına katılmalısın!")
        return
    
    kanal = ctx.message.author.voice.channel
    ses_istemi = ctx.voice_client
    
    if ses_istemi is None:
        ses_istemi = await kanal.connect()
    elif ses_istemi.channel != kanal:
        await ses_istemi.move_to(kanal)

    await ctx.send(f"🎵 **{sarki_adi}** aranıyor...")
    ffmpeg_yolu = './ffmpeg' if os.path.exists('./ffmpeg') else 'ffmpeg'

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(sarki_adi, download=False))
        
        if 'entries' in data:
            data = data['entries'][0]
            
        sarki_url = data['url']
        baslik = data['title']
        
        if ses_istemi.is_playing():
            ses_istemi.stop()
            
        ses_istemi.play(discord.FFmpegPCMAudio(sarki_url, executable=ffmpeg_yolu, **ffmpeg_options))
        await ctx.send(f"🎶 Şu an çalıyor: **{baslik}**")
    except Exception as e:
        await ctx.send("Şarkı çalınırken bir hata oluştu.")

@bot.command(name='dur')
async def dur(ctx):
    ses_istemi = ctx.voice_client
    if ses_istemi:
        await ses_istemi.disconnect()
        await ctx.send("Ses kanalından ayrıldım.")
    else:
        await ctx.send("Zaten bir ses kanalında değilim.")

keep_alive()
bot.run(os.environ['MTU0OTQ0OTQ2NTM3NzU5MTQxNw.GwAS-x.sjm0a4eBPVvcR6LJP2MGH2dSslQ0Rbzm3SOYOA'])
