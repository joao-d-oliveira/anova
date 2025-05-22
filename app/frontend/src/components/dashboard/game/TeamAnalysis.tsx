import { Stack, Title, Text, Table, Card, Divider, Grid, Group, Space, Paper, Box } from "@mantine/core";
import { TeamResponse, TeamStatsResponse, ProjectedPlayer, TeamAnalysisResponse } from "../../../generated/client";
import PillStat from "./PillStat";

export default function TeamAnalysis({ team, teamAnalysis, teamStats, playerStats, isScouting}: { team: TeamResponse, teamAnalysis: TeamAnalysisResponse, teamStats: TeamStatsResponse, playerStats: ProjectedPlayer[], isScouting: boolean }) {
    return (
        <>
            <Stack>
                <Title order={3}>{team.name} Report</Title>
                <Card>
                    <Card.Section>
                        {isScouting ? "Scouting Overview" : "Team Analysis"}
                    </Card.Section>
                    <Text>{teamAnalysis.playing_style}</Text>
                </Card>
                <Divider my='lg' />
                <Title order={3}>Key Players Projections</Title>
                <Grid>
                    {playerStats.map((player) => (
                        <Grid.Col key={player.id} span={6}>
                            <Card>
                                <Card.Section>
                                    <Group justify='space-between'>
                                        <Text fw={700} size='md'>{player.name}</Text>
                                        <Text size='md'>#{player.number}</Text>
                                    </Group>
                                </Card.Section>
                                <Grid>
                                    <Grid.Col span={3}>
                                        <Stack gap='4'>
                                            <PillStat label='PPG' value={player.actual_ppg.toString()} />
                                            <PillStat label='REB' value={player.actual_rpg.toString()} />
                                        </Stack>
                                    </Grid.Col>
                                    <Grid.Col span={3}>
                                        <Stack gap='4'>
                                            <PillStat label='FG%' value={player.actual_fg_pct.toString().replace('%', '')} />
                                            <PillStat label='AST' value={player.actual_apg.toString()} />
                                        </Stack>
                                    </Grid.Col>
                                    <Grid.Col span={3}>
                                        <Stack gap='4'>
                                            <PillStat label='3PT%' value={player.actual_fg3_pct.toString().replace('%', '')} />
                                            <PillStat label='STL' value={player.actual_spg.toString()} />
                                        </Stack>
                                    </Grid.Col>
                                    <Grid.Col span={3}>
                                        <Stack gap='4'>
                                            <PillStat label='FT%' value={player.actual_ft_pct.toString().replace('%', '')} />
                                            <PillStat label='BLK' value={player.actual_bpg.toString()} />
                                        </Stack>
                                    </Grid.Col>
                                </Grid>
                                <Divider my='sm' />
                                <Grid>
                                    <Grid.Col span={6}>
                                        <Stack>
                                            <Text fz='lg' fw={600} size="sm" pb='sm'>
                                                Strengths
                                            </Text>
                                        </Stack>
                                        <Stack>
                                            {player.strengths.slice(0, 3).map((strength, index) => (
                                                <>
                                                    {index > 0 && <Divider />}
                                                    <Text size='sm' key={strength}>{strength}</Text>
                                                </>
                                            ))}
                                        </Stack>
                                    </Grid.Col>
                                    <Grid.Col span={6}>
                                        <Stack>
                                            <Text fz='lg' fw={600} size="sm" pb='sm'>
                                                Weaknesses
                                            </Text>
                                        </Stack>
                                        <Stack>
                                            {player.weaknesses.slice(0, 3).map((weakness, index) => (
                                                <>
                                                    {index > 0 && <Divider />}
                                                    <Text size='sm' key={weakness}>{weakness}</Text>
                                                </>
                                            ))}
                                        </Stack>
                                    </Grid.Col>
                                </Grid>
                                <Divider my='sm' />

                                <Text fz='lg' fw={600} size="sm">
                                    Insights
                                </Text>
                                <Text size="sm" pb='sm'>
                                    {player.role}
                                </Text>
                                {/* <Text size="sm" c="dimmed" pb='sm'>
                                    {player.role}
                                </Text>
                                <Table>
                                    <Table.Thead>
                                        <Table.Tr>
                                            <Table.Th>Stat</Table.Th>
                                            <Table.Th>Projected</Table.Th>
                                            <Table.Th>Actual</Table.Th>
                                        </Table.Tr>
                                    </Table.Thead>
                                    <Table.Tbody>
                                        <Table.Tr>
                                            <Table.Td>Points</Table.Td>
                                            <Table.Td>{player.ppg}</Table.Td>
                                            <Table.Td>{player.actual_ppg ?? '-'}</Table.Td>
                                        </Table.Tr>
                                        <Table.Tr>
                                            <Table.Td>Rebounds</Table.Td>
                                            <Table.Td>{player.rpg}</Table.Td>
                                            <Table.Td>{player.actual_rpg ?? '-'}</Table.Td>
                                        </Table.Tr>
                                        <Table.Tr>
                                            <Table.Td>Assists</Table.Td>
                                            <Table.Td>{player.apg}</Table.Td>
                                            <Table.Td>{player.actual_apg ?? '-'}</Table.Td>
                                        </Table.Tr>
                                        <Table.Tr>
                                            <Table.Td>FG%</Table.Td>
                                            <Table.Td>{player.fg_pct}</Table.Td>
                                            <Table.Td>{player.actual_fg_pct ?? '-'}</Table.Td>
                                        </Table.Tr>
                                        <Table.Tr>
                                            <Table.Td>3P%</Table.Td>
                                            <Table.Td>{player.fg3_pct}</Table.Td>
                                            <Table.Td>{player.actual_fg3_pct ?? '-'}</Table.Td>
                                        </Table.Tr>
                                    </Table.Tbody>
                                </Table> */}
                            </Card>
                        </Grid.Col>
                    ))}
                </Grid>
            </Stack>
            <Space h='256px' />
        </>
    )
}