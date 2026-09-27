import discord
from discord.ext import commands

# -------------------------------------------------------------
# CONFIGURACIÓN DE INTENCIONES (PERMISOS DEL BOT)
# -------------------------------------------------------------
intents = discord.Intents.default()
intents.members = True          # Detecta cuando se unen usuarios
intents.message_content = True  # Lee los comandos de texto

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------------------------------------------
# CLASE PARA EL SISTEMA DE TICKETS (BOTONES INTERACTIVOS)
# -------------------------------------------------------------
class BotonCerrarTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Cerrar Ticket", style=discord.ButtonStyle.red, custom_id="cerrar_ticket")
    async def cerrar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ El ticket se cerrará en 5 segundos...")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

class VistaTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟️ Abrir Ticket", style=discord.ButtonStyle.primary, custom_id="abrir_ticket")
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        categoria = discord.utils.get(guild.categories, name="🛠️ ━━━ 𝐒𝐎𝐏𝐎𝐑𝐓𝐄 ━━━")
        
        # Nombre del canal del ticket
        nombre_canal = f"ticket-{interaction.user.name.lower()}"
        
        # Verificar si ya tiene un ticket abierto
        canal_existente = discord.utils.get(guild.text_channels, name=nombre_canal)
        if canal_existente:
            await interaction.response.send_message(f"❌ Ya tienes un ticket abierto en {canal_existente.mention}", ephemeral=True)
            return

        # Permisos del canal privado
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Crear el canal privado en la categoría de soporte
        canal_ticket = await guild.create_text_channel(
            name=nombre_canal,
            category=categoria,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"🎟️ Ticket de Soporte - {interaction.user.name}",
            description="¡Hola! Describe tu problema o consulta aquí y un miembro del staff te atenderá lo antes posible.\n\nPara cerrar el ticket, haz clic en el botón de abajo.",
            color=discord.Color.green()
        )
        
        await canal_ticket.send(content=f"Bienvenido {interaction.user.mention}", embed=embed, view=BotonCerrarTicket())
        await interaction.response.send_message(f"✅ ¡Tu ticket ha sido creado en {canal_ticket.mention}!", ephemeral=True)

# -------------------------------------------------------------
# EVENTOS DEL BOT
# -------------------------------------------------------------
@bot.event
async def on_ready():
    # Registrar las vistas persistentes de botones
    bot.add_view(VistaTicket())
    bot.add_view(BotonCerrarTicket())
    print(f'¡DrEAK Bot iniciado con éxito como: {bot.user}!')
    await bot.change_presence(activity=discord.Game(name="DrEAK MANY Community | !ayuda"))

@bot.event
async def on_member_join(member):
    canal = discord.utils.get(member.guild.text_channels, name="📜・bienvenida")
    if canal:
        embed = discord.Embed(
            title=f"¡Bienvenido/a a {member.guild.name}! 🚀",
            description=f"Hola {member.mention}, pasa a revisar `#📢・anuncios` y disfruta de la comunidad.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="DrEAK MANY Community • ¡Pásala bien!")
        await canal.send(embed=embed)

# -------------------------------------------------------------
# COMANDOS BÁSICOS
# -------------------------------------------------------------
@bot.command()
async def hola(ctx):
    await ctx.send(f'¡Hola {ctx.author.mention}! ¿Qué tal?')

@bot.command()
async def ping(ctx):
    await ctx.send('¡Pong! 🏓')

# -------------------------------------------------------------
# COMANDO PARA ENVIAR EL PANEL DE TICKETS
# -------------------------------------------------------------
@bot.command()
async def panelticket(ctx):
    """Manda el mensaje panel con el botón interactivo para abrir tickets."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ No tienes permisos de Administrador.")
        return

    embed = discord.Embed(
        title="🛠️ Centro de Soporte y Tickets",
        description="¿Necesitas ayuda, tienes alguna duda o quieres hacer un reporte?\n\nHaz clic en el botón **🎟️ Abrir Ticket** de abajo para crear un canal privado con el Staff.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="DrEAK MANY Community • Sistema de Tickets")
    
    await ctx.send(embed=embed, view=VistaTicket())

# -------------------------------------------------------------
# COMANDO DE DIRECTOS Y ROLES
# -------------------------------------------------------------
@bot.command()
async def directo(ctx, *, juego: str = "Free Fire"):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ No tienes permisos de Administrador.")
        return

    canal = discord.utils.get(ctx.guild.text_channels, name="📢・anuncios")
    if canal:
        embed = discord.Embed(
            title="🔴 ¡ESTAMOS EN EN VIVO!",
            description=f"¡Atención {ctx.guild.name}! Ya estamos en directo jugando a **{juego}**.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await canal.send(content="@everyone", embed=embed)
        await ctx.send("✅ Alerta enviada.")
# -------------------------------------------------------------
# COMANDOS PARA CREAR CATEGORÍAS Y CANALES
# -------------------------------------------------------------

# 1. Crear una nueva Categoría
@bot.command()
async def crearcategoria(ctx, *, nombre: str):
    """Crea una categoría. Uso: !crearcategoria 🎮 ━━━ JUEGOS ━━━"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ No tienes permisos de Administrador.")
        return

    try:
        categoria = await ctx.guild.create_category(nombre)
        await ctx.send(f"✅ Categoría **{categoria.name}** creada con éxito.")
    except Exception as e:
        await ctx.send(f"❌ Error al crear la categoría: {e}")


# 2. Crear un Canal de Texto
@bot.command()
async def crearcanal(ctx, nombre: str, *, categoria_nombre: str = None):
    """Crea un canal de texto. Uso: !crearcanal free-fire JUEGOS"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ No tienes permisos de Administrador.")
        return

    categoria = None
    if categoria_nombre:
        categoria = discord.utils.find(lambda c: categoria_nombre.lower() in c.name.lower(), ctx.guild.categories)

    try:
        canal = await ctx.guild.create_text_channel(name=nombre, category=categoria)
        if categoria:
            await ctx.send(f"✅ Canal **#{canal.name}** creado en **{categoria.name}**.")
        else:
            await ctx.send(f"✅ Canal **#{canal.name}** creado con éxito.")
    except Exception as e:
        await ctx.send(f"❌ Error al crear el canal: {e}")


# 3. Crear un Canal de Voz
@bot.command()
async def crearvoz(ctx, nombre: str, *, categoria_nombre: str = None):
    """Crea un canal de voz. Uso: !crearvoz Sala-General SALA DE VOZ"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ No tienes permisos de Administrador.")
        return

    categoria = None
    if categoria_nombre:
        categoria = discord.utils.find(lambda c: categoria_nombre.lower() in c.name.lower(), ctx.guild.categories)

    try:
        canal = await ctx.guild.create_voice_channel(name=nombre, category=categoria)
        if categoria:
            await ctx.send(f"🔊 Canal de voz **{canal.name}** creado en **{categoria.name}**.")
        else:
            await ctx.send(f"🔊 Canal de voz **{canal.name}** creado con éxito.")
    except Exception as e:
        await ctx.send(f"❌ Error al crear el canal de voz: {e}")
# -------------------------------------------------------------
# COMANDO PARA CREAR EL CONTADOR DE MIEMBROS
# -------------------------------------------------------------
@bot.command()
async def crearcontador(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo los administradores pueden crear el contador.")
        return

    guild = ctx.guild
    # Cuenta los miembros que no son bots
    total_miembros = len([m for m in guild.members if not m.bot])

    # Bloquea el canal para que nadie se pueda conectar a hablar
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=False)
    }

    try:
        # Crea una categoría y un canal de voz con el conteo
        categoria = await guild.create_category("📊 ESTADÍSTICAS")
        canal = await guild.create_voice_channel(
            name=f"👥 Miembros: {total_miembros}",
            category=categoria,
            overwrites=overwrites
        )
        await ctx.send(f"✅ Contador creado con éxito: **{canal.name}**")
    except Exception as e:
        await ctx.send(f"❌ Ocurrió un error al crear el contador: {e}")

import os

# Lee el token desde las variables de entorno
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)