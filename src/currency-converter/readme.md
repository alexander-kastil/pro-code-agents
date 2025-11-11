# Currency Converter

An Azure Functions-based REST API that provides real-time currency conversion using the Fixer.io exchange rate API. This serverless TypeScript application demonstrates building HTTP-triggered functions that integrate with external APIs to perform currency conversions between different currencies on current or historical dates.

## Description

The currency converter accepts conversion requests via HTTP POST, supporting conversions between multiple currencies using live or historical exchange rates from Fixer.io. The API automatically handles conversions through EUR (the Fixer.io free tier base currency) and returns the converted amount along with the exchange rate used.

## How to Run

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Configure the Fixer.io API key:**

   - Sign up at [Fixer.io](https://fixer.io/) to get a free API key
   - Create a `local.settings.json` file with your API key:
     ```json
     {
       "IsEncrypted": false,
       "Values": {
         "AzureWebJobsStorage": "",
         "FUNCTIONS_WORKER_RUNTIME": "node",
         "FIXER_KEY": "your_fixer_api_key_here"
       }
     }
     ```

3. **Start the Azure Functions runtime:**

   ```bash
   npm start
   ```

   The function will be available at `http://localhost:7071/api/convertTo`
