import aiofiles

GLOBAL_CHAT_FILE = "globalchatchannels.txt"

@tree.command(name="addglobalchat", description="このチャンネルをグローバルチャットに追加します")
@app_commands.checks.has_permissions(administrator=True)
async def add_global_chat(interaction: discord.Interaction):
    channel_id = interaction.channel.id
    try:
        async with aiofiles.open(GLOBAL_CHAT_FILE, mode='a+') as f:
            await f.seek(0)
            lines = await f.readlines()
            if f"{channel_id}\n" in lines:
                await interaction.response.send_message("⚠️ このチャンネルはすでに登録されています。", ephemeral=True)
                return
            await f.write(f"{channel_id}\n")
        await interaction.response.send_message("✅ このチャンネルをグローバルチャットに登録しました。")
    except Exception as e:
        await interaction.response.send_message(f"❌ 登録中にエラーが発生しました: {e}", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        async with aiofiles.open(GLOBAL_CHAT_FILE, mode='r') as f:
            lines = await f.readlines()
            channel_ids = [int(line.strip()) for line in lines]
    except FileNotFoundError:
        channel_ids = []

    if message.channel.id not in channel_ids:
        return  # 登録されていないチャンネルならスキップ

    for cid in channel_ids:
        if cid == message.channel.id:
            continue  # 自チャンネルには送らない

        channel = bot.get_channel(cid)
        if channel:
            webhooks = await channel.webhooks()
            webhook = next((w for w in webhooks if w.name == "GlobalChat"), None)
            if not webhook:
                webhook = await channel.create_webhook(name="GlobalChat")

            await webhook.send(
                content=message.content,
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url
            )
