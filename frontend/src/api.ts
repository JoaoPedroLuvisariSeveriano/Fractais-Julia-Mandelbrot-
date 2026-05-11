export type FractalType = 'julia' | 'mandelbrot';
export type ColoringMode = 'iteration' | 'magnitude' | 'smoothed';
export type OutputFormat = 'png' | 'svg';

export type FractalPayload = {
  type: FractalType;
  step: number;
  width: number;
  height: number;
  max_iter: number;
  palette: string | string[];
  mode: ColoringMode;
  format: OutputFormat;
  escape_radius?: number;
  real: number;
  imag: number;
};


export type PalettesResponse = { palettes: string[] };

export function getApiBaseUrl(): string {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (typeof envUrl === 'string' && envUrl.trim().length > 0) return envUrl;
  return 'http://127.0.0.1:8000';
}

export async function fetchPalettes(signal?: AbortSignal): Promise<string[]> {
  const res = await fetch(`${getApiBaseUrl()}/palettes`, { method: 'GET', signal });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Failed to fetch palettes: ${res.status} ${text}`);
  }
  const json = (await res.json()) as PalettesResponse;
  return json.palettes;
}

export async function generateFractal(
  payload: FractalPayload,
  signal?: AbortSignal,
): Promise<{ blob: Blob; contentType: string }> {
  const res = await fetch(`${getApiBaseUrl()}/fractal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Failed to generate fractal: ${res.status} ${text}`);
  }

  const blob = await res.blob();
  const contentType = res.headers.get('content-type') || '';
  return { blob, contentType };
}

