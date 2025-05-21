import { Stack, Title, Text, Table, Card, Divider, Grid, Group, Space } from "@mantine/core";
import { Team, TeamStats } from "../../../generated/client";
import { ProjectedPlayer } from "../../../generated/client";

export default function TeamAnalysis({ team, teamStats, playerStats }: { team: Team, teamStats: TeamStats, playerStats: ProjectedPlayer[] }) {
    return (
        <>
            <Stack>
                <Title order={2}>{team.name} Report</Title>
                <Text>
                    {team.record}
                </Text>
                <Card>
                    <Card.Section>
                        Playing Style
                    </Card.Section>
                    <Text>{team.playing_style}</Text>
                </Card>
                <Divider my='lg'/>
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