import discord
from discord.ext import commands
from discord import app_commands
import aiofiles
import asyncio
import os
import random  # 数字当てゲームに必要

# グローバルチャットに登録するチャンネルIDを保存するファイル
GLOBAL_CHAT_FILE = "globalchatchannels.txt"

# intentsの設定（message_contentが必要）
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # スラッシュコマンド用ツリー

# Webhookのキャッシュ（チャンネルID: webhook）
webhook_cache = {}

# --- 数字当てゲーム用 ---
target_number = None
game_active = False

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
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
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ 登録中にエラーが発生しました: {e}", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ 登録中にエラーが発生しました: {e}", ephemeral=True)

# メッセージ送信イベント
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
        return

    for cid in channel_ids:
        if cid == message.channel.id:
            continue

        channel = bot.get_channel(cid)
        if not channel:
            continue

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

    await bot.process_commands(message)

# --- 数字当てゲーム ---
@tree.command(name="game", description="1～100の数字当てゲームを開始します")
async def game(interaction: discord.Interaction):
    global target_number, game_active
    if game_active:
        await interaction.response.send_message("⚠️ すでにゲーム中です！ /guess で数字を当ててね！", ephemeral=True)
    else:
        target_number = random.randint(1, 100)
        game_active = True
        await interaction.response.send_message("🎯 数字当てゲームスタート！ /guess 数字 で当ててね！")

@tree.command(name="guess", description="数字を予想して送信します")
@app_commands.describe(number="1～100の中で予想する数字")
async def guess(interaction: discord.Interaction, number: int):
    global target_number, game_active
    if not game_active:
        await interaction.response.send_message("❗まず /game でゲームを始めてね！", ephemeral=True)
        return

    if number == target_number:
        game_active = False
        await interaction.response.send_message(f"🎉 正解！ {interaction.user.display_name} さんが当てました！")
    elif number < target_number:
        await interaction.response.send_message("🔺 もっと大きい数字だよ！")
    else:
        await interaction.response.send_message("🔻 もっと小さい数字だよ！")

@tree.command(name="cancel", description="進行中のゲームをキャンセルします")
async def cancel_game(interaction: discord.Interaction):
    global game_active
    if game_active:
        game_active = False
        await interaction.response.send_message("✅ ゲームをキャンセルしました。", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ 進行中のゲームはありません。", ephemeral=True)

# --- 管理者用コマンド ---
@tree.command(name="kick", description="指定したメンバーをキックします")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(member="キックするメンバー", reason="理由（任意）")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "理由なし"):
    if member == interaction.client.user:
        await interaction.response.send_message("❌ 自分自身をキックすることはできません。", ephemeral=True)
        return
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} をキックしました。理由: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ キックに失敗しました: 権限がありません。", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ エラーが発生しました: {e}", ephemeral=True)

@tree.command(name="ban", description="指定したメンバーをBANします")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(member="BANするメンバー", reason="理由（任意）")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "理由なし"):
    if member == interaction.client.user:
        await interaction.response.send_message("❌ 自分自身をBANすることはできません。", ephemeral=True)
        return
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} をBANしました。理由: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ BANに失敗しました: 権限がありません。", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ エラーが発生しました: {e}", ephemeral=True)

# --- Bot起動 ---
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
