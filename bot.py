import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True  # 必要なら（例: 通常コマンドにも対応したい時）

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ ログインしました: {bot.user} ({bot.user.id})")


# /servermember コマンド
@tree.command(name="servermember", description="サーバーのメンバー数を表示します")
async def servermember(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("サーバー内で使ってね。", ephemeral=True)
        return

    count = interaction.guild.member_count
    await interaction.response.send_message(f"このサーバーのメンバー数は **{count}人** です！")


# /ban コマンド
@tree.command(name="ban", description="指定したユーザーをBANします（管理者用）")
@app_commands.describe(user="BANしたいユーザー", reason="理由（省略可）")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "理由なし"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("🚫 BANする権限がありません。", ephemeral=True)
        return

    try:
        await user.ban(reason=reason)
        await interaction.response.send_message(f"{user.mention} をBANしました。理由: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"BANに失敗: {str(e)}", ephemeral=True)


# /kick コマンド
@tree.command(name="kick", description="指定したユーザーをKICKします（管理者用）")
@app_commands.describe(user="KICKしたいユーザー", reason="理由（省略可）")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "理由なし"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("🚫 KICKする権限がありません。", ephemeral=True)
        return

    try:
        await user.kick(reason=reason)
        await interaction.response.send_message(f"{user.mention} をKICKしました。理由: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"KICKに失敗: {str(e)}", ephemeral=True)


# /ping コマンド
@tree.command(name="ping", description="Botの応答速度を確認します")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! 応答速度: {latency}ms")


# ↓ 不要な /say は削除済み

# Bot起動
bot.run("MTM5MzgwODA5NjQ5Mjc4MTU2OQ.G-WrRk.uy8aDpAICbWzTkej03gwPqNN96EFaC54Ghm6Ac")  # ← トークンを自分のに差し替えてね
