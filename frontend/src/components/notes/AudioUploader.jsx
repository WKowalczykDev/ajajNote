import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { Button } from '../common/Button';
import { Loader } from '../common/Loader';
import { AudioRecorder } from './AudioRecorder';
import { theme } from '../../styles/theme';

const UploadSection = styled.div`
    background: ${props => props.theme.colors.bgSecondary};
    border: 2px dashed ${props => props.theme.colors.border};
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 32px;
    text-align: center;
    transition: all ${props => props.theme.transitions.fast};

    ${props => props.isDragging && `
    border-color: ${props.theme.colors.primary};
    background: ${props.theme.colors.primary}10;
  `}
`;

export const AudioUploader = ({ onUpload }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = Array.from(e.dataTransfer.files);
        const audioFile = files.find(f => f.type.startsWith('audio/'));
        if (audioFile) await uploadFile(audioFile);
    };

    const handleFileSelect = async (e) => {
        const file = e.target.files[0];
        if (file) await uploadFile(file);
    };

    const uploadFile = async (file) => {
        setUploading(true);
        try {
            await onUpload(file);
        } catch (err) {
            alert('Upload failed: ' + err.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <UploadSection
            isDragging={isDragging}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            <div style={{ fontSize: '48px', marginBottom: '12px' }}>🎵</div>
            <h3 style={{ marginBottom: '8px' }}>Upload Audio File or Record Audio</h3>
            <p style={{ color: theme.colors.textMuted, fontSize: '14px', marginBottom: '8px' }}>
                Drag and drop or click to select (MP3, WAV)
            </p>

            <input
                ref={fileInputRef}
                type="file"
                accept="audio/mp3,audio/wav,audio/mpeg"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
            />

            <div style ={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '16px',        // space between the two buttons
                    marginTop: '16px'}}>
                <Button onClick={() => fileInputRef.current?.click()} disabled={uploading}>
                    {uploading ? <Loader size="20px" /> : '📁 Choose File'}
                </Button>
                <AudioRecorder onUpload={onUpload} />
            </div>
            <div style={{ marginTop: '32px', paddingTop: '32px', borderTop: `1px solid ${theme.colors.border}` }}>


            </div>
        </UploadSection>
    );
};