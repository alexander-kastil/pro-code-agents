import { z } from "zod";
import { app, InvocationContext } from "@azure/functions";
// Define the currency validation schema using zod
const currencyConversionSchema = z.object({
    from: z.string().describe("Source currency code (e.g., USD, EUR)"),
    to: z.string().describe("Target currency code (e.g., USD, EUR)"),
    amount: z.number().positive().describe("Amount to convert"),
    date: z.string().optional().describe("Optional date in YYYY-MM-DD format (defaults to today)")
});

/**
 * MCP Tool handler for currency conversion
 * @param _toolArguments - Tool arguments (not used directly, comes from context)
 * @param context - Invocation context with metadata
 * @returns Promise with conversion result as JSON string
 */
export async function convertCurrency(
    _toolArguments: unknown,
    context: InvocationContext
): Promise<string> {
    context.log("Currency Conversion MCP Tool triggered");

    // Retrieve mcptool arguments from trigger metadata
    const mcptoolargs = context.triggerMetadata.mcptoolargs as {
        from?: string;
        to?: string;
        amount?: number;
        date?: string;
    };

    if (!mcptoolargs) {
        context.log("No arguments provided for currency conversion");
        return JSON.stringify({ error: "Missing conversion parameters" });
    }

    const from = mcptoolargs.from;
    const to = mcptoolargs.to;
    const amount = mcptoolargs.amount;
    const date = mcptoolargs.date || new Date().toISOString().split('T')[0];
    const fixerKey = process.env.FIXER_KEY;

    if (!from || !to || !amount || !fixerKey) {
        return JSON.stringify({
            error: "Missing or invalid parameters. Required: from, to, amount"
        });
    }

    try {
        const baseUrl = date === new Date().toISOString().split('T')[0]
            ? 'http://data.fixer.io/api/latest'
            : `http://data.fixer.io/api/${date}`;

        const url = `${baseUrl}?access_key=${fixerKey}`;

        // Track API dependency
        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (!data.success) {
            return JSON.stringify({
                error: data.error?.info || 'Failed to get exchange rate'
            });
        }

        // Convert through EUR (fixer.io free tier base currency)
        const fromRateInEur = data.rates[from];
        const toRateInEur = data.rates[to];
        const rate = toRateInEur / fromRateInEur;
        const convertedAmount = amount * rate;

        return JSON.stringify({
            from: from,
            to: to,
            amount: amount,
            result: convertedAmount,
            rate: rate,
            date: data.date
        });
    } catch (error) {
        context.log("Error during currency conversion:", error);
        return JSON.stringify({
            error: "Error fetching exchange rates",
            details: error.message
        });
    }
}

// Register the MCP tool with the Function App - using array syntax for toolProperties instead of zod schema
app.mcpTool("convertCurrency", {
    toolName: "convertCurrency",
    description: "Convert amounts between different currencies with optional historical rates",
    toolProperties: [
        {
            propertyName: "from",
            propertyValue: "string",
            description: "Source currency code (e.g., USD, EUR)"
        },
        {
            propertyName: "to", 
            propertyValue: "string",
            description: "Target currency code (e.g., USD, EUR)"
        },
        {
            propertyName: "amount",
            propertyValue: "number",
            description: "Amount to convert"
        },
        {
            propertyName: "date",
            propertyValue: "string",
            description: "Optional date in YYYY-MM-DD format (defaults to today)"
        }
    ],
    handler: convertCurrency
});