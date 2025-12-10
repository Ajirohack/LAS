import { useEffect } from 'react';

type KeyCombo = {
    key: string;
    meta?: boolean;
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
};

type ShortcutHandler = (e: KeyboardEvent) => void;

export function useKeyboardShortcuts(
    shortcuts: { combo: KeyCombo; handler: ShortcutHandler }[]
) {
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            shortcuts.forEach(({ combo, handler }) => {
                const keyMatch = e.key.toLowerCase() === combo.key.toLowerCase();
                const metaMatch = combo.meta ? e.metaKey : !e.metaKey;
                const ctrlMatch = combo.ctrl ? e.ctrlKey : !e.ctrlKey;
                const shiftMatch = combo.shift ? e.shiftKey : !e.shiftKey;
                const altMatch = combo.alt ? e.altKey : !e.altKey;

                if (keyMatch && metaMatch && ctrlMatch && shiftMatch && altMatch) {
                    e.preventDefault();
                    handler(e);
                }
            });
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [shortcuts]);
}
