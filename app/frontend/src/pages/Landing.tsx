import "../css/Landing.css";
import { Box, Button, Container, Grid, Group, Image, Paper, Stack, Text, Title } from "@mantine/core";

export default function Landing() {
    return (
        <Box bg='black' mih='100vh' m={0} p={0}>
            <Container size='xl' py='48'>
                <Group justify='space-between' mb='100'>
                    <Image maw={100} src="/imgs/anova_logo_white.png" alt="Anova Logo" pb='xl' />
                    <Text ff='Inter' c='dimmed' size='xl' fw={400}>
                        SEE THE GAME DIFFERENTLY
                    </Text>
                </Group>
                <Title ff='Inter' ta='center' lh={0.9} order={1} fz={70} fw={900} style={{ background: 'linear-gradient(to right, #C5FF0A, #01FB65)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    BASKETBALL<br />COACHING HAS CHANGED
                </Title>
                <Text c='white' size='22px' fw={400} ta='center' pt='16'>
                    Anova analyzes team and opponent performance to deliver complete coaching reports with <br /> matchup insights, play suggestions, and projected outcomes. All in minutes, not hours.
                </Text>
                <Grid>
                    <Grid.Col span={4}>
                        <Paper bg='rgba(255, 255, 255, 0.1)' p='24'>
                            <Stack ta={'center'}>
                                <Text ff='Inter' c='white' size='24px' lh={1.1} fw={700}>PERFORMANCE IN, NOTEBOOKS OUT.</Text>
                                <Text ff='Inter' c='white' size='16px' fw={500}>
                                    Forget wasted time on data prep. Anova uses your team's stats to generate complete coaching reports in minutes.
                                </Text>
                                <Text ff='Inter' c='white' size='16px' fw={300}>
                                    Anova processes your team and opponent performance data to start building real insight, automatically.
                                </Text>
                            </Stack>
                        </Paper>
                    </Grid.Col>
                    <Grid.Col span={4}>
                        <Paper bg='rgba(255, 255, 255, 0.1)' p='24'>
                            <Stack ta={'center'}>
                                <Text ff='Inter' c='white' size='24px' lh={1.1} fw={700}>PERFORMANCE IN, NOTEBOOKS OUT.</Text>
                                <Text ff='Inter' c='white' size='16px' fw={500}>
                                    Forget wasted time on data prep. Anova uses your team's stats to generate complete coaching reports in minutes.
                                </Text>
                                <Text ff='Inter' c='white' size='16px' fw={300}>
                                    Anova processes your team and opponent performance data to start building real insight, automatically.
                                </Text>
                            </Stack>
                        </Paper>
                    </Grid.Col>
                    <Grid.Col span={4}>
                        <Paper bg='rgba(255, 255, 255, 0.1)' p='24'>
                            <Stack ta={'center'}>
                                <Text ff='Inter' c='white' size='24px' lh={1.1} fw={700}>PERFORMANCE IN, NOTEBOOKS OUT.</Text>
                                <Text ff='Inter' c='white' size='16px' fw={500}>
                                    Forget wasted time on data prep. Anova uses your team's stats to generate complete coaching reports in minutes.
                                </Text>
                                <Text ff='Inter' c='white' size='16px' fw={300}>
                                    Anova processes your team and opponent performance data to start building real insight, automatically.
                                </Text>
                            </Stack>
                        </Paper>
                    </Grid.Col>
                </Grid>
                <Group justify="center">
                    <Button variant='outline' size='lg' fullWidth component="a" href="/auth/login">Launch Anova</Button>
                </Group>
            </Container>
        </Box>
    )
}