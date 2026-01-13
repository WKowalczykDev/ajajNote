const API_BASE_URL = 'http://localhost:5000';

export const api = {
    async request(endpoint, options = {}) {
        const { responseType, ...restOptions } = options;

        const config = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...restOptions.headers,
            },
            ...restOptions,
        };

        // Handle body serialization
        if (restOptions.body && !(restOptions.body instanceof FormData)) {
            config.body = JSON.stringify(restOptions.body);
        } else if (restOptions.body instanceof FormData) {
            delete config.headers['Content-Type']; // Let browser set for FormData
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

        if (!response.ok) {
            // Try JSON error, fallback to text
            const error = await response
                .json()
                .catch(async () => ({ message: await response.text() }));
            throw new Error(error.message || `HTTP ${response.status}`);
        }

        // Return appropriate response type
        if (responseType === 'blob') {
            return response.blob();
        } else if (responseType === 'text') {
            return response.text();
        } else {
            return response.json();
        }
    },
};
