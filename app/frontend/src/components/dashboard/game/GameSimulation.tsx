import { Stack, Title, Text, Card, Divider, Grid, Group, Space, Table } from "@mantine/core";
import { TeamAnalysisResponse, GameSimulationResponse, TeamResponse, PlayerProjectionResponse } from "../../../generated/client";
import StringList from "../StringList";
import PlayDetails from "./PlayDetails";
import SituationalDetails from "./SituationalDetails";

export default function GameSimulation({ gameSimulation, team, opponent, teamAnalysis, opponentAnalysis, teamPlayerAnalysis, opponentPlayerAnalysis }: {
    gameSimulation: GameSimulationResponse,
    team: TeamResponse,
    opponent: TeamResponse,
    teamAnalysis: TeamAnalysisResponse,
    opponentAnalysis: TeamAnalysisResponse,
    teamPlayerAnalysis: PlayerProjectionResponse[],
    opponentPlayerAnalysis: PlayerProjectionResponse[]
}) {
    return (
        <>
            <Stack>
                <Title order={3}>Game Simulation</Title>

                {/* Simulated Outcome */}
                <Card>
                    <Card.Section>
                        Simulated Outcome
                    </Card.Section>
                    <Stack mt="xs" gap={0}>
                        <Text size="lg">{gameSimulation.win_probability}</Text>
                    </Stack>
                </Card>

                <Divider my="md" />

                {/* Success Factors */}
                <Card>
                    <Card.Section mb='0'>
                        Success Factors
                    </Card.Section>
                    <Grid mt="md">
                        <Grid.Col span={6}>
                            <StringList text={gameSimulation.sim_success_factors} startIndex={0} maxElements={2} />
                        </Grid.Col>
                        <Grid.Col span={6}>
                            <StringList text={gameSimulation.sim_success_factors} startIndex={2} maxElements={2} />
                        </Grid.Col>
                    </Grid>
                </Card>

                <Divider my="md" />

                {/* Keys to Victory */}
                <Grid>
                    <Grid.Col span={6}>
                        <Card h='100%'>
                            <Card.Section>
                                Offensive Keys to Victory
                            </Card.Section>
                            <StringList maxElements={5} text={teamAnalysis.offensive_keys.join('\\n')} />
                        </Card>
                    </Grid.Col>
                    <Grid.Col span={6}>
                        <Card h='100%'>
                            <Card.Section>
                                Defensive Keys to Victory
                            </Card.Section>
                            <StringList maxElements={5} text={opponentAnalysis.defensive_keys.join('\\n')} />
                        </Card>
                    </Grid.Col>
                </Grid>

                <Divider my="md" />

                {/* Player Projections */}
                <Card>
                    <Card.Section>
                        Player Projections
                    </Card.Section>
                    <Title order={4} mt="sm" mb="md">{team.name}</Title>
                    <Table striped>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Player</Table.Th>
                                <Table.Th>PPG</Table.Th>
                                <Table.Th>RPG</Table.Th>
                                <Table.Th>APG</Table.Th>
                                <Table.Th>FG%</Table.Th>
                                <Table.Th>3PT%</Table.Th>
                                <Table.Th>Role</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {teamPlayerAnalysis.map((player) => (
                                <Table.Tr key={`team-${player.name}`}>
                                    <Table.Td>{player.name}</Table.Td>
                                    <Table.Td>{player.ppg}</Table.Td>
                                    <Table.Td>{player.rpg}</Table.Td>
                                    <Table.Td>{player.apg}</Table.Td>
                                    <Table.Td>{player.fg_pct}</Table.Td>
                                    <Table.Td>{player.fg3_pct}</Table.Td>
                                    <Table.Td>{player.role}</Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>

                    <Title order={4} mt="xl" mb="md">{opponent.name}</Title>

                    <Table striped>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Player</Table.Th>
                                <Table.Th>PPG</Table.Th>
                                <Table.Th>RPG</Table.Th>
                                <Table.Th>APG</Table.Th>
                                <Table.Th>FG%</Table.Th>
                                <Table.Th>3PT%</Table.Th>
                                <Table.Th>Role</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {opponentPlayerAnalysis.map((player) => (
                                <Table.Tr key={`opponent-${player.name}`}>
                                    <Table.Td>{player.name}</Table.Td>
                                    <Table.Td>{player.ppg}</Table.Td>
                                    <Table.Td>{player.rpg}</Table.Td>
                                    <Table.Td>{player.apg}</Table.Td>
                                    <Table.Td>{player.fg_pct}</Table.Td>
                                    <Table.Td>{player.fg3_pct}</Table.Td>
                                    <Table.Td>{player.role}</Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>
                </Card>

                <Divider my="md" />

                {/* Situational Adjustments */}
                <Title order={3}>Situational Adjustments</Title>
                <Stack>
                    {gameSimulation.sim_situational_adjustments.map((adjustment, index) => (
                        <Card key={`adjustment-${index}`}>
                            <SituationalDetails
                                purpose={adjustment.adjustment}
                                execution={adjustment.outcome}
                                adjustment={adjustment.adjustment}
                            />
                        </Card>
                    ))}
                </Stack>
            </Stack>
            <Space h="256px" />
        </>
    );
}