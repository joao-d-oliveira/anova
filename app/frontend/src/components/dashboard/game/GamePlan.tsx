import { Stack, Title, Text, Table, Card, Divider, Grid, Group, Space, Paper, Box } from "@mantine/core";
import { Team, TeamStats } from "../../../generated/client";
import { ProjectedPlayer } from "../../../generated/client";
import PillStat from "./PillStat";

export default function GamePlan({ team, teamStats, playerStats }: { team: Team, teamStats: TeamStats, playerStats: ProjectedPlayer[] }) {
    return (
        <>
            <Stack>
                <Title order={2}>Game Plan</Title>
                <Text>
                    {team.record}
                </Text>
                <Card>
                    <Card.Section>
                        Playing Style
                    </Card.Section>
                    <Text>{team.playing_style}</Text>
                </Card>
                <Divider my='lg' />
                <Title order={2}>Key Players Projections</Title>
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
                                        <Stack>
                                            <PillStat label='PPG' value={player.actual_ppg.toString()} />
                                            <PillStat label='REB' value={player.actual_rpg.toString()} />
                                        </Stack>
                                    </Grid.Col>
                                    <Grid.Col span={3}>
                                        <Stack>
                                            <PillStat label='FG%' value={player.actual_fg_pct.toString()} />
                                            <PillStat label='AST' value={player.actual_apg.toString()} />
                                        </Stack>
                                    </Grid.Col>
                                    <Grid.Col span={3}>
                                        <Stack>
                                            <PillStat label='3PT%' value={player.actual_fg3_pct.toString()} />
                                            <PillStat label='STL' value={player.actual_spg.toString()} />
                                        </Stack>
                                    </Grid.Col>
                                    <Grid.Col span={3}>
                                        <Stack>
                                            <PillStat label='FT%' value={player.actual_ft_pct.toString()} />
                                            <PillStat label='BLK' value={player.actual_bpg.toString()} />
                                        </Stack>
                                    </Grid.Col>
                                </Grid>
                                <Divider my='sm' />
                                <Grid>
                                    <Grid.Col span={6}>
                                        <Stack>
                                            <Text size="sm" c="dimmed" pb='sm'>
                                                Strengths
                                            </Text>
                                        </Stack>
                                    </Grid.Col>
                                    <Grid.Col span={6}>
                                        <Stack>
                                            <Text size="sm" c="dimmed" pb='sm'>
                                                Weaknesses
                                            </Text>
                                        </Stack>
                                    </Grid.Col>
                                </Grid>
                                <Text size="sm" c="dimmed" pb='sm'>
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
                                </Table>
                            </Card>
                        </Grid.Col>
                    ))}
                </Grid>
            </Stack>
            <Space h='256px' />
        </>
    )
}