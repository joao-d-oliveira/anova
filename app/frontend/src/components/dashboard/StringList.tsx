import { Box, BoxProps, Divider, DividerProps, Text, TextProps } from "@mantine/core";

export default function StringList({ text, textProps, boxProps, dividerProps, startIndex = 0, maxElements = 3 }: { text: string, textProps?: TextProps, boxProps?: BoxProps, dividerProps?: DividerProps, startIndex?: number, maxElements?: number }) {
    return (
        <Box py='md' {...boxProps}>
            {text.split('\n').slice(startIndex, startIndex + maxElements).map((text_part, index) => (
                <>
                    {index > 0 && <Divider my='md' {...dividerProps} />}
                    <Text {...textProps}>{text_part.replace("- ", "")}</Text>
                </>
            ))}
        </Box>
    );
}