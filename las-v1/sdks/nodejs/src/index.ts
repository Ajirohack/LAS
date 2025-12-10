import axios, { AxiosInstance } from 'axios';

export interface QueryResponse {
    answer: string;
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

    constructor(baseURL: string = 'http://localhost:7777') {
        this.client = axios.create({
            baseURL: baseURL.replace(/\/$/, ''),
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }

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

    async listSkills(): Promise<string[]> {
        const response = await this.client.get('/api/memory/skills');
        return response.data.skills;
    }

    async getSkill(name: string): Promise<Skill> {
        const response = await this.client.get(`/api/memory/skills/${name}`);
        return response.data;
    }

    async listReflections(taskType?: string, limit: number = 10): Promise<Reflection[]> {
        const params: any = { limit };
        if (taskType) params.task_type = taskType;

        const response = await this.client.get('/api/memory/reflections', { params });
        return response.data.reflections;
    }

    async getLessons(taskDescription: string, limit: number = 5): Promise<string[]> {
        const response = await this.client.get(
            `/api/memory/lessons/${encodeURIComponent(taskDescription)}`,
            { params: { limit } }
        );
        return response.data.lessons;
    }

    async transcribe(
        audioFile: Buffer | Blob,
        language?: string,
        modelSize: string = 'base'
    ): Promise<TranscriptionResult> {
        const formData = new FormData();
        formData.append('file', audioFile);
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
        formData.append('file', imageFile);
        formData.append('prompt', prompt);

        const response = await this.client.post('/api/voice/vision/analyze', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data.analysis;
    }

    async listPlugins(): Promise<Plugin[]> {
        const response = await this.client.get('/api/plugins');
        return response.data.plugins;
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
