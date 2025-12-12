import axios, { AxiosInstance } from 'axios';
import { Readable } from 'stream';

export interface QueryResponse {
    answer: string;
    [key: string]: any;
}

export interface ChatMessage {
    role: string;
    content: string;
    [key: string]: any;
}

export interface Skill {
    name: string;
    description: string;
    workflow_steps: any[];
    [key: string]: any;
}

export interface Reflection {
    task_description: string;
    failure_reason: string;
    lessons_learned: string[];
    [key: string]: any;
}

export interface TranscriptionResult {
    text: string;
    language?: string;
    segments?: any[];
}

export interface Plugin {
    name: string;
    version: string;
    author: string;
    description: string;
    loaded: boolean;
    enabled: boolean;
    error?: string;
}

export class LASClient {
    private client: AxiosInstance;

    constructor(baseURL: string = 'http://localhost:7777', apiKey?: string) {
        this.client = axios.create({
            baseURL: baseURL.replace(/\/$/, ''),
            headers: {
                'Content-Type': 'application/json',
                ...(apiKey ? { Authorization: `Bearer ${apiKey}` } : {}),
            },
        });
    }

    /**
     * Legacy Query Endpoint
     */
    async query(
        text: string,
        provider?: string,
        model?: string
    ): Promise<QueryResponse> {
        const payload: any = { query: text };
        if (provider) payload.provider = provider;
        if (model) payload.model = model;

        const response = await this.client.post('/api/query', payload);
        return response.data;
    }

    /**
     * Chat Completion (LiteLLM / OpenAI compatible)
     * Supports streaming if `stream: true` is passed in options.
     */
    async chat(
        messages: ChatMessage[],
        model: string = 'gpt-3.5-turbo',
        options: { stream?: boolean;[key: string]: any } = {}
    ): Promise<any | Readable> {
        const payload = {
            messages,
            model,
            ...options
        };

        const url = '/api/v1/litellm/chat/completions';

        if (options.stream) {
            const response = await this.client.post(url, payload, {
                responseType: 'stream'
            });
            return response.data; // Returns a Readable stream in Node environment
        } else {
            const response = await this.client.post(url, payload);
            return response.data;
        }
    }

    async listModels(): Promise<string[]> {
        const response = await this.client.get('/api/v1/litellm/models');
        return response.data.models;
    }

    async listProviders(): Promise<string[]> {
        const response = await this.client.get('/api/v1/litellm/providers');
        return response.data.providers;
    }

    // --- Memory & Skills ---

    async listSkills(): Promise<string[]> {
        const response = await this.client.get('/api/memory/skills');
        return response.data.skills || [];
    }

    async getSkill(name: string): Promise<Skill> {
        const response = await this.client.get(`/api/memory/skills/${name}`);
        return response.data;
    }

    async listReflections(taskType?: string, limit: number = 10): Promise<Reflection[]> {
        const params: any = { limit };
        if (taskType) params.task_type = taskType;

        const response = await this.client.get('/api/memory/reflections', { params });
        return response.data.reflections || [];
    }

    async getLessons(taskDescription: string, limit: number = 5): Promise<string[]> {
        const response = await this.client.get(
            `/api/memory/lessons/${encodeURIComponent(taskDescription)}`,
            { params: { limit } }
        );
        return response.data.lessons || [];
    }

    // --- Voice & Vision ---

    async transcribe(
        audioFile: Buffer | Blob,
        language?: string,
        modelSize: string = 'base'
    ): Promise<TranscriptionResult> {
        const formData = new FormData();
        // Check if Buffer (Node) or Blob (Browser) - simplistic check
        if (typeof Blob !== 'undefined' && audioFile instanceof Blob) {
            formData.append('file', audioFile);
        } else {
            // Node environment usually requires specific form-data handling or just buffers if supported by axios/backend
            // Assuming Node environment usage with form-data library might be needed if using 'FormData' global
            // For simplicity, passing as blob/file object is assumed handled by environment
            formData.append('file', new Blob([audioFile]));
        }

        formData.append('model_size', modelSize);
        if (language) formData.append('language', language);

        const response = await this.client.post('/api/voice/transcribe', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    }

    async synthesize(
        text: string,
        voiceId?: string,
        rate: number = 150
    ): Promise<ArrayBuffer> {
        const payload: any = { text, rate };
        if (voiceId) payload.voice_id = voiceId;

        const response = await this.client.post('/api/voice/synthesize', payload, {
            responseType: 'arraybuffer',
        });
        return response.data;
    }

    async analyzeImage(imageFile: Buffer | Blob, prompt: string = 'Describe this image'): Promise<string> {
        const formData = new FormData();
        if (typeof Blob !== 'undefined' && imageFile instanceof Blob) {
            formData.append('file', imageFile);
        } else {
            formData.append('file', new Blob([imageFile]));
        }
        formData.append('prompt', prompt);

        const response = await this.client.post('/api/voice/vision/analyze', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data.analysis;
    }

    // --- Plugins & Tools ---

    async listPlugins(): Promise<Plugin[]> {
        const response = await this.client.get('/api/plugins');
        return response.data.plugins || [];
    }

    async loadPlugin(name: string): Promise<{ status: string; plugin: string }> {
        const response = await this.client.post(`/api/plugins/load/${name}`);
        return response.data;
    }

    async healthCheck(): Promise<any> {
        const response = await this.client.get('/health');
        return response.data;
    }
}

export default LASClient;
