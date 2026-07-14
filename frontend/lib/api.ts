import type {
  ProviderConfig,
  ProviderConfigUpdate,
  ProviderId,
  StreamEvent,
  TestConnectionResponse,
  ToneId,
} from "./types";
import { getApiBase, getStreamEndpoint } from "./backend-url.js";

function apiBase(): string {
  return getApiBase();
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = err.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join("; ")
          : res.statusText || "Request failed";
    throw new Error(message || "Request failed");
  }
  return res.json();
}

export async function getProviders(): Promise<ProviderConfig[]> {
  return request("/settings/providers");
}

export async function updateProvider(
  providerId: ProviderId,
  data: ProviderConfigUpdate
): Promise<ProviderConfig> {
  return request(`/settings/providers/${providerId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function testProvider(
  providerId: ProviderId,
  data?: { api_key?: string; model?: string; base_url?: string }
): Promise<TestConnectionResponse> {
  return request(`/settings/providers/${providerId}/test`, {
    method: "POST",
    body: JSON.stringify(data || {}),
  });
}

export async function repurposeArticleStream(
  article: string,
  onEvent: (event: StreamEvent) => void,
  options?: { providerId?: ProviderId; tone?: ToneId; formats?: string[] }
): Promise<void> {
  const streamUrl = getStreamEndpoint();
  const res = await fetch(streamUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      article,
      provider_id: options?.providerId,
      tone: options?.tone ?? "professional",
      formats: options?.formats,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Stream request failed");
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          onEvent(JSON.parse(line.slice(6)) as StreamEvent);
        } catch {
          console.warn("Skipping malformed SSE event:", line.slice(0, 120));
        }
      }
    }
  }
}
