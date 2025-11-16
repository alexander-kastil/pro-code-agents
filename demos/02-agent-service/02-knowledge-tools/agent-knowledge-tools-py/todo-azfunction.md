# TODO: agents-azfunction.py

## Issue

The agent requires a deployed Azure Function for currency conversion.

## Required Actions

### 1. Deploy the Azure Function

You need to deploy an Azure Function that handles currency conversion. The function should:

- Accept POST requests with JSON payload
- Expected payload format:
  ```json
  {
    "from": "USD",
    "to": "EUR",
    "amount": 100,
    "date": "2024-01-15" // optional
  }
  ```
- Return response format:
  ```json
  {
    "result": 85.50,
    "date": "2024-01-15"
  }
  ```

### 2. Update Environment Variable

Once deployed, update `FUNCTION_DEPLOYMENT_URL` in your `.env` file:

**For Local Development:**

```
FUNCTION_DEPLOYMENT_URL="http://localhost:7071/api/convertTo"
```

**For Azure Deployment:**

```
FUNCTION_DEPLOYMENT_URL="https://your-function-app.azurewebsites.net/api/convertTo"
```

### 3. Create the Azure Function Code (Optional)

If you don't have the function yet, here's a sample implementation:

**function_app.py** (Python Azure Function):

```python
import azure.functions as func
import json
from datetime import datetime

app = func.FunctionApp()

@app.route(route="convertTo", methods=["POST"])
def currency_converter(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        from_currency = req_body.get('from')
        to_currency = req_body.get('to')
        amount = float(req_body.get('amount'))
        date = req_body.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Mock conversion rate - replace with actual API call
        conversion_rate = 0.85 if to_currency == 'EUR' else 1.2
        result = amount * conversion_rate

        return func.HttpResponse(
            json.dumps({
                "result": round(result, 2),
                "date": date
            }),
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=400,
            mimetype="application/json"
        )
```

## Test Command

```bash
python agents-azfunction.py
```

## Expected Behavior

The agent should:

1. Start an interactive chat session
2. Prompt: "Prompt (type 'quit' to exit):"
3. Accept currency conversion requests like:
   - "Convert 100 USD to EUR"
   - "How much is 50 GBP in USD?"
4. Call the Azure Function to perform conversion
5. Return the conversion result

## Interactive Usage

```
Prompt (type 'quit' to exit): Convert 100 USD to EUR
Assistant: 100 USD equals 85.00 EUR on 2024-01-15

Prompt (type 'quit' to exit): quit
```
