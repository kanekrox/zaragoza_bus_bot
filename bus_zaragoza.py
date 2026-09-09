import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("8934684718:AAEysYEXc_2yBKRmF5Raae1qK-WG5BTW8sQ")
PARADA_DEFECTO = "22"  # Cambia por tu poste habitual


async def obtener_tiempos_bus(id_parada: str) -> str:
    url = f"https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/transporte-urbano/poste-autobus/{id_parada}.json"
    headers = {"Accept": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 404:
                return f"⚠️ La parada `{id_parada}` no existe o no tiene datos."
            res.raise_for_status()
            data = res.json()

        lineas = data.get("destinos", [])
        if not lineas:
            return f"No hay autobuses próximos para la parada `{id_parada}`."

        mensaje = f"🚏 *Parada {id_parada}*\n\n"
        for item in lineas:
            linea = item.get("linea", "?")
            destino = item.get("destino", "Sin destino")
            minutos = item.get("minutos", "?")
            mensaje += f"• *Línea {linea}* ({destino}): `{minutos} min`\n"

        return mensaje
    except httpx.RequestError as e:
        return f"❌ Error de red: {e}"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Envíame `/bus` o `/bus <número_poste>` (ej: `/bus 230`).",
        parse_mode="Markdown",
    )


async def cmd_bus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_parada = context.args[0].strip() if context.args else PARADA_DEFECTO
    texto = await obtener_tiempos_bus(id_parada)
    await update.message.reply_text(texto, parse_mode="Markdown")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("bus", cmd_bus))
    print("Bot activo...")
    app.run_polling()