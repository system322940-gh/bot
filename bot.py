import discord
from discord.ext import commands
from discord import app_commands
import os
import random

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

target_number = None
game_active = False

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await tree.sync()
    print("Slash commands synced.")

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

@tree.command(name="say", description="Botに好きなことを言わせる")
@app_commands.describe(
    message="Botに言わせたい内容",
    embed="埋め込み形式で送るか（True/False）"
)
async def say(interaction: discord.Interaction, message: str, embed: bool = False):
    sender_name = interaction.user.display_name

    # まず即レス（3秒以内に）する
    await interaction.response.send_message("✅ 発言準備中...", ephemeral=True)

    try:
        if embed:
            embed_obj = discord.Embed(description=message, color=discord.Color.blurple())
            embed_obj.set_footer(text=f"送信者: {sender_name}")
            await interaction.channel.send(embed=embed_obj)
        else:
            await interaction.channel.send(f"{message}\n\n💬 送信者: **{sender_name}**")

    except Exception as e:
        await interaction.followup.send(f"❌ メッセージ送信中にエラーが発生しました: {e}", ephemeral=True)


# --- Bot起動 ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKENが設定されていません。環境変数で設定してください。")

bot.run(TOKEN)
