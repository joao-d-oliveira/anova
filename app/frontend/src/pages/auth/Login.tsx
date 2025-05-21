import React from "react";
import { Card, Container, Stack, Title, TextInput, Button, Image, Center } from "@mantine/core";
import { useForm } from '@mantine/form';
import { useLogin } from "../../mutations";
import { filledButtonProps, outlineButtonProps } from "../../props/Button";

export default function Login() {
    const { login } = useLogin();

    const form = useForm({
        initialValues: {
            email: '',
            password: '',
        },
        validate: {
            email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
            password: (value) => (value.length < 8 ? 'Password must be at least 8 characters' : null),
        }
    });

    const handleSubmit = (values: typeof form.values) => {
        console.log(values);
        login.mutate(values);
    };

    return (
        <Container size="sm">
            <form onSubmit={form.onSubmit(handleSubmit)}>
                <Stack>
                    <Center my='sm'>
                        <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" />
                    </Center>
                    <Card>
                        <Card.Section p="md">
                            Log in to your Anova Account
                        </Card.Section>
                        <Stack p="md" gap="md">
                            <TextInput
                                label="Email address"
                                placeholder="Enter your email address"
                                type="email"
                                required
                                {...form.getInputProps('email')}
                            />

                            <TextInput
                                label="Password"
                                placeholder="Enter your password"
                                type="password"
                                required
                                {...form.getInputProps('password')}
                            />
                        </Stack>
                    </Card>
                    <Button type="submit" fullWidth size="md" variant="filled" {...filledButtonProps}>
                        Log in
                    </Button>

                    <Button fullWidth size="md" variant="outline" component="a" {...outlineButtonProps} href="/auth/forgot-password">
                        Forgot your password?
                    </Button>

                    <Button fullWidth size="md" variant="outline" component="a" {...outlineButtonProps} href="/auth/signup">
                        Don't have an account? Register here
                    </Button>
                </Stack>
            </form>
        </Container>
    )
}