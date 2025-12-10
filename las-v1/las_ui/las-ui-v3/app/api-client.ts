import axios, { AxiosInstance } from 'axios';

interface QueryRequest {
    query: string;
    provider: string;
    model: string;
    stream?: boolean;
}

interface QueryResponse {
    response: string;
    metadata?: {
        provider: string;
        model: string;
        tokens?: number;
    };
}

class LASApiClient {
    private client: AxiosInstance;
    private baseURL: string;
    private token: string | null = null;

    constructor(baseURL: string = 'http://localhost:8080/api/v1') {
        this.baseURL = baseURL;
        this.client = axios.create({
            baseURL: this.baseURL,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Add request interceptor to attach token
        this.client.interceptors.request.use((config) => {
            if (this.token) {
                config.headers.Authorization = `Bearer ${this.token}`;
            }
            return config;
        });
    }

    setToken(token: string) {
        this.token = token;
    }

    async login(username: string, password: string) {
        const response = await this.client.post('/auth/login', null, {
            params: { username, password },
        });
        this.token = response.data.access_token;
        return response.data;
    }

    async register(username: string, email: string, password: string) {
        const response = await this.client.post('/auth/register', {
            username,
            email,
            password
        });
        return response.data;
    }

    async query(params: QueryRequest): Promise<QueryResponse> {
        const response = await this.client.post('/query', params);
        return response.data;
    }

    async getMemoryGraph() {
        const response = await this.client.get('/memory/knowledge-graph');
        return response.data;
    }

    async getCacheStats() {
        const response = await this.client.get('/perf/cache/stats');
        return response.data;
    }
}

export const lasApi = new LASApiClient();
export type { QueryRequest, QueryResponse };
