import discord
from discord.ext import commands
import requests
import gestorDB
import json
import time
import os
import webserver
import asyncio

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
    """Elimina todas las medallas de un usuario."""
    usuario_id = ctx.author.id
    success = gestorDB.delete_medallas_by_user(usuario_id)
    
    if success:
        await ctx.send("🗑️ ✅ Todas tus medallas han sido eliminadas.")
    else:
        await ctx.send("⚠️ No tienes medallas registradas o ocurrió un error al eliminarlas.")


@bot.command()
async def eliminarUsuario(ctx):
    """Elimina un usuario solo si no tiene medallas asociadas."""
    usuario_id = ctx.author.id
    try:
        success = gestorDB.delete_usuario(usuario_id)
        if success:
            await ctx.send("🗑️ ✅ Tu cuenta ha sido eliminada con éxito.")
        else:
            await ctx.send("⚠️ Ocurrió un error al intentar eliminar tu cuenta.")
    except ValueError as e:
        await ctx.send(f"⚠️ {str(e)}")


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
async def mutear(ctx, miembro: discord.Member, tiempo: int = 0):
    """Mutea a un usuario en el chat por un tiempo específico (en segundos). Si no se especifica tiempo, será indefinido."""

    # Verificamos si el autor del comando tiene permisos para mutear
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("⚠️ No tienes permisos para mutear usuarios en el chat.")
        return
    
    # Verificamos si el bot tiene permisos para mutear
    if not ctx.guild.me.guild_permissions.manage_messages:
        await ctx.send("⚠️ No tengo permisos para mutear usuarios en el chat.")
        return

    # Mutear al usuario en todos los canales de texto
    for canal in ctx.guild.text_channels:
        await canal.set_permissions(miembro, send_messages=False)
    
    await ctx.send(f"✅ {miembro.mention} ha sido muteado en el chat.")

    # Si se ha especificado un tiempo, desmutamos automáticamente después de ese tiempo
    if tiempo > 0:
        await asyncio.sleep(tiempo)  # Esperar el tiempo especificado
        # Restauramos los permisos del usuario para enviar mensajes
        for canal in ctx.guild.text_channels:
            await canal.set_permissions(miembro, send_messages=None)  # Restaurar permisos
        await ctx.send(f"✅ {miembro.mention} ha sido desmuteado después de {tiempo} segundos.")

@bot.command()
async def unmute(ctx, miembro: discord.Member):
    """Desmutea a un usuario en el chat, permitiéndole escribir nuevamente."""

    # Verificamos si el autor del comando tiene permisos para desmutear
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("⚠️ No tienes permisos para desmutear usuarios en el chat.")
        return
    
    # Verificamos si el bot tiene permisos para modificar permisos
    if not ctx.guild.me.guild_permissions.manage_messages:
        await ctx.send("⚠️ No tengo permisos para desmutear usuarios en el chat.")
        return

    # Restauramos los permisos del usuario en todos los canales de texto
    for canal in ctx.guild.text_channels:
        await canal.set_permissions(miembro, send_messages=None)  # Restaurar permisos
    
    await ctx.send(f"✅ {miembro.mention} ha sido desmuteado en el chat.")


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

@bot.event
async def on_command_error(ctx, error):
    """Maneja errores cuando un usuario ingresa un comando inválido."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"⚠️ El comando que intentaste usar no existe. Usa `Dam help` para ver los comandos disponibles.")
    else:
        # Si es otro error, lo mostramos en consola
        print(f"Error desconocido: {error}")


@bot.command()
async def ayuda(ctx):
    """Muestra la lista de comandos disponibles."""
    embed = discord.Embed(
        title="📜 Lista de Comandos Disponibles",
        description="Aquí tienes los comandos que puedes usar con el bot:",
        color=discord.Color.blue()
    )


    embed.add_field(name="💬 `Dam help`", value="Muestra esta lista de comandos.", inline=False)
    embed.add_field(name="🏅 `Dam med <medalla> <replay>`", value="Registra una medalla con su replay.", inline=False)
    embed.add_field(name="📜 `Dam verMeds`", value="Muestra todas tus medallas guardadas.", inline=False)
    embed.add_field(name="🗑️ `Dam eliminarMeds`", value="Elimina todas tus medallas registradas.", inline=False)
    embed.add_field(name="📝 `Dam registrar <nombre>`", value="Registra tu usuario en la base de datos.", inline=False)
    embed.add_field(name="📤 `Dam exportarMeds`", value="Exporta tus medallas a Google Sheets.", inline=False)
    embed.add_field(name="🏆 `Dam ranking`", value="Muestra el ranking de los 10 usuarios con más medallas.", inline=False)
    embed.add_field(name="🔇 `Dam mutear <@usuario>`", value="Restringe temporalmente a un usuario para que no pueda escribir.", inline=False)
    embed.add_field(name="🔊 `Dam unmute <@usuario>`", value="Restaura los permisos de escritura de un usuario.", inline=False)
    
    embed.set_footer(text="Usa 'Dam <comando>' para interactuar con el bot.")

    await ctx.send(embed=embed)


webserver.keep_alive()
bot.run(DISCORD_TOKEN)
