import discord
from discord.ext import commands
from discord import app_commands
import random
import os

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ ログインしました: {bot.user} ({bot.user.id})")

@tree.command(name="servermember", description="サーバーのメンバー数を表示します")
async def servermember(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("サーバー内で使ってね。", ephemeral=True)
        return
    count = interaction.guild.member_count
    await interaction.response.send_message(f"このサーバーのメンバー数は **{count}人** です！")

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

@tree.command(name="ping", description="Botの応答速度を確認します")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! 応答速度: {latency}ms")

class AuthButton(discord.ui.View):
    def __init__(self, user: discord.User, role: discord.Role):
        super().__init__(timeout=None)
        self.user = user
        self.role = role

    @discord.ui.button(label="認証", style=discord.ButtonStyle.primary)
    async def auth(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("これはあなた専用の認証です。", ephemeral=True)
            return
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        await interaction.response.send_modal(AuthModal(num1, num2, self.role))

class AuthModal(discord.ui.Modal, title="認証確認"):
    def __init__(self, num1, num2, role):
        super().__init__()
        self.num1 = num1
        self.num2 = num2
        self.answer = num1 + num2
        self.role = role
        self.response = discord.ui.TextInput(label=f"{num1} + {num2} の答えを入力してください", required=True)
        self.add_item(self.response)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if int(self.response.value) == self.answer:
                await interaction.user.add_roles(self.role)
                await interaction.response.send_message("✅ 正解！ロールを付与しました。", ephemeral=True)
            else:
                await interaction.response.send_message("❌ 不正解です。", ephemeral=True)
        except:
            await interaction.response.send_message("❌ エラーが発生しました。", ephemeral=True)

@tree.command(name="auth", description="認証用のボタンを作成します")
@app_commands.describe(title="大きく表示される文字", role="付与するロール")
async def auth(interaction: discord.Interaction, title: str, role: discord.Role):
    view = AuthButton(interaction.user, role)
    await interaction.response.send_message("✅ 認証メッセージを作成しました。", ephemeral=True)
    await interaction.channel.send(embed=discord.Embed(title=title, color=discord.Color.blue()), view=view)

class RoleButton(discord.ui.View):
    def __init__(self, role: discord.Role):
        super().__init__(timeout=None)
        self.role = role

    @discord.ui.button(label="ロールをもらう", style=discord.ButtonStyle.success)
    async def grant_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.user.add_roles(self.role)
            await interaction.response.send_message("✅ ロールを付与しました。", ephemeral=True)
        except:
            await interaction.response.send_message("❌ ロールを付与できませんでした。", ephemeral=True)

@tree.command(name="rp", description="ボタンを押してロールを付与します")
@app_commands.describe(title="大きく表示される文字", role="付与するロール")
async def rp(interaction: discord.Interaction, title: str, role: discord.Role):
    view = RoleButton(role)
    await interaction.response.send_message("✅ ロール付与ボタンを作成しました。", ephemeral=True)
    await interaction.channel.send(embed=discord.Embed(title=title, color=discord.Color.green()), view=view)

# /help コマンド
@tree.command(name="info", description="ヘルプを埋め込みで表示します")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="ヘルプ",
        description="`/auth` - 認証パネルを作成します。　`/rp` - ロールパネルを作成します。　`/kick` - メンバーをキックします。管理者専用です。　`/ban` - メンバーをbanします。管理者専用です。　`/ping` - botの反応速度を表示します。,
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)

# 環境変数 DISCORD_TOKEN からトークンを取得して起動(Discordにト*クンリセットされるので環境変数名変えたけど名前のセンスが小2だけどゆるして)
bot.run(os.getenv("KIDOU_MOJI"))
