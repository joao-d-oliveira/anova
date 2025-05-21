import React, { useEffect, useState } from "react";
import { Card, Container, Stack, Title, TextInput, Button, Image, Center, Text, PasswordInput } from "@mantine/core";
import { useForm } from '@mantine/form';
import { useForgotPassword, useResetPassword } from "../../mutations";
import { successNotification } from "../../common/notifications";
import { filledButtonProps, outlineButtonProps } from "../../props/Button";

function RequestResetForm({ cbRequested }: { cbRequested: (email: string) => void }) {
    const { forgotPassword } = useForgotPassword();
    const form = useForm({
        initialValues: {
            email: '',
        },
        validate: {
            email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
        },
    });

    const handleSubmit = (values: typeof form.values) => {
        forgotPassword.mutate(values.email);
    };

    useEffect(() => {
        if (forgotPassword.isSuccess) {
            successNotification("If an account exists with this email, you will receive password reset instructions.");
            cbRequested(form.values.email);
        }
    }, [forgotPassword.isSuccess]);

    return (
        <Stack>
            <Center my='sm'>
                <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" />
            </Center>
            <Card>
                <Card.Section p="md">
                    Reset your password
                    <Text c='white' size="sm" mt="0" pb='2'>
                        Enter your email address and we'll send you instructions to reset your password.
                    </Text>
                </Card.Section>
                <form onSubmit={form.onSubmit(handleSubmit)}>
                    <Stack p="md" gap="md">
                        <TextInput
                            label="Email address"
                            placeholder="Enter your email"
                            type="email"
                            required
                            {...form.getInputProps('email')}
                        />
                        <Button type="submit" fullWidth size="md" {...filledButtonProps} loading={forgotPassword.isPending}>
                            Reset password
                        </Button>
                    </Stack>
                </form>
            </Card>

            <Button fullWidth size="md" variant="outline" component="a" {...outlineButtonProps} href="/auth/login">
                Back to login
            </Button>

            <Button fullWidth size="md" variant="outline" component="a" {...outlineButtonProps} href="/auth/signup">
                Don't have an account? Register here
            </Button>
        </Stack>
    );
}

function ResetPasswordForm({ email }: { email: string }) {
    const { resetPassword } = useResetPassword();
    const form = useForm({
        initialValues: {
            otp: '',
            password: '',
            confirmPassword: '',
        },
        validate: {
            otp: (value) => (value.trim().length < 1 ? 'Please enter the verification code' : null),
            password: (value) => (value.length < 8 ? 'Password must be at least 8 characters' : null),
            confirmPassword: (value, values) =>
                value !== values.password ? 'Passwords do not match' : null,
        },
    });

    const handleSubmit = (values: typeof form.values) => {
        resetPassword.mutate({
            email: email,
            otp: values.otp,
            new_password: values.password,
            confirm_password: values.confirmPassword,
        });
    };

    useEffect(() => {
        if (resetPassword.isSuccess) {
            successNotification("Your password has been reset successfully!");
            window.location.href = '/auth/login';
        }
    }, [resetPassword.isSuccess]);

    return (
        <Stack>
            <Center my='sm'>
                <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" />
            </Center>
            <Card>
                <Card.Section p="md">
                    Set new password
                    <Text c="white" size="sm" mt="0" pb='2'>
                        Enter the verification code sent to your email and choose a new password.
                    </Text>
                </Card.Section>
                <form onSubmit={form.onSubmit(handleSubmit)}>
                    <Stack p="md" gap="md">
                        <TextInput
                            label="Verification code"
                            placeholder="Enter the code from your email"
                            required
                            {...form.getInputProps('otp')}
                        />
                        <PasswordInput
                            label="New password"
                            placeholder="Enter your new password"
                            required
                            {...form.getInputProps('password')}
                        />
                        <PasswordInput
                            label="Confirm new password"
                            placeholder="Confirm your new password"
                            required
                            {...form.getInputProps('confirmPassword')}
                        />
                        <Button type="submit" fullWidth size="md" variant="filled" {...filledButtonProps} loading={resetPassword.isPending}>
                            Reset password
                        </Button>
                    </Stack>
                </form>
            </Card>

            <Button fullWidth size="md" variant="outline" component="a" {...outlineButtonProps} href="/auth/login">
                Back to login
            </Button>
        </Stack>
    );
}

export default function ForgotPassword() {
    const [resetEmail, setResetEmail] = useState<string | null>(null);
    
    return (
        <Container size="sm">
            {resetEmail === null ? (
                <RequestResetForm cbRequested={(email) => setResetEmail(email)} />
            ) : (
                <ResetPasswordForm email={resetEmail} />
            )}
        </Container>
    );
}