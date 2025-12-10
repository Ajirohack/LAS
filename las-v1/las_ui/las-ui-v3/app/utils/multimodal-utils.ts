export interface ContentBlock {
    type: 'text' | 'image' | 'file';
    text?: string;
    image?: string; // base64 or url
    data?: string; // base64
    mimeType?: string;
    metadata?: Record<string, unknown>;
}

/**
 * Convert a File object to a ContentBlock.Multimodal.Data object
 * compatible with the Vercel AI SDK or similar.
 */
export const fileToContentBlock = async (
    file: File
): Promise<ContentBlock> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            if (typeof reader.result === "string") {
                resolve({
                    type: file.type.startsWith("image/") ? "image" : "file",
                    mimeType: file.type,
                    data: reader.result, // Data URL
                    metadata: {
                        name: file.name,
                        size: file.size,
                    },
                });
            } else {
                reject(new Error("Failed to read file"));
            }
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
};
