
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000000,
});

export async function submitQuery(query: string, bbox: number[]) {
  const resp = await api.post('/query', { query, bbox });
  return resp.data.task_id as string;
}

export async function getStatus(taskId: string) {
  const resp = await api.get(`/status/${taskId}`);
  return resp.data as { chain_of_thought: any; completed: boolean };
}

export async function getSummary(taskId: string) {
  const resp = await api.get(`/summary/${taskId}`);
  return resp.data as {
    summary: string;
    results: Array<{ lat: number; lon: number; area_m2: number }>;
    overlay_map: string | null;
  };
}

export async function fetchReports() {
  const resp = await api.get('/reports');
  return resp.data.reports as Array<{
    task_id: string;
    files: { name: string; url: string }[];
  }>;
}

export async function fetchRandomCandidates(
  taskId: string,
  limit = 10
): Promise<{ lat: number; lng: number }[]> {
  const resp = await api.get(`/candidates/${taskId}`, {
    params: { limit },
  });
  return resp.data.points;
}
export async function sendReportsEmail(taskId: string, email: string) {
  const { data } = await api.post("/email_reports", { task_id: taskId, email });
  return data as { message: string };
}