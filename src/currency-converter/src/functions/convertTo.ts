import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";

export async function convertTo(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
    context.log(`Http function processed request for url "${request.url}"`);

    try {
        const body: any = await request.json().catch(() => ({}));
        const fromCurrency = body.from;
        const toCurrency = body.to;
        const amount = parseFloat(body.amount);
        const date = body.date || new Date().toISOString().split('T')[0];
        const fixerKey = process.env.FIXER_KEY;

        if (!fromCurrency || !toCurrency || isNaN(amount) || !fixerKey) {
            return {
                status: 400,
                body: "Missing or invalid parameters. Required: from, to, amount"
            };
        }

        const baseUrl = date === new Date().toISOString().split('T')[0]
            ? 'http://data.fixer.io/api/latest'
            : `http://data.fixer.io/api/${date}`;

        const url = `${baseUrl}?access_key=${fixerKey}`;

        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (!data.success) {
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
        return {
            status: 500,
            body: JSON.stringify({
                error: "Error fetching exchange rates",
                details: error.message
            })
        };
    }
};

app.http('convertTo', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: convertTo
});
