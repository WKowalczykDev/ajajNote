import React from 'react';
import { ThemeProvider } from 'styled-components';
import { GlobalStyles } from './styles/GlobalStyles';
import { theme } from './styles/theme';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AuthPage } from './pages/AuthPage';
import { DashboardPage } from './pages/DashboardPage';
import { Loader } from './components/common/Loader';
import styled from 'styled-components';

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
`;

const AppContent = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <LoadingContainer>
                <Loader />
            </LoadingContainer>
        );
    }

    return user ? <DashboardPage /> : <AuthPage />;
};

function App() {
    return (
        <ThemeProvider theme={theme}>
            <GlobalStyles />
            <AuthProvider>
                <AppContent />
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;