import "../css/Landing.css";
import { Box, Button, Center, Container, Grid, Group, Image, Paper, Stack, Text, Title } from "@mantine/core";

function FeatureCard({ title, description, text }: { title: string, description: string, text: string }) {
    return (
        <Paper bg='rgba(255, 255, 255, 0.1)' p='24'>
            <Stack ta={'center'}>
                <Text mx='auto' ff='Inter' c='white' size='24px' lh={1.1} fw={700} style={{textTransform: 'uppercase'}} dangerouslySetInnerHTML={{ __html: title }} />
                <Text ff='Inter' c='white' size='16px' fw={500}>
                    {description}
                </Text>
                <Text ff='Inter' c='white' size='16px' fw={300}>
                    {text}
                </Text>
            </Stack>
        </Paper>
    )
}
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
                <Text c='white' size='22px' fw={400} ta='center' py='16'>
                    Anova analyzes team and opponent performance to deliver complete coaching reports with <br /> matchup insights, play suggestions, and projected outcomes. All in minutes, not hours.
                </Text>
                <Grid mt='24'>
                    <Grid.Col span={4}>
                        <FeatureCard
                            title="PERFORMANCE IN, NOTEBOOKS OUT."
                            description="Forget wasted time on data prep."
                            text="Anova processes your team and opponent performance data to start building real insight, automatically."
                        />
                    </Grid.Col>
                    <Grid.Col span={4}>
                        <FeatureCard
                            title="Tactical Clarity, <br /> Not Raw Data."
                            description="Know what matters, instantly."
                            text="Anova processes your team and opponent performance data to start building real insight, automatically."
                        />
                    </Grid.Col>
                    <Grid.Col span={4}>
                        <FeatureCard
                            title="Game-Ready Reports. <br /> In Minutes."
                            description="Strategy you can act on."
                            text="Receive structured scouting reports, tailored game plans, and play suggestions built around how your team actually plays."
                        />
                    </Grid.Col>
                </Grid>
                <Center mt='xl'>
                    <Button 
                        maw={400} 
                        variant='filled' 
                        size='md' 
                        fullWidth 
                        component="a" 
                        href="/auth/login"
                        style={{ 
                            background: 'linear-gradient(to right, #C5FF0A, #01FB65)',
                            color: 'black',
                            border: 'none'
                        }}>
                        Launch Anova
                    </Button>
                </Center>
            </Container>
        </Box>
    )
}