import discord
from discord.ext import commands
import requests
import gestorDB
import json
import time
import os
import webserver

DISCORD_TOKEN = "MTI3MjI4NzA5NzI0NzUwMjM5Nw.GIjfLM."
DISCORD_TOKEN+="SXYUxnNwyO0IHylOUVqjZPprGm8PMamGvUrnCE"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxzM99Jfaq-OZMtvsSKTcHZ6uKHlTSznxGM4Mji1OhSD3F9jTvkbH-bYVRJoLKt24W_nA/exec"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='Dam ', intents=intents)

@bot.event
async def on_ready():
    gestorDB.create_tables()
    print(f'We have logged in as {bot.user}')

@bot.command()
async def test(ctx, *args):  # *args permite múltiples argumentos
    resposta = " ".join(args)
    await ctx.send(resposta)

@bot.command()
async def med(ctx, medalla: str, replay: str):
    usuario_id = ctx.author.id
    gestorDB.insert_medalla(usuario_id, medalla, replay)
    await ctx.send(f'✅ Medalla guardada: **{medalla}** (Replay: {replay})')

@bot.command()
async def verMeds(ctx):
    usuario_id = ctx.author.id
    meds = gestorDB.select_medallas_by_user(usuario_id)
    if meds:
        for nick, medalla, replay in meds:
            await ctx.send(f"🏅 Usuario: {nick}, Medalla: **{medalla}**, Replay: {replay}")
    else:
        await ctx.send("⚠️ No tienes medallas registradas.")

@bot.command()
async def eliminarMeds(ctx):
    usuario_id = ctx.author.id
    gestorDB.delete_medallas_by_user(usuario_id)
    await ctx.send("🗑️ ✅ Todas tus medallas han sido eliminadas.")

@bot.command()
async def registrar(ctx, nombre_usuario: str):
    """Registra un usuario con su nombre en la base de datos."""
    usuario_id = ctx.author.id
    gestorDB.insert_usuario(usuario_id, nombre_usuario)
    await ctx.send(f"✅ Te has registrado con éxito como: {nombre_usuario}")

def export_medallas_to_sheets(usuario_id):
    try:
        nombre_usuario = gestorDB.select_nombre_by_user(usuario_id)
        if not nombre_usuario:
            return "⚠️ No estás registrado. Usa `Nya registrar <nombre>` primero."

        medallas = gestorDB.select_medallas_by_user(usuario_id)
        medallas_formateadas = [[m[1], m[2]] for m in medallas]

        data = {
            "nombre_usuario": nombre_usuario,
            "medallas": medallas_formateadas
        }

        intentos = 3  # Número de intentos
        for i in range(intentos):
            try:
                response = requests.post(
                    GOOGLE_SCRIPT_URL, json=data, headers={"Content-Type": "application/json"}, timeout=10
                )
                response.raise_for_status()
                return f"✅ Exportación exitosa. Aquí tienes tu archivo: {response.text}"
            except requests.exceptions.Timeout:
                if i < intentos - 1:
                    time.sleep(2)  # Espera antes de reintentar
                    continue
                return "⏳ Error: La conexión a Google Script tardó demasiado."
            except requests.exceptions.RequestException as e:
                return f"❌ Error al exportar: {e}"

    except Exception as e:
        return f"❌ Error inesperado: {e}"

@bot.command()
async def exportarMeds(ctx):
    usuario_id = ctx.author.id
    resultado = export_medallas_to_sheets(usuario_id)
    await ctx.send(resultado)



@bot.command()
async def ranking(ctx):
    """Muestra el ranking de los 10 usuarios con más medallas."""
    top_usuarios = gestorDB.select_top_usuarios()

    if not top_usuarios:
        await ctx.send("⚠️ No hay medallas registradas aún.")
        return

    ranking_msg = "**🏆 Ranking de Medallas 🏆**\n\n"
    for i, (nombre_usuario, cantidad) in enumerate(top_usuarios, start=1):
        ranking_msg += f"**#{i}** - {nombre_usuario} 🏅 {cantidad} medallas\n"

    await ctx.send(ranking_msg)


webserver.keep_alive()
bot.run(DISCORD_TOKEN)
