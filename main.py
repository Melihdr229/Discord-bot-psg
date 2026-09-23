# --- 3. SES KANALI VE BAĞLANTI KESİLME LOGLARI ---
@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    log_kanal = discord.utils.get(member.guild.text_channels, name="mod-log")

    if log_kanal:
        # Biri sesten ayrıldığında veya atıldığında
        if before.channel is not None and after.channel is None:
            # Eğer kullanıcı kendi çıkmadıysa (başbiri attıysa veya susturduysa)
            durum_mesaji = f"🔇 **{member.mention}** adlı kullanıcı **{before.channel.name}** ses kanalından ayrıldı/bağlantısı kesildi."
            
            # Audit log kontrolü için kısa bir bekleme (Discord API senkronizasyonu için)
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
