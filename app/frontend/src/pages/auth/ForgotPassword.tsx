import React from "react";
import { Card, Container, Stack, Title, TextInput, PasswordInput, Checkbox, Button, Group, Text, Anchor, Image, Center } from "@mantine/core";
import { useForm } from '@mantine/form';

export default function Signup() {
    const form = useForm({
        initialValues: {
            email: '',
        },
        validate: {
            email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
        },
    });

    const handleSubmit = (values: typeof form.values) => {
        console.log(values);
        // TODO: Implement form submission
    };

    return (
        <Container size="sm">
            <Stack>
                <Center my='sm'>
                    <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" />
                </Center>
                <Card>
                    <Card.Section p="md">
                        <Title order={2}>Reset your password</Title>
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
                        </Stack>
                    </form>
                </Card>
                <Button type="submit" fullWidth size="md" variant="filled">
                    Reset password
                </Button>

                <Button fullWidth size="md" variant="outline" component="a" href="/auth/login">
                    Log in
                </Button>

                <Button fullWidth size="md" variant="outline" component="a" href="/auth/signup">
                    Don't have an account? Register here
                </Button>
            </Stack>
        </Container>
    )
}