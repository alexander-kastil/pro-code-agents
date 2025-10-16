import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import * as appInsights from 'applicationinsights';

export async function convertTo(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
    const client = appInsights.defaultClient;
    const startTime = Date.now();
    const operationId = context.traceContext.traceParent;

    try {
        const body: any = await request.json().catch(() => ({}));
        const fromCurrency = request.query.get('from') || body.from;
        const toCurrency = request.query.get('to') || body.to;
        const amount = parseFloat(request.query.get('amount') || body.amount);
        const date = request.query.get('date') || body.date || new Date().toISOString().split('T')[0];
        const fixerKey = process.env.FIXER_KEY;

        if (!fromCurrency || !toCurrency || isNaN(amount) || !fixerKey) {
            client?.trackEvent({
                name: "CurrencyConversionValidationError",
                properties: {
                    fromCurrency,
                    toCurrency,
                    amount: amount?.toString(),
                    date
                }
            });
            return {
                status: 400,
                body: "Missing or invalid parameters. Required: from, to, amount"
            };
        }

        const baseUrl = date === new Date().toISOString().split('T')[0]
            ? 'http://data.fixer.io/api/latest'
            : `http://data.fixer.io/api/${date}`;

        const url = `${baseUrl}?access_key=${fixerKey}`;

        // Track API dependency
        const dependencyStartTime = Date.now();
        const response = await fetch(url);
        const data = await response.json();

        client?.trackRequest({
            name: "Fixer.io API",
            url: baseUrl,
            duration: Date.now() - dependencyStartTime,
            success: response.ok && data.success,
            resultCode: response.status.toString(),
            id: operationId
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (!data.success) {
            client?.trackException({
                exception: new Error(data.error?.info || 'Failed to get exchange rate'),
                properties: {
                    fromCurrency,
                    toCurrency,
                    date
                }
            });
            return {
                status: 400,
                body: JSON.stringify({
                    error: data.error?.info || 'Failed to get exchange rate'
                })
            };
        }

        // Convert through EUR (fixer.io free tier base currency)
        const fromRateInEur = data.rates[fromCurrency];
        const toRateInEur = data.rates[toCurrency];
        const rate = toRateInEur / fromRateInEur;
        const convertedAmount = amount * rate;

        // Track successful conversion with standard request duration
        const duration = Date.now() - startTime;
        client?.trackRequest({
            name: "Currency Conversion",
            url: request.url,
            duration: duration,
            success: true,
            resultCode: "200",
            properties: {
                fromCurrency,
                toCurrency,
                amount: amount.toString(),
                rate: rate.toString(),
                date
            }
        });

        return {
            body: JSON.stringify({
                from: fromCurrency,
                to: toCurrency,
                amount,
                result: convertedAmount,
                rate,
                date: data.date
            })
        };
    } catch (error) {
        client?.trackException({
            exception: error,
            properties: {
                message: error.message
            }
        });
        return {
            status: 500,
            body: JSON.stringify({
                error: "Error fetching exchange rates",
                details: error.message
            })
        };
    }
}

app.http('convertTo', {
    methods: ['GET', 'POST'],
    authLevel: 'anonymous',
    handler: convertTo
});
