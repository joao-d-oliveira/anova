import { Card, Grid, Group, List, Stack, Table, Text, Title } from "@mantine/core";
import { OverallReport, TeamStats } from "../../../generated/client";

interface StatisticRowProps {
    name: string;
    teamValue: number | string | null;
    opponentValue: number | string | null;
}

function StatisticRow({ name, teamValue, opponentValue }: StatisticRowProps) {
    return (
        <Table.Tr>
            <Table.Td>{teamValue}</Table.Td>
            <Table.Td ta="center">{name}</Table.Td>
            <Table.Td ta="right">{opponentValue}</Table.Td>
        </Table.Tr>
    );
}

interface StatisticTableProps {
    title: string;
    statistics: Array<{
        name: string;
        teamValue: number | string | null;
        opponentValue: number | string | null;
    }>;
}

function StatisticTable({ title, statistics }: StatisticTableProps) {
    return (
        <Table mb="md" withRowBorders={false} verticalSpacing={"2"}>
            <Table.Thead>
                <Table.Tr bg="gray.1">
                    <Table.Th colSpan={3}>
                        <Text ta="center" fw={500}>{title}</Text>
                    </Table.Th>
                </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
                {statistics.map((stat) => (
                    <StatisticRow
                        key={stat.name}
                        name={stat.name}
                        teamValue={stat.teamValue}
                        opponentValue={stat.opponentValue}
                    />
                ))}
            </Table.Tbody>
        </Table>
    );
}

interface ComparisonCardProps {
    teamName: string;
    opponentName: string;
    teamStats: TeamStats;
    opponentStats: TeamStats;
}

function ComparisonCard({ teamName, opponentName, teamStats, opponentStats }: ComparisonCardProps) {
    const offenseStats = [
        { name: "Points Per Game", teamValue: teamStats.ppg, opponentValue: opponentStats.ppg },
        { name: "Field Goal %", teamValue: teamStats.fg_pct, opponentValue: opponentStats.fg_pct },
        { name: "3-Point %", teamValue: teamStats.fg3_pct, opponentValue: opponentStats.fg3_pct },
        { name: "Free Throw %", teamValue: teamStats.ft_pct, opponentValue: opponentStats.ft_pct },
    ];

    const defenseStats = [
        { name: "Steals", teamValue: teamStats.steals, opponentValue: opponentStats.steals },
        { name: "Blocks", teamValue: teamStats.blocks, opponentValue: opponentStats.blocks },
    ];

    const reboundingStats = [
        { name: "Total Rebounds", teamValue: teamStats.rebounds, opponentValue: opponentStats.rebounds },
        { name: "Offensive Rebounds", teamValue: teamStats.offensive_rebounds, opponentValue: opponentStats.offensive_rebounds },
        { name: "Defensive Rebounds", teamValue: teamStats.defensive_rebounds, opponentValue: opponentStats.defensive_rebounds },
    ];

    const playmakingStats = [
        { name: "Assists", teamValue: teamStats.assists, opponentValue: opponentStats.assists },
        { name: "Turnovers", teamValue: teamStats.turnovers, opponentValue: opponentStats.turnovers },
        { name: "Assist/Turnover Ratio", teamValue: teamStats.assist_to_turnover, opponentValue: opponentStats.assist_to_turnover },
    ];

    return (
        <Card>
            <Card.Section>
                Team Comparison
            </Card.Section>
            <Stack mt='md'>
                <Table mb="0" withRowBorders={false} verticalSpacing={"0"}>
                    <Table.Tbody>
                        <Table.Tr>
                            <Table.Td>
                                <Text ta="left" fz="xl" fw={500}>{teamName}</Text>
                            </Table.Td>
                            <Table.Td>
                                <Text ta="right" fz="xl" fw={500}>{opponentName}</Text>
                            </Table.Td>
                        </Table.Tr>
                    </Table.Tbody>
                </Table>
                <StatisticTable title="Offense" statistics={offenseStats} />
                <StatisticTable title="Defense" statistics={defenseStats} />
                <StatisticTable title="Rebounding" statistics={reboundingStats} />
                <StatisticTable title="Playmaking" statistics={playmakingStats} />
            </Stack>
        </Card>
    );
}

export default function Overview({ overallReport }: { overallReport: OverallReport }) {
    return (
        <Grid>
            <Grid.Col span={6}>
                <Grid mb='md'>
                    <Grid.Col span={6}>
                        <Card h="100%">
                            <Card.Section>
                                Win Probability
                            </Card.Section>
                            <Text>{overallReport?.game_simulation.win_probability}</Text>
                        </Card>
                    </Grid.Col>
                    <Grid.Col span={6}>
                        <Card h="100%">
                            <Card.Section>
                                Projected Score
                            </Card.Section>
                            <Text>{overallReport?.game_simulation.projected_score}</Text>
                        </Card>
                    </Grid.Col>
                </Grid>
                <Card>
                <Card.Section>
                        Critical Advantage
                    </Card.Section>
                    <List>
                        {overallReport?.game_simulation.sim_success_factors.split('\n').map((line, index) => (
                            <List.Item py='xs' key={index}>{line.replace('- ', '')}</List.Item>
                        ))}
                    </List>
                </Card>
                <Card>
                    <Card.Section>
                        Simulated Outcome
                    </Card.Section>
                    <List>
                        {overallReport?.game_simulation.sim_success_factors.split('\n').map((line, index) => (
                            <List.Item py='xs' key={index}>{line.replace('- ', '')}</List.Item>
                        ))}
                    </List>
                </Card>
            </Grid.Col>
            <Grid.Col span={6}>
                <ComparisonCard
                    teamName={overallReport.team.name}
                    opponentName={overallReport.opponent.name}
                    teamStats={overallReport.team_stats}
                    opponentStats={overallReport.opponent_stats}
                />
            </Grid.Col>
        </Grid>
    );
}