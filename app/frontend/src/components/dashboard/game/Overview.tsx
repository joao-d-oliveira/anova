import { Card, Grid, Group, List, Table, Text, Title } from "@mantine/core";
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
        <Table mb="md">
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
    teamStats: TeamStats;
    opponentStats: TeamStats;
}

function ComparisonCard({ teamStats, opponentStats }: ComparisonCardProps) {
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
            <Card.Section p='md'>
                <Title order={3}>Team Comparison</Title>
            </Card.Section>
            <StatisticTable title="Offense" statistics={offenseStats} />
            <StatisticTable title="Defense" statistics={defenseStats} />
            <StatisticTable title="Rebounding" statistics={reboundingStats} />
            <StatisticTable title="Playmaking" statistics={playmakingStats} />
        </Card>
    );
}

export default function Overview({ overallReport }: { overallReport: OverallReport }) {
    return (
        <Grid>
            <Grid.Col span={6}>
                <Grid mb='md'>
                    <Grid.Col span={6}>
                        <Card>
                            <Card.Section p='md'>
                                <Title order={3}>Win Probability</Title>
                            </Card.Section>
                            <Text>{overallReport?.game_simulation.win_probability}</Text>
                        </Card>
                    </Grid.Col>
                    <Grid.Col span={6}>
                        <Card>
                            <Card.Section p='md'>
                                <Title order={3}>Projected Score</Title>
                            </Card.Section>
                            <Text>{overallReport?.game_simulation.projected_score}</Text>
                        </Card>
                    </Grid.Col>
                </Grid>
                <Card>
                    <Card.Section p='md'>
                        <Title order={3}>Simulated Outcome</Title>
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
                    teamStats={overallReport.team_stats}
                    opponentStats={overallReport.opponent_stats}
                />

            </Grid.Col>
        </Grid>
    );
}