import { useState, useEffect, useCallback } from 'react';
import { notesService } from '../services/notesService';

export const useNotes = () => {
    const [notes, setNotes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({ status: '', search: '', sortBy: 'date-desc' });

    const fetchNotes = useCallback(async () => {
        try {
            setLoading(true);
            const params = filters.status ? { status: filters.status } : {};
            const data = await notesService.getNotes(params);
            setNotes(data);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [filters.status]);

    useEffect(() => {
        fetchNotes();
    }, [fetchNotes]);

    const uploadAudio = async (file, title) => {
        const formData = new FormData();
        formData.append('audio', file);
        await notesService.uploadAudio(formData);
        await fetchNotes();
    };

    const processNote = async (id) => {
        await notesService.processNote(id);
        await fetchNotes();
    };

    const updateNote = async (id, updatedFields) => {
        console.log(id)
        try {
            const response = await notesService.updateNote(id, updatedFields);
            const updatedNote = response.note;

            setNotes(prev =>
                prev.map(n => (n.id === updatedNote.id ? updatedNote : n))
            );

            return updatedNote;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };

    const deleteNote = async (id) => {
        await notesService.deleteNote(id);
        setNotes(prev => prev.filter(n => n.id !== id));
    };

    const exportToPdf = async (id) => {
        try {
            await notesService.exportToPdf(id);
            return { success: true };
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };

    const getFilteredAndSortedNotes = () => {
        let filtered = [...notes];

        if (filters.search) {
            const search = filters.search.toLowerCase();
            filtered = filtered.filter(n =>
                n.title.toLowerCase().includes(search) ||
                (n.note_content && n.note_content.toLowerCase().includes(search))
            );
        }

        filtered.sort((a, b) => {
            switch (filters.sortBy) {
                case 'date-desc':
                    return new Date(b.created_at) - new Date(a.created_at);
                case 'date-asc':
                    return new Date(a.created_at) - new Date(b.created_at);
                case 'title-asc':
                    return a.title.localeCompare(b.title);
                case 'title-desc':
                    return b.title.localeCompare(a.title);
                default:
                    return 0;
            }
        });

        return filtered;
    };

    return {
        notes: getFilteredAndSortedNotes(),
        loading,
        error,
        filters,
        setFilters,
        uploadAudio,
        processNote,
        deleteNote,
        updateNote,
        exportToPdf,
        refreshNotes: fetchNotes,
    };
};