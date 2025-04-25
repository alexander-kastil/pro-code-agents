# Currency Converter Plugin

## Service Overview

The Currency Converter plugin is a TypeScript-based Azure Function that provides real-time and historical currency conversion capabilities using the Fixer.io API.

### Purpose and Functionality

This plugin allows users to:

- Convert amounts between different currencies
- Access both current and historical exchange rates
- Get detailed conversion information including rates and timestamps

### Key Features

- Support for multiple currencies via Fixer.io
- Historical currency data lookup
- Comprehensive error handling
- Request validation and sanitization
- Application Insights telemetry integration
- Support for both GET and POST request methods

### Tech Stack Breakdown

- **Runtime**: Node.js
- **Language**: TypeScript
- **Framework**: Azure Functions v4
- **External API**: Fixer.io (for currency exchange rates)
- **Monitoring**: Application Insights

## Development Guide

### Prerequisites

- Node.js 14.x or higher
- Azure Functions Core Tools v4
- Azurite for local storage emulation
- Fixer.io API key (free or paid tier)

### DevContainer Configuration

The plugin uses VS Code's built-in development container support for consistent development environments.

### Build and Execution Instructions

1. Install dependencies:

   ```
   npm install
   ```

2. Set up local settings:

   - Create or update `local.settings.json`:

   ```json
    {
    "IsEncrypted": false,
    "Values": {
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "FUNCTIONS_WORKER_RUNTIME": "node",
        "FIXER_KEY": "",
        "APPLICATIONINSIGHTS_CONNECTION_STRING": ""
    },
    "Host": {
        "LocalHttpPort": 7072,
        "CORS": "*"
    }
    }
   ```

3. Build the project:

   ```
   npm run build
   ```

4. Run locally:
   ```
   func start
   ```

### Dependencies on Other Services

- Requires Azurite (local storage emulation) for local development
- Depends on Fixer.io API for currency exchange rates

## Configuration Reference

| Config Key                            | Description                                                | Required | Default                    | Example                                                 |
| ------------------------------------- | ---------------------------------------------------------- | -------- | -------------------------- | ------------------------------------------------------- |
| FIXER_KEY                             | API key for accessing Fixer.io currency exchange API       | Yes      | None                       | abcdef1234567890                                        |
| APPLICATIONINSIGHTS_CONNECTION_STRING | Connection string for Azure Application Insights telemetry | No       | None                       | InstrumentationKey=00000000-0000-0000-0000-000000000000 |
| AzureWebJobsStorage                   | Storage account connection string                          | Yes      | UseDevelopmentStorage=true | DefaultEndpointsProtocol=https;AccountName=...          |

## API Reference

### GET/POST /api/convertTo

Converts an amount from one currency to another.

**Query Parameters / Request Body**:

| Parameter | Description                            | Required | Example    |
| --------- | -------------------------------------- | -------- | ---------- |
| from      | Source currency code (ISO 4217)        | Yes      | USD        |
| to        | Target currency code (ISO 4217)        | Yes      | EUR        |
| amount    | Amount to convert                      | Yes      | 100        |
| date      | Date for historical rates (YYYY-MM-DD) | No       | 2023-01-15 |

**Example GET Request**:

```
GET /api/convertTo?from=USD&to=EUR&amount=100&date=2023-01-15
```

**Example POST Request**:

```json
{
  "from": "USD",
  "to": "EUR",
  "amount": 100,
  "date": "2023-01-15"
}
```

**Response**:

```json
{
  "from": "USD",
  "to": "EUR",
  "amount": 100,
  "result": 92.34,
  "rate": 0.9234,
  "date": "2023-01-15"
}
```
