import React, { useState } from 'react';
import styled from 'styled-components';
import { Header } from '../components/layout/Header';
import { AudioUploader } from '../components/notes/AudioUploader';
import { NoteCard } from '../components/notes/NoteCard';
import { NoteModal } from '../components/notes/NoteModal';
import { Input } from '../components/common/Input';
import { Select } from '../components/common/Select';
import { Loader } from '../components/common/Loader';
import { useNotes } from '../hooks/useNotes';

const Container = styled.div`
    min-height: 100vh;
    display: flex;
    flex-direction: column;
`;

const MainContent = styled.main`
    flex: 1;
    padding: 32px;
    max-width: 1400px;
    width: 100%;
    margin: 0 auto;
`;

const TopBar = styled.div`
    display: flex;
    gap: 16px;
    margin-bottom: 32px;
    flex-wrap: wrap;
`;

const SearchBar = styled(Input)`
    flex: 1;
    min-width: 300px;
`;

const FiltersRow = styled.div`
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
`;

const NotesGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
`;

const EmptyState = styled.div`
    text-align: center;
    padding: 80px 20px;
    color: ${props => props.theme.colors.textSecondary};

    h3 {
        font-size: 20px;
        margin-bottom: 8px;
        color: ${props => props.theme.colors.text};
    }

    p {
        font-size: 14px;
    }
`;

const LoadingContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 80px;
`;

export const DashboardPage = () => {
    const { notes, loading, filters, setFilters, uploadAudio, processNote, deleteNote, updateNote, exportToPdf } = useNotes();
    const [selectedNote, setSelectedNote] = useState(null);

    return (
        <Container>
            <Header />

            <MainContent>
                <AudioUploader onUpload={uploadAudio} />

                {/*<TopBar>*/}
                {/*    <SearchBar*/}
                {/*        type="text"*/}
                {/*        placeholder="🔍 Search notes..."*/}
                {/*        value={filters.search}*/}
                {/*        onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}*/}
                {/*    />*/}
                {/*    <FiltersRow>*/}
                {/*        <Select*/}
                {/*            value={filters.status}*/}
                {/*            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}*/}
                {/*        >*/}
                {/*            <option value="">All Status</option>*/}
                {/*            <option value="pending">Pending</option>*/}
                {/*            <option value="processing">Processing</option>*/}
                {/*            <option value="completed">Completed</option>*/}
                {/*            <option value="failed">Failed</option>*/}
                {/*        </Select>*/}

                {/*        <Select*/}
                {/*            value={filters.sortBy}*/}
                {/*            onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}*/}
                {/*        >*/}
                {/*            <option value="date-desc">Newest First</option>*/}
                {/*            <option value="date-asc">Oldest First</option>*/}
                {/*            <option value="title-asc">Title A-Z</option>*/}
                {/*            <option value="title-desc">Title Z-A</option>*/}
                {/*        </Select>*/}
                {/*    </FiltersRow>*/}
                {/*</TopBar>*/}

                {loading ? (
                    <LoadingContainer>
                        <Loader />
                    </LoadingContainer>
                ) : notes.length === 0 ? (
                    <EmptyState>
                        <h3>No notes found</h3>
                        <p>Upload or record your first audio note to get started</p>
                    </EmptyState>
                ) : (
                    <NotesGrid>
                        {notes.map(note => (
                            <NoteCard
                                key={note.id}
                                note={note}
                                onClick={() => setSelectedNote(note)}
                            />
                        ))}
                    </NotesGrid>
                )}

                {selectedNote && (
                    <NoteModal
                        note={selectedNote}
                        onClose={() => setSelectedNote(null)}
                        onDelete={deleteNote}
                        onProcess={processNote}
                        onUpdate={updateNote}
                        onExport={exportToPdf}
                    />
                )}
            </MainContent>
        </Container>
    );
};