import '@mantine/dropzone/styles.css';

import { Card, Container, FileInput, Group, Stack, TextInput, Title, Text, Button } from "@mantine/core";
import { useUpload, useUser } from "../../mutations";
import Header from "../../components/dashboard/Header";
import { useForm } from "@mantine/form";
import { Dropzone } from '@mantine/dropzone';
import { IconPhoto, IconRefresh, IconUpload, IconX } from '@tabler/icons-react';
import { useEffect } from 'react';
import { errorNotification } from '../../common/notifications';
import { AuthProvider } from '../../providers/AuthProvider';

const UploadComponent = ({ form, field }: { form: any, field: string }) => {
    return (
        <Stack gap='xs'>
            <Text size='sm' fw={500}>Your Team Stats</Text>
            <Text size='xs' c="dimmed">
                These can be from the last game, the last 5 or 10 games, or the entire season. Currently, we only accept PDFs.
            </Text>
            {form.values[field] === null && (

                <Dropzone
                    onDrop={(files) => form.setFieldValue(field, files)}
                    onReject={(files) => errorNotification('Please upload a valid PDF file')}
                    maxSize={5 * 1024 ** 2}
                    accept={['application/pdf']}
                    {...form.getInputProps(field)}
                >
                    <Group justify="center" gap="xl" mih={120} style={{ pointerEvents: 'none' }}>
                        <Dropzone.Accept>
                            <IconUpload size={52} color="var(--mantine-color-blue-6)" stroke={1.5} />
                        </Dropzone.Accept>
                        <Dropzone.Reject>
                            <IconX size={52} color="var(--mantine-color-red-6)" stroke={1.5} />
                        </Dropzone.Reject>
                        <Dropzone.Idle>
                            <IconPhoto size={52} color="var(--mantine-color-dimmed)" stroke={1.5} />
                        </Dropzone.Idle>

                        <div>
                            <Text size="xl" inline>
                                Drag images here or click to select files
                            </Text>
                            <Text size="sm" c="dimmed" inline mt={7}>
                                Attach as many files as you like, each file should not exceed 5mb
                            </Text>
                        </div>
                    </Group>
                </Dropzone>
            )}
            {form.values[field] && form.values[field].length > 0 && (
                <Text size="sm" c="dimmed" mt={7}>
                    {form.values[field].map((file) => file.name).join(', ')}
                </Text>
            )}
            {form.errors[field] && (
                <Text size="sm" c="red" mt={7}>
                    {form.errors[field]}
                </Text>
            )}
        </Stack>
    )
}

export default function Dashboard() {
    const { data: user } = useUser();
    const { upload } = useUpload();

    const form = useForm({
        initialValues: {
            yourTeamName: '',
            yourTeamStats: null,
            opponentTeamName: '',
            opponentTeamStats: null,
            useLocalSimulation: true,
        },
        validate: {
            yourTeamName: (value) => value.length > 0 ? null : 'Team name is required',
            opponentTeamName: (value) => value.length > 0 ? null : 'Opponent team name is required',
            yourTeamStats: (value) => value !== null ? null : 'Team stats are required',
            opponentTeamStats: (value) => value !== null ? null : 'Opponent team stats are required',
        },
    });

    useEffect(() => {
        console.log(form.values);
    }, [form.values]);

    const handleSubmit = (values: any) => {
        upload.mutate({
            team_files: form.values.yourTeamStats[0],
            opponent_files: form.values.opponentTeamStats[0],
            team_name: form.values.yourTeamName,
            opponent_name: form.values.opponentTeamName
        });
    }

    useEffect(() => {
        if (upload.isSuccess) {
            console.log("Upload success", upload.data);
            window.location.href = `/dashboard/analysis?task_id=${upload.data.task_id}`;
        }
    }, [upload.isSuccess]);

    if (!user) {
        return <AuthProvider>
            <div>Loading...</div>
        </AuthProvider>;
    }

    return (
        <Container size="xl">
            <Header />
            <Title order={1} my='xl'>Upload Your Team and Opponent Stats to Get Started</Title>
            <form onSubmit={form.onSubmit(handleSubmit)}>
                <Stack>
                    <Group flex={1} w="100%" align="flex-start">
                        <Card style={{ flex: 1 }}>
                            <Card.Section p="md">
                                <Title order={2}>Enter your player stats</Title>
                            </Card.Section>
                            <Stack>
                                <TextInput label="Your Team Name" {...form.getInputProps('yourTeamName')} />
                                <UploadComponent form={form} field="yourTeamStats" />
                            </Stack>
                        </Card>
                        <Card style={{ flex: 1 }}>
                            <Card.Section p="md">
                                <Title order={2}>Enter your player stats</Title>
                            </Card.Section>
                            <Stack>
                                <TextInput label="Opponent Team Name" {...form.getInputProps('opponentTeamName')} />
                                <UploadComponent form={form} field="opponentTeamStats" />
                            </Stack>
                        </Card>
                    </Group>
                    <Group justify="center">
                        <Button type="submit" miw={120}>Submit</Button>
                        <Button variant="outline" type="reset" onClick={() => form.reset()} leftSection={<IconRefresh stroke={1.3} />}>Start Again</Button>
                    </Group>
                </Stack>
            </form>
        </Container>
    );
}