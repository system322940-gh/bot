import discord
from discord.ext import commands
from discord import app_commands
import aiofiles
import asyncio
import os

# グローバルチャットに登録するチャンネルIDを保存するファイル
GLOBAL_CHAT_FILE = "globalchatchannels.txt"

# intentsの設定（message_contentが必要）
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # スラッシュコマンド用ツリー

# Webhookのキャッシュ（チャンネルID: webhook）
webhook_cache = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    # スラッシュコマンドをDiscordに同期（初回起動時や更新時に必要）
    await tree.sync()
    print("Slash commands synced.")

# /addglobalchat コマンド（管理者権限のみ）
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
    # Bot自身のメッセージは無視
    if message.author.bot:
        return

    # 登録チャンネル一覧読み込み
    try:
        async with aiofiles.open(GLOBAL_CHAT_FILE, mode='r') as f:
            lines = await f.readlines()
            channel_ids = [int(line.strip()) for line in lines]
    except FileNotFoundError:
        channel_ids = []

    # 登録されていないチャンネルなら処理しない
    if message.channel.id not in channel_ids:
        return

    # メッセージを他のグローバルチャットチャンネルにWebhookで送信
    for cid in channel_ids:
        if cid == message.channel.id:
            continue

        channel = bot.get_channel(cid)
        if not channel:
            continue

        # Webhookをキャッシュから取得、なければ作成してキャッシュに保存
        webhook = webhook_cache.get(cid)
        if webhook is None:
            webhooks = await channel.webhooks()
            webhook = next((w for w in webhooks if w.name == "GlobalChat"), None)
            if not webhook:
                webhook = await channel.create_webhook(name="GlobalChat")
            webhook_cache[cid] = webhook

        try:
            await webhook.send(
                content=message.content,
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url
            )
        except Exception as e:
            print(f"Webhook送信エラー: チャンネルID {cid} - {e}")

    # コマンドの処理も行う（もしコマンドがメッセージとして入ってきた場合）
    await bot.process_commands(message)


TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)
