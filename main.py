@bot.command(name="skor")
async def skor(ctx):
    # UNL (Uluslar Ligi), CL (Şampiyonlar Ligi) ve TR1 (Süper Lig) kodlarını ekledik
    url = "https://api.football-data.org/v4/matches?competitions=UNL,CL,TR1"
    headers = {"X-Auth-Token": os.environ.get("FOOTBALL_API_KEY", "")}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    matches = data.get("matches", [])
                    
                    if not matches:
                        # Eğer filtreli gelmezse genel maç listesini dener
                        async with session.get("https://api.football-data.org/v4/matches", headers=headers) as resp2:
                            if resp2.status == 200:
                                data2 = await resp2.json()
                                matches = data2.get("matches", [])
                    
                    if not matches:
                        await ctx.send("ℹ️ Şu an API havuzunda aktif maç verisi görünmüyor. (Ücretsiz API paketlerinin veri güncellemelerinde anlık gecikmeler olabiliyor).")
                        return
                    
                    embed = discord.Embed(title="⚽ Canlı Maçlar & Uluslar Ligi Skorları", color=discord.Color.green())
                    count = 0
                    for match in matches:
                        comp = match.get("competition", {}).get("name", "Futbol Maçı")
                        home = match['homeTeam']['name']
                        away = match['awayTeam']['name']
                        score_home = match['score']['fullTime']['home']
                        score_away = match['score']['fullTime']['away']
                        status = match['status']
                        utc_date = match.get('utcDate', '')
                        
                        tarih_saat = "Yakında"
                        if len(utc_date) >= 16:
                            gun = utc_date[8:10]
                            ay = utc_date[5:7]
                            saat = utc_date[11:16]
                            tarih_saat = f"{gun}.{ay} - {saat} UTC"

                        if status == "FINISHED":
                            durum = "Bitti"
                        elif status == "IN_PLAY" or status == "PAUSED":
                            durum = "Canlı 🔴"
                        else:
                            durum = f"Tarih: {tarih_saat}"
                        
                        s_home = score_home if score_home is not None else "0"
                        s_away = score_away if score_away is not None else "0"
                        
                        embed.add_field(
                            name=comp,
                            value=f"**{home}** {s_home} - {s_away} **{away}** *({durum})*",
                            inline=False
                        )
                        count += 1
                        if count >= 8:
                            break
                    
                    await ctx.send(embed=embed)
                else:
                    text_resp = await response.text()
                    await ctx.send(f"⚠️ API Hatası! Kod: `{response.status}` | Detay: `{text_resp}`")
        except Exception as e:
            await ctx.send(f"⚠️ Maçlar çekilirken bir hata oluştu: `{e}`")
