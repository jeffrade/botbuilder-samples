# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
from datetime import datetime
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    TurnContext,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.core import BotFrameworkAdapterSettings
from botbuilder.integration.aiohttp import BotFrameworkHttpAdapter
from botbuilder.schema import Activity, ActivityTypes

from bots import SuggestActionsBot
from config import DefaultConfig

CONFIG = DefaultConfig()

# Validate production configuration
if CONFIG.ENV != "dev":
    if not CONFIG.APP_ID or not CONFIG.APP_PASSWORD:
        raise ValueError(
            "Production mode requires MicrosoftAppId and MicrosoftAppPassword environment variables. "
            "Set these in Azure App Service Configuration → Application settings."
        )

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
if CONFIG.ENV == "dev":
    # For local development without auth, use BotFrameworkHttpAdapter with empty credentials
    SETTINGS = BotFrameworkAdapterSettings("", "")
    ADAPTER = BotFrameworkHttpAdapter(SETTINGS)
else:
    ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))

# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error

# Create Bot
BOT = SuggestActionsBot()


# Listen for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    if CONFIG.ENV == "dev":
        # BotFrameworkHttpAdapter expects (activity, auth_header, bot)
        if "application/json" in req.headers.get("Content-Type", ""):
            body = await req.json()
        else:
            return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")

        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        if response:
            return json_response(data=response.body, status=response.status)
        return Response(status=HTTPStatus.OK)
    else:
        # CloudAdapter has a simpler API - just pass the request and bot
        return await ADAPTER.process(req, BOT)


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        if CONFIG.ENV == "dev":
            print(f"Starting Bot on http://{CONFIG.HOST}:{CONFIG.PORT}/api/messages in {CONFIG.ENV} mode...")
        else:
            print(f"Starting Bot in {CONFIG.ENV} mode on port {CONFIG.PORT}...")
            print(f"App Type: {CONFIG.APP_TYPE}, Tenant: {CONFIG.APP_TENANTID or 'default'}")
        web.run_app(APP, host=CONFIG.HOST, port=CONFIG.PORT)
    except Exception as error:
        raise error
