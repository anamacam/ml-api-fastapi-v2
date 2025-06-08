import axios, { AxiosInstance, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

// Configuración base de la API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Crear instancia de axios
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para requests
apiClient.interceptors.request.use(
  (config: any) => {
    // Agregar token si existe
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error: any) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para responses
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: any) => {
    console.error('❌ Response Error:', error);

    // Manejo de errores globales
    if (error.response?.status === 401) {
      toast.error('Sesión expirada. Por favor inicia sesión nuevamente.');
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      toast.error('No tienes permisos para realizar esta acción.');
    } else if (error.response?.status >= 500) {
      toast.error('Error del servidor. Por favor intenta más tarde.');
    }

    return Promise.reject(error);
  }
);

// Tipos para la API
export interface PredictionRequest {
  model_id: string;
  input_data: any;
  async_mode?: boolean;
}

export interface PredictionResponse {
  prediction_id: string;
  status: 'PROCESSING' | 'COMPLETED' | 'FAILED';
  result?: any;
  cached?: boolean;
  message?: string;
  created_at: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  type: string;
  version: string;
  description?: string;
  input_schema: any;
  output_schema: any;
  created_at: string;
  updated_at: string;
  status: 'ACTIVE' | 'INACTIVE' | 'TRAINING';
  metrics?: {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1_score?: number;
  };
}

export interface HealthCheck {
  status: string;
  timestamp: string;
  service: string;
  version: string;
  uptime?: number;
  checks?: {
    database?: { status: string; connection?: string; error?: string };
    redis?: { status: string; connection?: string; error?: string };
    system?: {
      status: string;
      cpu_percent?: number;
      memory_percent?: number;
      disk_percent?: number;
    };
  };
}

// Servicios de la API
export const apiService = {
  // Health Check
  async getHealth(): Promise<HealthCheck> {
    const response = await apiClient.get('/health/');
    return response.data;
  },

  async getDetailedHealth(): Promise<HealthCheck> {
    const response = await apiClient.get('/health/detailed');
    return response.data;
  },

  // Predicciones
  async createPrediction(request: PredictionRequest): Promise<PredictionResponse> {
    const response = await apiClient.post('/predict/', request);
    return response.data;
  },

  async getPrediction(predictionId: string): Promise<PredictionResponse> {
    const response = await apiClient.get(`/predict/${predictionId}`);
    return response.data;
  },

  async listPredictions(params?: {
    limit?: number;
    offset?: number;
    model_id?: string;
    status?: string;
  }): Promise<{
    predictions: PredictionResponse[];
    total: number;
    limit: number;
    offset: number;
  }> {
    const response = await apiClient.get('/predict/', { params });
    return response.data;
  },

  async deletePrediction(predictionId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/predict/${predictionId}`);
    return response.data;
  },

  async batchPredict(requests: PredictionRequest[]): Promise<PredictionResponse[]> {
    const response = await apiClient.post('/predict/batch', requests);
    return response.data;
  },

  // Modelos
  async listModels(): Promise<ModelInfo[]> {
    const response = await apiClient.get('/models/');
    return response.data;
  },

  async getModel(modelId: string): Promise<ModelInfo> {
    const response = await apiClient.get(`/models/${modelId}`);
    return response.data;
  },

  async uploadModel(
    file: File,
    metadata: {
      name: string;
      type: string;
      description?: string;
    }
  ): Promise<ModelInfo> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    const response = await apiClient.post('/upload/model', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent: any) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload progress: ${percentCompleted}%`);
        }
      },
    });
    return response.data;
  },

  async deleteModel(modelId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/models/${modelId}`);
    return response.data;
  },

  // Upload de archivos
  async uploadFile(
    file: File,
    type: 'dataset' | 'model' | 'other' = 'other'
  ): Promise<{
    filename: string;
    size: number;
    upload_id: string;
    url: string;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const response = await apiClient.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Utilidades
export const apiUtils = {
  /**
   * Construir URL completa para archivos estáticos
   */
  getFileUrl(path: string): string {
    return `${API_BASE_URL}/static/${path}`;
  },

  /**
   * Manejar errores de API de forma consistente
   */
  handleApiError(error: any): string {
    if (error?.response?.data?.detail) {
      return error.response.data.detail;
    } else if (error?.message) {
      return error.message;
    } else {
      return 'Ha ocurrido un error inesperado';
    }
  },

  /**
   * Formatear tamaño de archivo
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },
};

export default apiClient;
