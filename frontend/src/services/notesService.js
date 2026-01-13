import { api } from './api';

export const notesService = {
    getNotes: async (params) => {
        const query = new URLSearchParams(params).toString();
        const response = await api.request(`/notes${query ? `?${query}` : ''}`);
        return response.notes || [];
    },
    getNote: (id) => api.request(`/notes/${id}`),
    uploadAudio: (formData) => api.request('/notes/send', { method: 'POST', body: formData }),
    processNote: (id) => api.request(`/notes/process/${id}`, { method: 'POST' }),
    deleteNote: (id) => api.request(`/notes/${id}`, { method: 'DELETE' }),
    updateNote: (id, data) => api.request(`/notes/${id}`, {
        method: 'PUT',
        body: data,
        headers: {
            'Content-Type': 'application/json'
        }
    }),
    exportToPdf: async (id) => {

        const blob = await api.request(`/notes/${id}/export/pdf`, {
            method: 'GET',
            responseType: 'blob'
        });

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `note_${id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        return { success: true };
    }
};
