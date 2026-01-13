import React, { useState } from 'react';
import styled from 'styled-components';
import { Button } from '../common/Button';
import { Loader } from '../common/Loader';
import { useAudioRecorder } from '../../hooks/useAudioRecorder';

const RecordingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: ${props => props.theme.colors.error}20;
  border: 1px solid ${props => props.theme.colors.error};
  border-radius: 8px;
  margin-bottom: 20px;

  .pulse {
    width: 12px;
    height: 12px;
    background: ${props => props.theme.colors.error};
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
`;

const UploadActions = styled.div`
  display: flex;
  justify-content: center;
`;

export const AudioRecorder = ({ onUpload }) => {
    const { isRecording, audioBlob, recordingTime, startRecording, stopRecording, resetRecording } = useAudioRecorder();
    const [uploading, setUploading] = useState(false);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handleUpload = async () => {
        if (!audioBlob) return;
        setUploading(true);
        try {
            const file = new File([audioBlob], `recording-${Date.now()}.webm`, { type: 'audio/webm' });
            await onUpload(file);
            resetRecording();
        } catch (err) {
            alert('Upload failed: ' + err.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            {isRecording && (
                <RecordingIndicator>
                    <div className="pulse" />
                    <span>Recording: {formatTime(recordingTime)}</span>
                </RecordingIndicator>
            )}

            {audioBlob && !isRecording && (
                <div style={{ marginBottom: '20px', textAlign: 'center' }}>
                    <audio controls src={URL.createObjectURL(audioBlob)} style={{ width: '100%', maxWidth: '400px' }} />
                </div>
            )}

            <UploadActions>
                {!isRecording && !audioBlob && (
                    <Button onClick={startRecording}>
                        🎤 Start Recording
                    </Button>
                )}

                {isRecording && (
                    <Button variant="danger" onClick={stopRecording}>
                        ⏹️ Stop Recording
                    </Button>
                )}

                {audioBlob && !isRecording && (
                    <>
                        <Button onClick={handleUpload} disabled={uploading}>
                            {uploading ? <Loader size="20px" /> : '📤 Upload Recording'}
                        </Button>
                        <Button variant="secondary" onClick={resetRecording}>
                            🔄 Reset
                        </Button>
                    </>
                )}
            </UploadActions>
        </div>
    );
};