import { useState, useCallback, useMemo } from 'react';

export interface SlashCommand {
    command: string;
    description: string;
    category: 'general' | 'coding' | 'writing' | 'analysis' | 'creative';
    handler: (args: string) => string;
    examples?: string[];
}

interface UseSlashCommandsReturn {
    commands: SlashCommand[];
    filteredCommands: SlashCommand[];
    selectedIndex: number;
    handleSlashInput: (input: string) => void;
    insertCommand: (command: SlashCommand) => void;
    closeCommands: () => void;
}

export function useSlashCommands(): UseSlashCommandsReturn {
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);

    // Define available slash commands
    const commands: SlashCommand[] = useMemo(() => [
        // General commands
        {
            command: 'help',
            description: 'Show available commands and features',
            category: 'general',
            handler: () => 'Help: Available commands include /code, /write, /analyze, /summarize, and more. Type / to see all commands.',
            examples: ['/help']
        },
        {
            command: 'clear',
            description: 'Clear the current conversation',
            category: 'general',
            handler: () => 'Please clear the conversation history.',
            examples: ['/clear']
        },
        {
            command: 'reset',
            description: 'Reset the current session',
            category: 'general',
            handler: () => 'Please reset this session and start fresh.',
            examples: ['/reset']
        },

        // Coding commands
        {
            command: 'code',
            description: 'Generate or explain code',
            category: 'coding',
            handler: (args) => `Please generate code for: ${args}`,
            examples: ['/code create a React component', '/code explain this function']
        },
        {
            command: 'debug',
            description: 'Debug code or error messages',
            category: 'coding',
            handler: (args) => `Please debug this code: ${args}`,
            examples: ['/debug this error message', '/debug my function']
        },
        {
            command: 'refactor',
            description: 'Refactor and improve code',
            category: 'coding',
            handler: (args) => `Please refactor this code to make it cleaner and more efficient: ${args}`,
            examples: ['/refactor this function', '/refactor improve performance']
        },
        {
            command: 'test',
            description: 'Generate unit tests for code',
            category: 'coding',
            handler: (args) => `Please write unit tests for: ${args}`,
            examples: ['/test this function', '/test create comprehensive tests']
        },

        // Writing commands
        {
            command: 'write',
            description: 'Write content or documents',
            category: 'writing',
            handler: (args) => `Please write: ${args}`,
            examples: ['/write a blog post about AI', '/write a professional email']
        },
        {
            command: 'summarize',
            description: 'Summarize text or content',
            category: 'writing',
            handler: (args) => `Please summarize: ${args}`,
            examples: ['/summarize this article', '/summarize in 3 bullet points']
        },
        {
            command: 'translate',
            description: 'Translate text to another language',
            category: 'writing',
            handler: (args) => `Please translate: ${args}`,
            examples: ['/translate to Spanish', '/translate this to French']
        },
        {
            command: 'improve',
            description: 'Improve and enhance writing',
            category: 'writing',
            handler: (args) => `Please improve this writing: ${args}`,
            examples: ['/improve this sentence', '/improve make it more professional']
        },

        // Analysis commands
        {
            command: 'analyze',
            description: 'Analyze data, text, or code',
            category: 'analysis',
            handler: (args) => `Please analyze: ${args}`,
            examples: ['/analyze this data', '/analyze the pros and cons']
        },
        {
            command: 'compare',
            description: 'Compare different options or solutions',
            category: 'analysis',
            handler: (args) => `Please compare: ${args}`,
            examples: ['/compare React vs Vue', '/compare these approaches']
        },
        {
            command: 'explain',
            description: 'Explain concepts or code',
            category: 'analysis',
            handler: (args) => `Please explain: ${args}`,
            examples: ['/explain quantum computing', '/explain this algorithm']
        },

        // Creative commands
        {
            command: 'brainstorm',
            description: 'Generate creative ideas',
            category: 'creative',
            handler: (args) => `Please brainstorm ideas for: ${args}`,
            examples: ['/brainstorm business ideas', '/brainstorm marketing strategies']
        },
        {
            command: 'create',
            description: 'Create something new',
            category: 'creative',
            handler: (args) => `Please create: ${args}`,
            examples: ['/create a story', '/create a marketing plan']
        },
        {
            command: 'design',
            description: 'Design or plan something',
            category: 'creative',
            handler: (args) => `Please design: ${args}`,
            examples: ['/design a user interface', '/design a system architecture']
        }
    ], []);

    // Filter commands based on query
    const filteredCommands = useMemo(() => {
        if (!query) return commands;
        
        const searchTerm = query.toLowerCase();
        return commands.filter(cmd => 
            cmd.command.toLowerCase().includes(searchTerm) ||
            cmd.description.toLowerCase().includes(searchTerm) ||
            cmd.category.toLowerCase().includes(searchTerm)
        );
    }, [commands, query]);

    const handleSlashInput = useCallback((input: string) => {
        if (input === '/') {
            setQuery('');
            setSelectedIndex(0);
        } else if (input === 'ArrowDown') {
            setSelectedIndex(prev => 
                prev < filteredCommands.length - 1 ? prev + 1 : prev
            );
        } else if (input === 'ArrowUp') {
            setSelectedIndex(prev => prev > 0 ? prev - 1 : 0);
        } else {
            setQuery(input);
            setSelectedIndex(0);
        }
    }, [filteredCommands.length]);

    const insertCommand = useCallback((command: SlashCommand) => {
        // This would be called to insert the command into the input
        // The actual implementation would depend on how it's integrated with the input component
        console.log('Inserting command:', command.command);
    }, []);

    const closeCommands = useCallback(() => {
        setQuery('');
        setSelectedIndex(0);
    }, []);

    return {
        commands,
        filteredCommands,
        selectedIndex,
        handleSlashInput,
        insertCommand,
        closeCommands,
    };
}