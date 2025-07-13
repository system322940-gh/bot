from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import random
import os

# --- Flask部分（RenderのためのダミーWeb） ---
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# --- Discord Bot部分 ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

target_number = None
game_active = False

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot ready: {bot.user}")

@tree.command(name="game", description="1～100の数字当てゲームを開始します")
async def game(interaction: discord.Interaction):
    global target_number, game_active
    if game_active:
        await interaction.response.send_message("⚠️ すでにゲーム中です！ `/guess` で数字を当ててね！", ephemeral=True)
    else:
        target_number = random.randint(1, 100)
        game_active = True
        await interaction.response.send_message("🎯 数字当てゲームスタート！ `/guess 数字` で当ててね！")

@tree.command(name="guess", description="数字を予想して送信します")
@app_commands.describe(number="1～100の中で予想する数字")
async def guess(interaction: discord.Interaction, number: int):
    global target_number, game_active
    if not game_active:
        await interaction.response.send_message("❗まず `/game` でゲームを始めてね！", ephemeral=True)
        return

    if number == target_number:
        game_active = False
        await interaction.response.send_message(f"🎉 正解！ {interaction.user.display_name} さんが当てました！")
    elif number < target_number:
        await interaction.response.send_message("🔺 もっと大きい数字だよ！")
    else:
        await interaction.response.send_message("🔻 もっと小さい数字だよ！")

# --- 起動部分 ---
def start():
    Thread(target=run_web).start()
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    start()
