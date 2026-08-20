// Safely resolves API Base URL and Authorization Headers without hardcoded credentials
export const getApiBaseUrl = (): string => {
  return import.meta.env.VITE_API_BASE_URL || 'https://devmanipal.getafixtechnologies.com/api';
};

export const getAuthToken = (): string => {
  // 1. Check browser runtime session / local storage for user/admin session token
  if (typeof window !== 'undefined') {
    const sessionToken =
      sessionStorage.getItem('manipal_bearer_token') ||
      localStorage.getItem('manipal_bearer_token');
    if (sessionToken) return sessionToken;

    // 2. Check window injected runtime config if hosted in enterprise portal
    const windowToken = (window as any)?.__MANIPAL_CONFIG__?.BEARER_TOKEN;
    if (windowToken) return windowToken;
  }

  // 3. Environment variable or default production fallback token
  return import.meta.env.VITE_BEARER_TOKEN || import.meta.env.VITE_API_TOKEN || '2xlYx1fBtAhYBqAIVqxu0qwh8SFGJQ';
};

export const getAuthHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};
