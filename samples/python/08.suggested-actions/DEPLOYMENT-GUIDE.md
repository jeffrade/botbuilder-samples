# Azure Deployment Guide for Single-Tenant Teams Bot

## Prerequisites
✅ Azure CLI installed (`az --version`)
✅ Logged into Azure (`az login`)
✅ Azure AD App Registration completed with:
   - App ID: `88888888-4444-4444-4444-cccccccccccc`
   - App Secret: (regenerate if compromised)
   - Tenant ID: `88888888-4444-4444-4444-cccccccccccc`
✅ Resource group created in Azure

## Deployment Steps

### Step 1: Edit Local Parameters Files

**Important: Region Selection**
- For the App Service, choose a region with available quota, like `canadacentral`. Set this for `newAppServicePlanLocation` in `app-service-params.json`.
- The Azure Bot Service resource has limited regions. You **must** choose a supported region like `global`, `westeurope`, or `westus`. Set this for `azureBotRegion` in `azure-bot-params.json`.

Edit `app-service-params.json` (App Service parameters):
```json
{
  "appServiceName": "your-unique-app-service-name",
  "appType": "SingleTenant",
  "appId": "88888888-4444-4444-4444-cccccccccccc",
  "appSecret": "YOUR-REGENERATED-SECRET-HERE",
  "tenantId": "88888888-4444-4444-4444-cccccccccccc"
}
```

Edit `azure-bot-params.json` (Bot Registration parameters):
```json
{
  "azureBotId": "your-bot-name",
  "azureBotSku": "F0",  // Free tier, or "S1" for standard
  "botEndpoint": "https://your-app-service-name.azurewebsites.net/api/messages",
  "appType": "SingleTenant",
  "appId": "88888888-4444-4444-4444-cccccccccccc",
  "tenantId": "88888888-4444-4444-4444-cccccccccccc"
}
```

### Step 2: Deploy App Service (BotApp)

```bash
az deployment group create \
  --resource-group <YOUR-RESOURCE-GROUP> \
  --template-file deploymentTemplates/deployUseExistResourceGroup/template-BotApp-with-rg.json \
  --parameters @app-service-params.json
```

**Note:** This creates the App Service and automatically sets the environment variables (`MicrosoftAppId`, `MicrosoftAppPassword`, etc.)

### Step 3: Deploy Bot Code

Create deployment package:
```bash
zip -r bot.zip app.py config.py bots/ requirements.txt -x "*.pyc" -x "*__pycache__*" -x "*.git*" -x ".env*" -x "*venv/*" -x "*.venv/*"
```

Upload to Azure:
```bash
az webapp deployment source config-zip \
  --resource-group <YOUR-RESOURCE-GROUP> \
  --name <YOUR-APP-SERVICE-NAME> \
  --src bot.zip
```

### Step 4: Deploy Azure Bot Registration

```bash
az deployment group create \
  --resource-group <YOUR-RESOURCE-GROUP> \
  --template-file deploymentTemplates/deployUseExistResourceGroup/template-AzureBot-with-rg.json \
  --parameters @azure-bot-params.json
```

### Step 5: Verify Deployment

Check App Service logs:
```bash
az webapp log tail \
  --resource-group <YOUR-RESOURCE-GROUP> \
  --name <YOUR-APP-SERVICE-NAME>
```

Expected output:
```
Starting Bot in production mode on port 8080...
App Type: SingleTenant, Tenant: 88888888-4444-4444-4444-cccccccccccc
```

Test the endpoint:
```bash
curl https://<YOUR-APP-SERVICE-NAME>.azurewebsites.net/api/messages
```

## Local Development with Ngrok and Teams

This is a powerful workflow for testing your bot locally without deploying the code to Azure after every change.

### 1. Create `.export` file
Create a file named `.export` (and add it to `.gitignore`) to hold your local environment variables.
```bash
export MicrosoftAppId="88888888-4444-4444-4444-cccccccccccc"
export MicrosoftAppPassword="<YOUR-SECRET>"
export MicrosoftAppType="SingleTenant"
export MicrosoftAppTenantId="88888888-4444-4444-4444-cccccccccccc"
export AZURE_BOT_GROUP="default-group"
export AZURE_BOT_NAME="Local_08_Suggested_Actions"
export BOT_NGROK_SUBDOMAIN="<your-ngrok-subdomain>"
```

### 2. Run the Bot and Ngrok
- **Terminal 1:** Source the variables and run the bot.
  ```bash
  source .export && python app.py
  ```
- **Terminal 2:** Start ngrok to tunnel traffic to your bot's local port.
  ```bash
  ngrok http 3978
  ```
  *(Note: Use the subdomain from your `.export` file if you have a paid ngrok plan)*

### 3. Update Bot Endpoint
Update your Azure Bot's messaging endpoint to point to your public ngrok URL.
```bash
source .export && az bot update --name $AZURE_BOT_NAME --resource-group $AZURE_BOT_GROUP --endpoint "https://${BOT_NGROK_SUBDOMAIN}.ngrok-free.dev/api/messages"
```

### 4. Sideload Bot in Teams
To add the bot to Teams for testing, you must sideload a custom app package.
1.  **Create `manifest.json`:** Ensure the `id` and `botId` match your `MicrosoftAppId`, and add `*.ngrok-free.dev` to the `validDomains` array.
2.  **Create Icons:** `color.png` (192x192) and `outline.png` (32x32).
3.  **Create Zip Package:** Zip `manifest.json`, `color.png`, and `outline.png` together.
4.  **Upload to Teams:** In the Teams "Apps" section, use "Manage your apps" -> "Upload an app" -> "Upload a custom app" to upload your zip file.

You can now add the bot to a chat and test it in real-time. Messages from Teams will be securely routed to your local machine.

## Troubleshooting

### Bot fails to start with "Production mode requires MicrosoftAppId"
**Fix:** The ARM template didn't set the environment variables. Manually add them:
```bash
az webapp config appsettings set \
  --resource-group <YOUR-RG> \
  --name <YOUR-APP-SERVICE-NAME> \
  --settings \
    MicrosoftAppId="88888888-4444-4444-4444-cccccccccccc" \
    MicrosoftAppPassword="YOUR-SECRET" \
    MicrosoftAppType="SingleTenant" \
    MicrosoftAppTenantId="88888888-4444-4444-4444-cccccccccccc"
```

### AADSTS7000229: Missing Service Principal
**Error:** `Failed to get access token with error: invalid_client, error_description: AADSTS7000229: The client application <APP_ID> is missing service principal in the tenant...`

**Meaning:** The application registration exists in Azure AD, but it doesn't have a corresponding "instance" (a Service Principal) in your tenant to grant it permissions.

**Fix:** Create the Service Principal for your App ID.
```bash
az ad sp create --id <YOUR-APP-ID>
```

### 401 Unauthorized errors
- Verify your App Secret is correct (regenerate if needed)
- Check that `appType` is "SingleTenant" everywhere
- Verify `tenantId` matches your Azure AD

### Bot not responding in Teams
- Check Azure Portal logs for errors
- Verify the botEndpoint URL is correct
- Test endpoint with curl or Postman

## Security Checklist

- [ ] Never commit `app-service-params.json` or `azure-bot-params.json` to git
- [ ] Regenerated App Secret after any exposure
- [ ] `.gitignore` includes all local parameter files
- [ ] No secrets in source code files

## Reference

Official Microsoft Docs: https://learn.microsoft.com/en-us/azure/bot-service/provision-and-publish-a-bot?view=azure-bot-service-4.0&tabs=singletenant%2Cpython
