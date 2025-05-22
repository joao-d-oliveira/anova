import React, { useEffect, useState } from "react";
import { Card, Container, Stack, Title, TextInput, PasswordInput, Checkbox, Button, Group, Text, Anchor, Image, Center } from "@mantine/core";
import { useForm } from '@mantine/form';
import { useRegister } from "../../mutations";
import { successNotification } from "../../common/notifications";
import { filledButtonProps, outlineButtonProps } from "../../props/Button";
import { Head } from "vite-react-ssg";

function RegisterForm({ cbRegistered }: { cbRegistered: (email: string) => void }) {
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
            cbRegistered(form.values.email);
        }
    }, [register.isSuccess]);

    return (
        <form onSubmit={form.onSubmit(handleSubmit)}>
            <Stack>
                <Center my='sm'>
                    <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" />
                </Center>
                <Card>
                    <Card.Section p="md">
                        Create your Anova Account
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
                                        <Anchor href="/terms" target="_blank" td="underline">terms and conditions</Anchor>
                                    </Group>
                                }
                                {...form.getInputProps('termsAccepted', { type: 'checkbox' })}
                            />
                        </Group>
                    </Stack>
                </Card>
                <Button type="submit" fullWidth size="md" variant="filled" {...filledButtonProps}>
                    Register
                </Button>

                <Button fullWidth size="md" variant="outline" component="a" {...outlineButtonProps} href="/auth/login">
                    Already have an account? Log in
                </Button>
            </Stack>
        </form>
    )
}

function ConfirmAccount({ email }: { email: string }) {
    const { confirmAccount } = useRegister();
    const form = useForm({
        initialValues: {
            code: '',
        },
    });

    const handleSubmit = (values: typeof form.values) => {
        confirmAccount.mutate({
            email: email,
            code: values.code,
        });
    }

    useEffect(() => {
        if (confirmAccount.isSuccess) {
            window.location.href = '/dashboard';
        }
    }, [confirmAccount.isSuccess]);

    useEffect(() => {
        successNotification("Please check your email for a verification code");
    }, []);

    return (
        <form onSubmit={form.onSubmit(handleSubmit)}>
            <Stack>
                <Center my='sm'>
                    <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" />
                </Center>
                <Card>
                    <Card.Section p="md">
                        Confirm your email
                    </Card.Section>
                    <Stack p="md" gap="md">
                        <Text>Please enter the code sent to your email to confirm your account.</Text>
                        <TextInput
                            label="Verification code"
                            placeholder="Enter your verification code"
                            required
                            {...form.getInputProps('code')}
                        />
                    </Stack>
                </Card>
                <Button type="submit" fullWidth size="md" variant="filled" {...filledButtonProps}>
                    Confirm
                </Button>
            </Stack>
        </form>
    )
}


export default function Signup() {
    const [confirmEmail, setConfirmEmail] = useState<string | null>(null);
    return (
        <Container size="sm" mb="xl">
            <Head>
                <title>Anova | Signup</title>
            </Head>
            {confirmEmail === null ? <RegisterForm cbRegistered={(email) => setConfirmEmail(email)} /> : <ConfirmAccount email={confirmEmail} />}

        </Container>
    )
}