import React, { useState } from 'react';
import styled from 'styled-components';
import { ModalOverlay, ModalContent, ModalHeader, ModalBody, CloseButton, EditableTitle, EditableTitleInput } from '../common/Modal';
import { Button } from '../common/Button';
import { Textarea } from '../common/Textarea';
import { StatusBadge } from '../common/StatusBadge';
import { Loader } from '../common/Loader';
import { theme } from '../../styles/theme';

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
`;

const ContentBox = styled.div`
  padding: 16px;
  background: ${props => props.theme.colors.bgTertiary};
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  max-height: ${props => props.maxHeight || '400px'};
  overflow-y: auto;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

export const NoteModal = ({ note, onClose, onDelete, onProcess, onUpdate, onExport}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editedContent, setEditedContent] = useState(note.note_content || '');
    const [processing, setProcessing] = useState(false);
    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [editedTitle, setEditedTitle] = useState(note.title || '');
    const [saving, setSaving] = useState(false);
    const [downloading, setDownloading] = useState(false);

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const handleProcess = async () => {
        setProcessing(true);
        try {
            await onProcess(note.id);
            onClose();
        } catch (err) {
            alert('Processing failed: ' + err.message);
        } finally {
            setProcessing(false);
        }
    };

    const handleExportPdf = async () => {
        if (!onExport) return;

        setDownloading(true);
        try {
            await onExport(note.id);
        } catch (err) {
            alert('Failed to download PDF: ' + err.message);
        } finally {
            setDownloading(false);
        }
    };

    const handleDelete = async () => {
        if (window.confirm('Are you sure you want to delete this note?')) {
            try {
                await onDelete(note.id);
                onClose();
            } catch (err) {
                alert('Delete failed: ' + err.message);
            }
        }
    };

    const handleTitleSave = async () => {
        if (editedTitle === note.title) {
            setIsEditingTitle(false);
            return;
        }

        if (!onUpdate) return;

        setSaving(true);
        try {
            await onUpdate(note.id, { title: editedTitle });
            note.title = editedTitle; // update locally
            setIsEditingTitle(false);
        } catch (err) {
            alert('Failed to save title: ' + err.message);
        } finally {
            setSaving(false);
        }
    };

    const handleContentSave = async () => {
        if (editedContent === note.note_content || !onUpdate) {
            setIsEditing(false);
            return;
        }

        setSaving(true);
        try {
            await onUpdate(note.id, { note_content: editedContent });
            note.note_content = editedContent;
            setIsEditing(false);
        } catch (err) {
            alert('Failed to save note content: ' + err.message);
        } finally {
            setSaving(false);
        }
    };

    return (
        <ModalOverlay onClick={onClose}>
            <ModalContent maxWidth="800px" onClick={e => e.stopPropagation()}>
                <ModalHeader>
                    {isEditingTitle ? (
                        <EditableTitleInput
                            value={editedTitle}
                            onChange={(e) => setEditedTitle(e.target.value)}
                            onBlur={handleTitleSave}
                            onKeyDown={(e) => e.key === 'Enter' && handleTitleSave()}
                            autoFocus
                        />
                    ) : (
                        <EditableTitle onDoubleClick={() => setIsEditingTitle(true)} title="Double-click to edit">
                            {editedTitle}
                        </EditableTitle>
                    )}
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <StatusBadge status={note.status}>{note.status}</StatusBadge>
                        <CloseButton onClick={onClose}>✕</CloseButton>
                    </div>
                </ModalHeader>

                <ModalBody>
                    {/*{note.transcription && (*/}
                    {/*    <FormGroup>*/}
                    {/*        <Label>Transcription</Label>*/}
                    {/*        <ContentBox maxHeight="200px">*/}
                    {/*            {note.transcription}*/}
                    {/*        </ContentBox>*/}
                    {/*    </FormGroup>*/}
                    {/*)}*/}

                    {/*<FormGroup>*/}
                    {/*    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>*/}
                    {/*        <Label>Note Content</Label>*/}
                    {/*        {note.note_content && (*/}
                    {/*            <Button*/}
                    {/*                size="sm"*/}
                    {/*                variant="secondary"*/}
                    {/*                onClick={() => setIsEditing(!isEditing)}*/}
                    {/*            >*/}
                    {/*                {isEditing ? '👁️ Preview' : '✏️ Edit'}*/}
                    {/*            </Button>*/}
                    {/*        )}*/}
                    {/*    </div>*/}
                    {/*    {note.note_content ? (*/}
                    {/*        isEditing ? (*/}
                    {/*            <Textarea*/}
                    {/*                value={editedContent}*/}
                    {/*                onChange={(e) => setEditedContent(e.target.value)}*/}
                    {/*                style={{ minHeight: '200px' }}*/}
                    {/*            />*/}
                    {/*        ) : (*/}
                    {/*            <ContentBox>*/}
                    {/*                {note.note_content}*/}
                    {/*            </ContentBox>*/}
                    {/*        )*/}
                    {/*    ) : (*/}
                    {/*        <ContentBox style={{ padding: '32px', textAlign: 'center', color: theme.colors.textMuted }}>*/}
                    {/*            No content available yet*/}
                    {/*        </ContentBox>*/}
                    {/*    )}*/}
                    {/*</FormGroup>*/}

                    <ButtonGroup>
                        {note.status === 'pending' && !note.note_content && (
                            <Button onClick={handleProcess} disabled={processing}>
                                {processing ? <Loader size="20px" /> : '⚙️ Process Note'}
                            </Button>
                        )}
                        {note.status === 'processed' && note.note_content && (
                            <Button
                                onClick={handleExportPdf}
                                disabled={downloading}
                                variant="primary"
                            >
                                {downloading ? <Loader size="20px" /> : '📄 Export PDF'}
                            </Button>
                        )}
                        <Button variant="danger" onClick={handleDelete}>
                            🗑️ Delete
                        </Button>
                    </ButtonGroup>
                </ModalBody>
            </ModalContent>
        </ModalOverlay>
    );
};
