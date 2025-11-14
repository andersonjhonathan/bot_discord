from flask import Flask
from threading import Thread
import nextcord as discord
from nextcord.ext import commands, tasks
import os
import random
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from waitress import serve

app = Flask('')

@app.route('/')
def home():
    return "✅ Bot ativo e rodando no Replit!"

def run():
    port = int(os.environ.get("PORT", 8080))
    serve(app, host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

RANKING_FILE = "ranking.json"

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
                adicionar_ponto(membro.id, "mencionado")
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

    canal = encontrar_canal_geral(after.guild)
    
    if before.status == discord.Status.offline and after.status == discord.Status.online:
        
        if canal:
            if mensagem_online_alternada:
                mensagem = f"🟢 O Baitola **{after.display_name}** está online! Bora Baitolaaaaa! 🎮"
            else:
                mensagem = f"🪖 O baitola **{after.display_name}** está online! Bora jogar, miseráaa! 🎯"            
            mensagem_online_alternada = not mensagem_online_alternada
            await canal.send(mensagem)
            adicionar_ponto(after.id, "online")

    if before.activity and hasattr(before.activity, 'name'):
        jogo = before.activity.name.lower()
        if "call of duty" in jogo:
            if canal:
                await canal.send(f"🎮 O baitola **{after.display_name}** começou a jogar **Warzone**! Bora dropar, soldado!")

        else:
            if canal:
                await canal.send(f"🚨 TRAIÇÃO DETECTADA! 🚨\n"
                    f"❌ O corno **{after.display_name}** está jogando **{after.activity.name}** "
                    f"ao invés de dropar no Warzone com o esquadrão!\n"
                    f"🤦‍♂️ Vergonha do clã!"
                )

        # if before.activity and not after.activity:
        #     if canal:
        #         await canal.send(f"🚪 O baitola **{after.display_name}** saiu do jogo. Fim da missão!🔚")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    
    if before.channel is None and after.channel is not None:
        canal = encontrar_canal_geral(member.guild)
        if canal:
            mensagem = f"🔊 O Baitola **{member.display_name}** entrou em **{after.channel.name}** e está jogando sem você! Bora Baitolaaaaa! 🎮"
            await canal.send(mensagem)
            adicionar_ponto(member.id, "voz")

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


def carregar_ranking():
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_ranking(data):
    with open(RANKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

def adicionar_ponto(user_id, tipo):
    data = carregar_ranking()
    if str(user_id) not in data:
        data[str(user_id)] = {"voz": 0, "online": 0, "mencionado": 0}

    data[str(user_id)][tipo] += 1
    salvar_ranking(data)

@tasks.loop(hours=24)
async def resetar_ranking():
    agora = datetime.now()
    if agora.weekday() == 6 and agora.hour == 0:
        data = carregar_ranking()
        if data:
            campeao_id = None
            campeao_pontos = 0

            for user_id, pontos in data.items():
                total = sum(pontos.values())
                if total > campeao_pontos:
                    campeao_pontos = total
                    campeao_id = user_id

            for guild in bot.guilds:
                canal = encontrar_canal_geral(guild)
                if canal:
                    if campeao_id:
                        membro = guild.get_member(int(campeao_id))
                        nome = membro.display_name if membro else "Desconhecido"
                        await canal.send(
                            f"👑 **O Baitola Supremo da Semana foi {membro.mention if membro else nome}!**\n"
                            f"Com um total de **{campeao_pontos} pontos**, sua baitolagem atingiu níveis lendários! 💅🔥"
                        )
                    await canal.send("🧹 Ranking semanal resetado! Começou a nova corrida dos baitolas 🔥")

        salvar_ranking({})

@bot.command(name="ranking")
async def ranking(ctx):
    data = carregar_ranking()
    if not data:
        await ctx.send("😴 Ninguém fez nada ainda essa semana! Vamos jogar, baitolas!")
        return

    membros = []
    for user_id, pontos in data.items():
        membro = ctx.guild.get_member(int(user_id))
        nome = membro.display_name if membro else f"Desconhecido ({user_id})"
        total = sum(pontos.values())
        membros.append((nome, total, pontos))

    membros.sort(key=lambda x: x[1], reverse=True)

    embed = discord.Embed(
        title="🏅 Top Baitolas da Semana",
        description="Ranking dos mais ativos do Baitolas Club!",
        color=discord.Color.orange()
    )

    for i, (nome, total, pontos) in enumerate(membros[:10], start=1):
        embed.add_field(
            name=f"{i}. {nome}",
            value=f"🎧 Voz: {pontos['voz']} | 🟢 Online: {pontos['online']} | 💬 Mencionado: {pontos['mencionado']} | Total: {total}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    respostas = {
        "camper": [
            "👀 Alguém falou de camper? Aposto que foi o {nome} de novo!",
            "🚽 {nome} tá camperando desde o drop, certeza!",
            "📦 Camper detectado! {nome}, sai do mato!"
        ],
        "dropa": [
            "🪂 Boraaaa dropar, baitolaaaa!",
            "🎯 Drop confirmado, {nome}!",
            "🪖 {nome}, espero que você não caia longe dessa vez!"
        ],
        "ganhamos": [
            "🏆 Ganhou nada, {nome}. Quero ver o print!",
            "🔥 Boraaaa! Até que enfim uma vitória decente!",
            "💪 É isso, {nome}! Agora repete pra provar que não foi sorte!"
        ],
        "lag": [
            "📶 Cuidado, {nome}, o lag é só desculpa pra morrer rápido 😆",
            "💥 Lag? Ou falta de skill mesmo? 👀"
        ]
    }

    msg = message.content.lower()
    for palavra, frases in respostas.items():
        if palavra in msg:
            resposta = random.choice(frases).format(nome=message.author.display_name)
            await message.channel.send(resposta)
            break  # só responde uma vez por mensagem

    await bot.process_commands(message)


if __name__ == '__main__':
    keep_alive()
    main()
