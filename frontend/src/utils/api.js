const API_KEY = import.meta.env.VITE_CANVAS_API_KEY || '';
let _getToken = null;

export function setTokenGetter(fn) {
  _getToken = fn;
}

export function getAuthHeaders(extra = {}) {
  const headers = { ...extra };
  if (API_KEY) {
    headers['X-API-Key'] = API_KEY;
  }
  return headers;
}

export async function apiFetch(url, options = {}) {
  const headers = { ...(options.headers || {}) };

  if (_getToken) {
    try {
      const token = await _getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    } catch (e) {
      // Token refresh failed, continue without auth
    }
  }

  if (API_KEY) {
    headers['X-API-Key'] = API_KEY;
  }

  return fetch(url, { ...options, headers });
}
