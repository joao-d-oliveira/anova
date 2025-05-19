import React, { useEffect } from "react";
import { Card, Container, Stack, Title, TextInput, PasswordInput, Checkbox, Button, Group, Text, Anchor, Image, Center } from "@mantine/core";
import { useForm } from '@mantine/form';
import { useRegister } from "../../mutations";

export default function Signup() {
    const { register } = useRegister();
    const form = useForm({
        initialValues: {
            name: '',
            email: '',
            phone: '',
            coachingLocation: '',
            role: '',
            password: '',
            confirmPassword: '',
            termsAccepted: false,
        },
        validate: {
            name: (value) => (value.trim().length < 2 ? 'Name must be at least 2 characters' : null),
            email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
            phone: (value) => (value.trim().length < 5 ? 'Please enter a valid phone number' : null),
            coachingLocation: (value) => (value.trim().length < 2 ? 'Please enter your coaching location' : null),
            role: (value) => (value.trim().length < 2 ? 'Please enter your role' : null),
            password: (value) => (value.length < 8 ? 'Password must be at least 8 characters' : null),
            confirmPassword: (value, values) =>
                value !== values.password ? 'Passwords do not match' : null,
            termsAccepted: (value) => (!value ? 'You must accept the terms and conditions' : null),
        },
    });

    const handleSubmit = (values: typeof form.values) => {
        register.mutate({
            name: values.name,
            email: values.email,
            phone_number: values.phone,
            school: values.coachingLocation,
            role: values.role,
            password: values.password,
            confirm_password: values.confirmPassword,
        });
    };

    useEffect(() => {
        if (register.isSuccess) {
            window.location.href = `/auth/login?message=${encodeURIComponent('Account created successfully. Please verify your email to continue.')}&messageType=success`;
        }
    }, [register.isSuccess]);

    return (
        <Container size="sm" mb="xl">
            <form onSubmit={form.onSubmit(handleSubmit)}>
                <Stack>
                    <Center my='sm'>
                        <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" />
                    </Center>
                    <Card>
                        <Card.Section p="md">
                            <Title order={2}>Create your Anova Account</Title>
                        </Card.Section>
                        <Stack p="md" gap="md">
                            <TextInput
                                label="Your name"
                                placeholder="Enter your full name"
                                required
                                {...form.getInputProps('name')}
                            />

                            <TextInput
                                label="Email address"
                                placeholder="Enter your email"
                                type="email"
                                required
                                {...form.getInputProps('email')}
                            />

                            <TextInput
                                label="Phone number"
                                placeholder="Enter your phone number"
                                type="tel"
                                required
                                {...form.getInputProps('phone')}
                            />

                            <TextInput
                                label="Where do you coach?"
                                placeholder="Enter your coaching location"
                                required
                                {...form.getInputProps('coachingLocation')}
                            />

                            <TextInput
                                label="What is your role?"
                                placeholder="Enter your role"
                                required
                                {...form.getInputProps('role')}
                            />

                            <PasswordInput
                                label="Create a password"
                                placeholder="Enter your password"
                                required
                                {...form.getInputProps('password')}
                            />

                            <PasswordInput
                                label="Confirm your password"
                                placeholder="Confirm your password"
                                required
                                {...form.getInputProps('confirmPassword')}
                            />

                            <Group>
                                <Checkbox
                                    label={
                                        <Group gap="4">
                                            <Text>I accept the</Text>
                                            <Anchor href="/terms" target="_blank">terms and conditions</Anchor>
                                        </Group>
                                    }
                                    {...form.getInputProps('termsAccepted', { type: 'checkbox' })}
                                />
                            </Group>
                        </Stack>
                    </Card>
                    <Button type="submit" fullWidth size="md" variant="filled">
                        Register
                    </Button>

                    <Button fullWidth size="md" variant="outline" component="a" href="/auth/login">
                        Already have an account? Log in
                    </Button>

                </Stack>
            </form>

        </Container>
    )
}