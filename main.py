import discord
from discord.ext import commands, tasks
import os
import random
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

mensagem_online_alternada = True

def encontrar_canal_geral(guild):
    for channel in guild.text_channels:
        if channel.name.lower() in ['geral', 'general', '💬geral', '💬general']:
            return channel
    return guild.system_channel

def pegar_membro_aleatorio(guild):
    membros = [m for m in guild.members if not m.bot]
    if membros:
        return random.choice(membros)
    return None


@tasks.loop(hours=2)
async def mensagens_aleatorias():
    frases_com_nome = [
        "Alguém viu o {nome}? Deve tá camperando no banheiro 🚽",
        "Dica do dia: não caia fora da safe, igual o {nome} ontem 😆",
        "Reza a lenda que o {nome} ainda tá looteando em Verdansk até hoje...",
        "Missão do dia: morrer menos que o {nome}. Boa sorte, recruta 🪖",
        "Tem gente que joga Warzone… e tem o {nome}, que dá aula de como ser o primeiro a morrer 😆",
        "📦 Drop chegando... mas o {nome} já pegou tudo, como sempre 🤑",
        "🪂 O {nome} caiu longe de novo. O cara acha que tá jogando Minecraft."
    ]
    
    frases_sem_nome = [
        "Lembre-se: loot é vida. Reanime seus baitolas!",
        "O bot detectou baitolas online! Preparem as placas 🛡️",
        "Quando a squad tá completa, até a safe respeita 💪",
        "Atenção, baitolas! Nova meta: ganhar uma sem reclamar do lag."
    ]
    
    for guild in bot.guilds:
        canal = encontrar_canal_geral(guild)
        if canal:
            membro = pegar_membro_aleatorio(guild)
            
            if membro:
                frase = random.choice(frases_com_nome)
                frase = frase.format(nome=membro.display_name)
            else:
                frase = random.choice(frases_sem_nome)
            
            await canal.send(frase)

@bot.event
async def on_ready():
    print(f'✓ Bot conectado como {bot.user.name} (ID: {bot.user.id})')
    print(f'✓ Aplicação Bot está online!')
    print(f'✓ Conectado a {len(bot.guilds)} servidor(es)')
    print('━' * 50)
    
    if not mensagens_aleatorias.is_running():
        mensagens_aleatorias.start()
        print('✓ Mensagens aleatórias ativadas (a cada 2 horas)')
    else:
        print('✓ Mensagens aleatórias já estavam ativas')


@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel is not None:
        embed = discord.Embed(
            title="Bem-vindo!",
            description=
            f'Olá {member.mention}, seja bem-vindo ao {member.guild.name}!',
            color=discord.Color.green())
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.
                            default_avatar.url)
        await channel.send(embed=embed)


@bot.event
async def on_presence_update(before, after):
    global mensagem_online_alternada
    if before.bot:
        return
    
    if before.status == discord.Status.offline and after.status == discord.Status.online:
        canal = encontrar_canal_geral(after.guild)
        if canal:
            if mensagem_online_alternada:
                mensagem = f"🟢 O Baitola **{after.display_name}** está online! Bora Baitolaaaaa! 🎮"
            else:
                mensagem = f"🪖 O baitola **{after.display_name}** acordou do gulag e tá ONLINE!\nSerá que hoje ele acerta um tiro? 🎯"
            
            mensagem_online_alternada = not mensagem_online_alternada
            await canal.send(mensagem)


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    
    if before.channel is None and after.channel is not None:
        canal = encontrar_canal_geral(member.guild)
        if canal:
            mensagem = f"🔊 O Baitola **{member.display_name}** entrou em **{after.channel.name}** e está jogando sem você! Bora Baitolaaaaa! 🎮"
            await canal.send(mensagem)


@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!",
                          description=f'Latência: {latency}ms',
                          color=discord.Color.blue())
    await ctx.send(embed=embed)


@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(
        title="ℹ️ Informações do Bot",
        description="Aplicação Bot - Um bot Discord em Python",
        color=discord.Color.purple())
    embed.add_field(name="Servidores", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Usuários", value=str(len(bot.users)), inline=True)
    embed.add_field(name="Prefixo", value="!", inline=True)
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    await ctx.send(embed=embed)


@bot.command(name='ajuda')
async def ajuda(ctx):
    embed = discord.Embed(title="📚 Comandos Disponíveis",
                          description="Lista de comandos da Aplicação Bot",
                          color=discord.Color.gold())
    embed.add_field(name="!ping",
                    value="Verifica a latência do bot",
                    inline=False)
    embed.add_field(name="!info",
                    value="Mostra informações sobre o bot",
                    inline=False)
    embed.add_field(name="!ajuda",
                    value="Mostra esta mensagem de ajuda",
                    inline=False)
    embed.set_footer(text="Use ! antes de cada comando")
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "❌ Comando não encontrado! Use `!ajuda` para ver os comandos disponíveis."
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Argumentos faltando! Verifique o comando e tente novamente.")
    else:
        await ctx.send(f"❌ Ocorreu um erro: {str(error)}")


def main():
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ ERRO: DISCORD_BOT_TOKEN não encontrado!")
        print("Por favor, adicione seu token do Discord Bot nas secrets.")
        return

    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido! Verifique seu DISCORD_BOT_TOKEN.")
    except Exception as e:
        print(f"❌ ERRO ao iniciar o bot: {e}")


if __name__ == '__main__':
    main()
