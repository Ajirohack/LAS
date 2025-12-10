import { OpenAIStream, StreamingTextResponse } from 'ai';
import { Configuration, OpenAIApi } from 'openai-edge';

// Connect to LAS Backend
// We use the openai-edge library to connect to our custom backend
// by overriding the basePath.
const config = new Configuration({
    apiKey: process.env.OPENAI_API_KEY || 'dummy-key', // Key is required by SDK but might be ignored by local backend
    basePath: process.env.LAS_API_URL || 'http://localhost:8080/api/v1', // Proxy to LAS Core
});
const openai = new OpenAIApi(config);

export const runtime = 'edge';

export async function POST(req: Request) {
    const { messages, model } = await req.json();

    // In a real scenario, we might want to pass the provider/model 
    // to the backend if it supports dynamic selection via the OpenAI compatible endpoint.
    // For now, we assume the backend handles the routing based on the request.

    try {
        const response = await openai.createChatCompletion({
            model: model || 'gpt-4',
            stream: true,
            messages,
            // Pass extra parameters if your backend supports them
            // provider: provider 
        });

        // Check for errors from the backend
        if (response.status !== 200) {
            const errorText = await response.text();
            return new Response(errorText, { status: response.status });
        }

        const stream = OpenAIStream(response);
        return new StreamingTextResponse(stream);
    } catch (error: unknown) {
        console.error("Error in chat route:", error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return new Response(JSON.stringify({ error: errorMessage }), { status: 500 });
    }
}
