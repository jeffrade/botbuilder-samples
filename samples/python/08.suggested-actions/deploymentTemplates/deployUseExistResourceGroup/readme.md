# Usage
BotApp must be deployed prior to AzureBot.

### Command line:
`az login`<br>
`az deployment group create --resource-group <group-name> --template-file <template-file> --parameters @<parameters-file>`

## Parameters for template-BotApp-with-rg.json:

- **appServiceName**: (required)        The Name of the Bot App Service.
- (Pick an existing App Service Plan or create a new App Service Plan.)
  - **existingAppServicePlanName**:     The name of the App Service Plan.
  - **existingAppServicePlanLocation**: The location of the App Service Plan.
  - **newAppServicePlanName**:          The name of the App Service Plan.
  - **newAppServicePlanLocation**:      The location of the App Service Plan.
  - **newAppServicePlanSku**:           The SKU of the App Service Plan. Defaults to Standard values.
- **appType**:    Type of Bot Authentication. set as MicrosoftAppType in the Web App's Application Settings. **Allowed values are: MultiTenant(default), SingleTenant, UserAssignedMSI.**
- **appId**: (required)                                       Active Directory App ID or User-Assigned Managed Identity Client ID, set as MicrosoftAppId in the Web App's Application Settings.
- **appSecret**: (required for MultiTenant and SingleTenant)  Active Directory App Password, set as MicrosoftAppPassword in the Web App's Application Settings.
- **tenantId**:   The Azure AD Tenant ID to use as part of the Bot's Authentication. Only used for SingleTenant and UserAssignedMSI app types. Defaults to Subscription Tenant ID.

## Parameters for template-AzureBot-with-rg.json:

- **azureBotId**: (required)          The globally unique and immutable bot ID.
- **azureBotSku**:                    The pricing tier of the Bot Service Registration. Allowed values are: F0, S1(default).
- **azureBotRegion**:                 Specifies the location of the new AzureBot. Allowed values are: global(default), westeurope.
- **botEndpoint**:                    Use to handle client messages, Such as `https://<botappServiceName>.azurewebsites.net/api/messages`.
- **appType**:   Type of Bot Authentication. set as MicrosoftAppType in the Web App's Application Settings. Allowed values are: MultiTenant(default), SingleTenant, UserAssignedMSI.
- **appId**: (required)                                       Active Directory App ID or User-Assigned Managed Identity Client ID, set as MicrosoftAppId in the Web App's Application Settings.
- **tenantId**:  The Azure AD Tenant ID to use as part of the Bot's Authentication. Only used for SingleTenant and UserAssignedMSI app types. Defaults to Subscription Tenant ID.

## Step 3: Deploy Your Python Bot Code

After deploying the infrastructure above, you need to upload your Python bot code to the App Service.

### Create Deployment Package
Navigate to the bot's root directory (where `app.py` is located) and create a zip file:

```bash
cd ../../  # Navigate back to the bot root directory
zip -r bot.zip app.py config.py bots/ requirements.txt -x "*.pyc" -x "*__pycache__*" -x "*.git*" -x ".env*" -x "*venv/*" -x "*.venv/*"
```

**Note:** The command above excludes common files that should NOT be deployed (`.env`, `.git`, `__pycache__`, virtual environments).

### Deploy Code to Azure App Service
Upload your bot code to the Azure App Service created in Step 1:

```bash
az webapp deployment source config-zip \
  --resource-group <your-resource-group-name> \
  --name <your-app-service-name> \
  --src bot.zip
```

Replace:
- `<your-resource-group-name>` with your Azure resource group name
- `<your-app-service-name>` with the `appServiceName` you used in template-BotApp-with-rg.json

### Verify Deployment
- Check logs: Azure Portal → Your App Service → Log stream
- Test endpoint: `https://<your-app-service-name>.azurewebsites.net/api/messages`
- The bot should respond to messages from Teams or the Bot Framework Emulator (configured with your Azure bot)

**Important Notes:**
- The infrastructure templates automatically set `MicrosoftAppId`, `MicrosoftAppPassword`, `MicrosoftAppType`, and `MicrosoftAppTenantId` as App Service environment variables from your deployment parameters
- Do NOT set `BOT_ENV` environment variable in Azure - it defaults to "production" mode automatically
- For local development with Bot Framework Emulator, set `BOT_ENV=dev` when running locally
