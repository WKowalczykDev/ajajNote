import React, { useState } from 'react';
import { Form, FormGroup, Label, ErrorMessage } from './AuthStyles';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Loader } from '../common/Loader';
import { useAuth } from '../../context/AuthContext';

export const LoginForm = () => {
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await login(formData.email, formData.password);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    return (
        <>
            {error && <ErrorMessage>{error}</ErrorMessage>}

            <Form onSubmit={handleSubmit}>
                <FormGroup>
                    <Label>Email</Label>
                    <Input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="you@example.com"
                        required
                    />
                </FormGroup>

                <FormGroup>
                    <Label>Password</Label>
                    <Input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="••••••••"
                        required
                    />
                </FormGroup>

                <Button type="submit" disabled={loading} style={{ marginTop: '8px' }}>
                    {loading ? <Loader size="20px" /> : 'Sign In'}
                </Button>
            </Form>
        </>
    );
};