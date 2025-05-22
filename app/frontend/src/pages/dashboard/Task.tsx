import { useParams } from "react-router-dom";
import { useAnalysis } from "../../mutations";
import { Container, Loader, Stack, Text, Title } from "@mantine/core";
import Header from "../../components/dashboard/Header";
import { useEffect } from "react";
import { Head } from "vite-react-ssg";

export default function Task() {
    const searchParams = new URLSearchParams(window.location.search);
    const task_id = searchParams.get('task_id');
    const { status } = useAnalysis({ task_id: task_id as string })

    useEffect(() => {
        if (status.data?.status === "completed" && status.data?.game_uuid) {
            window.location.href = "/dashboard/game-report?game_uuid=" + status.data?.game_uuid;
        }
    }, [status.data?.status]);

    return <>
        <Container py='xl'>
            <Head>
                <title>Anova | Processing</title>
            </Head>
            <Header />

            <Stack justify='center' align='center' gap='xs' py='xl'>
                <Title order={3} pb='lg'>Processing your analysis, this may take a few minutes.</Title>
                <Loader type="dots" />
                <Stack gap='0'>
                    <Text>Step {status.data?.current_step + 1} / {status.data?.total_steps}</Text>
                    <Text>{status.data?.step_description}</Text>
                </Stack>
            </Stack>
        </Container>
    </>;
}