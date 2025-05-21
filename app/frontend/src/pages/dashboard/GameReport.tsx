import { Button, Container, Group, Stack, Title, Text, Space, Tabs, Loader } from "@mantine/core";
import Header from "../../components/dashboard/Header";
import { useReport } from "../../mutations";
import Overview from "../../components/dashboard/game/Overview";
import TeamAnalysis from "../../components/dashboard/game/TeamAnalysis";
import { filledButtonProps } from "../../props/Button";

export default function GameReport() {
    const { searchParams } = new URL(window.location.href);
    const game_uuid = searchParams.get('game_uuid');
    const { overallReport, downloadReport } = useReport({ game_uuid: game_uuid as string });


    if (overallReport.isLoading) {
        return <Container size='xl'>
            <Header />
            <Loader type="dots" />
        </Container>;
    }

    if (overallReport.isError) {
        return <Container size='xl'>
            <Header />
            <Text>Error: {overallReport.error.message}</Text>
        </Container>;
    }

    return <Container size='xl'>
        <Header />
        <Group justify='space-between'>
            <Stack>
                <Title order={1}>{overallReport.data.team.name} vs {overallReport.data.opponent.name} Game Report</Title>
                <Text>Created: {new Date(overallReport.data?.created_at).toLocaleString()}</Text>
            </Stack>
            <Group>
                <Button onClick={() => downloadReport.mutate()} {...filledButtonProps}>Download</Button>
            </Group>
        </Group>
        <Space h='xl' />
        <Tabs color="brand" defaultValue="overview">
            <Tabs.List>
                <Tabs.Tab value="overview">
                    Overview
                </Tabs.Tab>
                <Tabs.Tab value="scouting">
                    Scouting Report
                </Tabs.Tab>
                <Tabs.Tab value="team">
                    Team Analysis
                </Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="overview">
                <Space h='xl' />
                <Overview overallReport={overallReport.data} />
            </Tabs.Panel>

            <Tabs.Panel value="scouting">
                <Space h='xl' />
                <TeamAnalysis team={overallReport.data.team} teamStats={overallReport.data.team_stats} playerStats={overallReport.data.team_player_analysis} />
            </Tabs.Panel>

            <Tabs.Panel value="team">
                <Space h='xl' />
                <TeamAnalysis team={overallReport.data.opponent} teamStats={overallReport.data.opponent_stats} playerStats={overallReport.data.opponent_player_analysis} />
            </Tabs.Panel>
        </Tabs>
    </Container>;
}