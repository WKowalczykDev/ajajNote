import React from 'react';
import styled from 'styled-components';
import { StatusBadge } from '../common/StatusBadge';

const Card = styled.div`
  background: ${props => props.theme.colors.bgSecondary};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all ${props => props.theme.transitions.fast};

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.lg};
    border-color: ${props => props.theme.colors.borderLight};
  }
`;

const CardHeader = styled.div`
    display: flex;
    justify-content: center;   // centers horizontally
    align-items: center;       // centers vertically
    height: 100%;              // allows vertical centering inside container
    margin-bottom: 12px;
    gap: 12px;                 // spacing between title and badge
`;

const Title = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: 4px;
  line-height: 1.4;
`;

const Date = styled.p`
  font-size: 13px;
  color: ${props => props.theme.colors.textMuted};
`;

const Footer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid ${props => props.theme.colors.border};
`;

const Filename = styled.span`
  font-size: 12px;
  color: ${props => props.theme.colors.textMuted};
`;

export const NoteCard = ({ note, onClick }) => {
    const formatDate = (dateInput) => {
        return '';
    };

    return (
        <Card onClick={onClick}>
            <CardHeader style={{alignContent: 'center', justifyContent: 'center'}}>
                <div>
                    <Title>{note.title}</Title>
                    {/*<Date>{formatDate(note.created_at)}</Date>*/}
                </div>
                <StatusBadge status={note.status}>{note.status}</StatusBadge>
            </CardHeader>

        </Card>
    );
};