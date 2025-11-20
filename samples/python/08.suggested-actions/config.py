#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    ENV = os.environ.get("BOT_ENV", "production")
    HOST = os.environ.get("BOT_HOST", "0.0.0.0")  # 0.0.0.0 for Azure, localhost for local dev or ngrok
    PORT = int(os.environ.get("BOT_PORT") or os.environ.get("PORT", "3978"))  # Azure will provide PORT via env var
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "SingleTenant")
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")
