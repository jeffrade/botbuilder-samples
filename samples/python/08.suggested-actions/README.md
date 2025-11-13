# Suggested Actions

Bot Framework v4 using adaptive cards bot sample

This bot has been created using [Bot Framework](https://dev.botframework.com), it shows how to use suggested actions.  Suggested actions enable your bot to present buttons that the user can tap to provide input.

## To try this sample

- Clone the repository
```bash
git clone https://github.com/Microsoft/botbuilder-samples.git
```
- In a terminal, navigate to `botbuilder-samples\samples\python\08.suggested-actions` folder
- Activate your desired virtual environment
- In the terminal, type `pip install -r requirements.txt`
- Run your bot with `python app.py`

## Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the latest Bot Framework Emulator from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- File -> Open Bot
- Enter a Bot URL of `http://localhost:3978/api/messages`

## Interacting with the bot

Suggested actions enable your bot to present buttons that the user can tap to provide input. Suggested actions appear close to the composer and enhance user experience.
They enable the user to answer a question or make a selection with a simple tap of a button, rather than having to type a response with a keyboard.

Unlike buttons that appear within rich cards (which remain visible and accessible to the user even after being tapped), buttons that appear within the suggested actions pane will disappear after the user makes a selection. This prevents the user from tapping stale buttons within a conversation and simplifies bot development (since you will not need to account for that scenario).

## Environment Configuration

This bot uses different authentication adapters depending on the environment:

### Local Development (Bot Framework Emulator)
- Set the `BOT_ENV` environment variable to `dev`:
  ```bash
  BOT_ENV=dev python app.py
  ```
- The bot will use `BotFrameworkHttpAdapter` with no authentication
- In the Bot Framework Emulator, leave the "Microsoft App ID" and "Microsoft App password" fields **empty** when connecting

### Azure Deployment (Production)
- **Do not set** the `BOT_ENV` environment variable (it defaults to "production")
- The bot will use `CloudAdapter` with `ConfigurationBotFrameworkAuthentication`
- Azure will automatically provide the required credentials through environment variables:
  - `MicrosoftAppId`
  - `MicrosoftAppPassword`
  - `MicrosoftAppType` (defaults to "MultiTenant")
  - `MicrosoftAppTenantId`

**Important:** When creating a deployment package (zip file) for Azure, ensure `BOT_ENV` is not set in your Azure App Service configuration so it defaults to production mode with proper authentication.

## Deploy the bot to Azure (to learn more about deploying a bot to Azure, see [Deploy your bot to Azure](https://aka.ms/azuredeployment))

### Prerequisites
- Azure CLI installed and logged in (`az login`)
- Azure AD App Registration completed (App ID, App Secret, and Tenant ID)
- Resource Group created in Azure

### Deployment Steps

#### 1. Deploy Azure Infrastructure
Follow the instructions in [deploymentTemplates/deployUseExistResourceGroup/readme.md](deploymentTemplates/deployUseExistResourceGroup/readme.md) to:
- Deploy the App Service (template-BotApp-with-rg.json)
- Deploy the Bot Registration (template-AzureBot-with-rg.json)

Make sure to set `appType=SingleTenant` for Teams bots and provide your `tenantId`.

#### 2. Create Deployment Package
Create a zip file containing your bot code (from the root of this directory):

```bash
zip -r bot.zip app.py config.py bots/ requirements.txt -x "*.pyc" -x "*__pycache__*" -x "*.git*" -x ".env*" -x "*venv/*" -x "*.venv/*"
```

**Note:** The command above excludes common files that should NOT be deployed (`.env`, `.git`, `__pycache__`, virtual environments).

#### 3. Deploy Bot Code to Azure
Upload your bot code to the Azure App Service:

```bash
az webapp deployment source config-zip \
  --resource-group <your-resource-group-name> \
  --name <your-app-service-name> \
  --src bot.zip
```

#### 4. Verify Deployment
- Check that your bot is running: `https://<your-app-service-name>.azurewebsites.net`
- Check logs in Azure Portal: App Service → Log stream
- Test your bot endpoint: `https://<your-app-service-name>.azurewebsites.net/api/messages`

**Important:** The infrastructure templates automatically configure the required environment variables (`MicrosoftAppId`, `MicrosoftAppPassword`, etc.) from the deployment parameters. You do not need to set `BOT_ENV` - it defaults to "production" mode.

For more details, see [Deploy your bot to Azure](https://aka.ms/azuredeployment).

## Further reading

- [Bot Framework Documentation](https://docs.botframework.com)
- [Bot Basics](https://docs.microsoft.com/azure/bot-service/bot-builder-basics?view=azure-bot-service-4.0)
- [Suggested Actions](https://docs.microsoft.com/azure/bot-service/bot-builder-howto-add-suggested-actions?view=azure-bot-service-4.0&tabs=csharp#suggest-action-using-button)
- [Bot State](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-storage-concept?view=azure-bot-service-4.0)
- [Activity processing](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-concept-activity-processing?view=azure-bot-service-4.0)
- [Azure Bot Service Introduction](https://docs.microsoft.com/azure/bot-service/bot-service-overview-introduction?view=azure-bot-service-4.0)
- [Azure Bot Service Documentation](https://docs.microsoft.com/azure/bot-service/?view=azure-bot-service-4.0)
- [Azure CLI](https://docs.microsoft.com/cli/azure/?view=azure-cli-latest)
- [Azure Portal](https://portal.azure.com)
- [Channels and Bot Connector Service](https://docs.microsoft.com/en-us/azure/bot-service/bot-concepts?view=azure-bot-service-4.0)
