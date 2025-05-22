import { Card, Divider, Grid, Group, List, Space, Stack, Table, Text, Title } from "@mantine/core";
import { OverallReport, TeamResponse, TeamStatsResponse } from "../../../generated/client";
import KeyStats from "./KeyStats";

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
            <Space h='xs' />
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
    team: TeamResponse;
    opponent: TeamResponse;
    teamStats: TeamStatsResponse;
    opponentStats: TeamStatsResponse;
}

function ComparisonCard({ team, opponent, teamStats, opponentStats }: ComparisonCardProps) {
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
        <Card py='0'>
            <Stack mt='md'>
                <Table mb="0" withRowBorders={false} verticalSpacing={"0"}>
                    <Table.Tbody>
                        <Table.Tr>
                            <Table.Td px={0}>
                                <Text ta="left" fz="xl" fw={500}>{team.name}</Text>
                            </Table.Td>
                            <Table.Td px={0}>
                                <Text ta="center" fz="xl" fw={500}></Text>
                            </Table.Td>
                            <Table.Td px={0}>
                                <Text ta="right" fz="xl" fw={500}>{opponent.name}</Text>
                            </Table.Td>
                        </Table.Tr>
                        <Space h='xs' />
                        <Table.Tr>
                            <Table.Td w='33%' px={0}>
                                <Text ta="left" fz="sm" fw={500}>{team.record}</Text>
                            </Table.Td>
                            <Table.Td >
                                <Text ta="center" fz="sm" fw={500}>Record</Text>
                            </Table.Td>
                            <Table.Td w='33%' px={0}>
                                <Text ta="right" fz="sm" fw={500}>{opponent.record}</Text>
                            </Table.Td>
                        </Table.Tr>
                        <Table.Tr>
                            <Table.Td w='33%' px={0}>
                                <Text ta="left" fz="sm" fw={500}>{team.ranking}</Text>
                            </Table.Td>
                            <Table.Td >
                                <Text ta="center" fz="sm" fw={500}>Ranking</Text>
                            </Table.Td>
                            <Table.Td w='33%' px={0}>
                                <Text ta="right" fz="sm" fw={500}>{opponent.ranking}</Text>
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
        <>
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
                    <Card mb='md'>
                        <Card.Section>
                            Critical Advantage
                        </Card.Section>
                        <Text>{overallReport?.game_simulation.sim_critical_advantage}</Text>
                    </Card>
                    <Card>
                        <Card.Section>
                            Keys to Victory
                        </Card.Section>
                        <>
                            {overallReport?.game_simulation.sim_keys_to_victory.map((line, index) => (
                                <>
                                    {index > 0 && <Divider my='sm' />}
                                    <Text py='xs' key={index}>{line}</Text>
                                </>
                            ))}
                        </>
                    </Card>
                </Grid.Col>
                <Grid.Col span={6}>
                    <Grid mb='md'>
                        <Grid.Col span={6}>
                            <KeyStats team_name={overallReport.team.name} team_analysis={overallReport.team_analysis} />
                        </Grid.Col>
                        <Grid.Col span={6}>
                            <KeyStats team_name={overallReport.opponent.name} team_analysis={overallReport.opponent_analysis} />
                        </Grid.Col>
                    </Grid>

                    <ComparisonCard
                        team={overallReport.team}
                        opponent={overallReport.opponent}
                        teamStats={overallReport.team_stats}
                        opponentStats={overallReport.opponent_stats}
                    />
                </Grid.Col>
            </Grid>
            <Space h="256px" />
        </>
    );
}