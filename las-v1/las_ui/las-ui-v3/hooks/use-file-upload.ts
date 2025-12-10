import { useState, useRef, useEffect, useCallback, ChangeEvent } from "react";
import { useToast } from "@/hooks/use-toast";
import { fileToContentBlock, ContentBlock } from "@/app/utils/multimodal-utils";
import { formatFileSize } from "@/lib/utils";

export const SUPPORTED_FILE_TYPES = [
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/webp",
  "application/pdf",
  "text/plain",
  "text/markdown",
  "application/json",
  "text/csv",
];

export const SUPPORTED_FILE_EXTENSIONS = [
  ".jpg",
  ".jpeg",
  ".png",
  ".gif",
  ".webp",
  ".pdf",
  ".txt",
  ".md",
  ".json",
  ".csv",
];

interface UseFileUploadOptions {
  initialBlocks?: ContentBlock[];
  maxFileSize?: number;
  allowedFileTypes?: string[];
  maxFiles?: number;
  onFileAdd?: (file: File) => void;
  onFileRemove?: (block: ContentBlock) => void;
  onError?: (error: string) => void;
}

interface UseFileUploadReturn {
  contentBlocks: ContentBlock[];
  setContentBlocks: (blocks: ContentBlock[]) => void;
  handleFileUpload: (e: ChangeEvent<HTMLInputElement>) => Promise<void>;
  removeBlock: (idx: number) => void;
  resetBlocks: () => void;
  dropRef: React.RefObject<HTMLDivElement | null>;
  dragOver: boolean;
  handlePaste: (
    e: React.ClipboardEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => Promise<void>;
  totalSize: number;
  fileCount: number;
  isAtLimit: boolean;
}

export const useFileUpload = (
  options: UseFileUploadOptions = {}
): UseFileUploadReturn => {
  const {
    initialBlocks = [],
    maxFileSize = 10 * 1024 * 1024, // 10MB
    allowedFileTypes = SUPPORTED_FILE_TYPES,
    maxFiles = 10,
    onFileAdd,
    onFileRemove,
    onError,
  } = options;

  const [contentBlocks, setContentBlocks] =
    useState<ContentBlock[]>(initialBlocks);
  const dropRef = useRef<HTMLDivElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const dragCounter = useRef(0);
  const { success, error: showError } = useToast();

  // Calculate total size and file count
  const totalSize = contentBlocks.reduce(
    (acc, block) => acc + (Number(block.metadata?.size) || 0),
    0
  );
  const fileCount = contentBlocks.length;
  const isAtLimit = fileCount >= maxFiles;

  const isDuplicate = (file: File, blocks: ContentBlock[]) => {
    return blocks.some((block) => {
      if (block.type === "file" || block.type === "image") {
        const nameMatch = block.metadata?.name === file.name;
        const typeMatch = block.mimeType === file.type;
        const sizeMatch = block.metadata?.size === file.size;
        return nameMatch && typeMatch && sizeMatch;
      }
      return false;
    });
  };

  const validateFile = useCallback(
    (file: File): { valid: boolean; error?: string } => {
      // Check file size
      if (file.size > maxFileSize) {
        return {
          valid: false,
          error: `File "${
            file.name
          }" is too large. Maximum size is ${formatFileSize(maxFileSize)}.`,
        };
      }

      // Check file type
      const isAllowedType =
        allowedFileTypes.includes(file.type) ||
        allowedFileTypes.some((type) =>
          file.name.toLowerCase().endsWith(type.toLowerCase())
        );

      if (!isAllowedType) {
        return {
          valid: false,
          error: `File type "${
            file.type || file.name.split(".").pop()
          }" is not supported.`,
        };
      }

      // Check duplicate
      if (isDuplicate(file, contentBlocks)) {
        return {
          valid: false,
          error: `File "${file.name}" is already attached.`,
        };
      }

      return { valid: true };
    },
    [contentBlocks, maxFileSize, allowedFileTypes]
  );

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const fileArray = Array.from(files);

    // Check if we're at the file limit
    if (fileCount + fileArray.length > maxFiles) {
      const errorMsg = `Maximum ${maxFiles} files allowed. You can add ${
        maxFiles - fileCount
      } more files.`;
      showError(errorMsg);
      onError?.(errorMsg);
      e.target.value = "";
      return;
    }

    const validFiles: File[] = [];
    const errors: string[] = [];

    // Validate each file
    for (const file of fileArray) {
      const validation = validateFile(file);
      if (validation.valid) {
        validFiles.push(file);
      } else if (validation.error) {
        errors.push(validation.error);
      }
    }

    // Show errors if any
    if (errors.length > 0) {
      errors.forEach((errorMsg) => {
        showError(errorMsg);
        onError?.(errorMsg);
      });
    }

    // Process valid files
    if (validFiles.length > 0) {
      try {
        const newBlocks = await Promise.all(
          validFiles.map(async (file) => {
            const block = await fileToContentBlock(file);
            onFileAdd?.(file);
            return block;
          })
        );
        setContentBlocks((prev) => [...prev, ...newBlocks]);

        const successMessage = `Added ${validFiles.length} file${
          validFiles.length > 1 ? "s" : ""
        }`;
        success(successMessage);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to process files";
        showError(errorMessage);
        onError?.(errorMessage);
      }
    }

    e.target.value = "";
  };

  // Drag and drop handlers
  useEffect(() => {
    if (!dropRef.current) return;

    const handleWindowDragEnter = (e: DragEvent) => {
      if (e.dataTransfer?.types?.includes("Files")) {
        dragCounter.current += 1;
        setDragOver(true);
      }
    };

    const handleWindowDragLeave = (e: DragEvent) => {
      if (e.dataTransfer?.types?.includes("Files")) {
        dragCounter.current -= 1;
        if (dragCounter.current <= 0) {
          setDragOver(false);
          dragCounter.current = 0;
        }
      }
    };

    const handleWindowDrop = async (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter.current = 0;
      setDragOver(false);

      if (!e.dataTransfer) return;

      const files = Array.from(e.dataTransfer.files);

      // Check if we're at the file limit
      if (fileCount + files.length > maxFiles) {
        const errorMsg = `Maximum ${maxFiles} files allowed. You can add ${
          maxFiles - fileCount
        } more files.`;
        showError(errorMsg);
        onError?.(errorMsg);
        return;
      }

      const validFiles: File[] = [];
      const errors: string[] = [];

      // Validate each file
      for (const file of files) {
        const validation = validateFile(file);
        if (validation.valid) {
          validFiles.push(file);
        } else if (validation.error) {
          errors.push(validation.error);
        }
      }

      // Show errors if any
      if (errors.length > 0) {
        errors.forEach((errorMsg) => {
          showError(errorMsg);
          onError?.(errorMsg);
        });
      }

      // Process valid files
      if (validFiles.length > 0) {
        try {
          const newBlocks = await Promise.all(
            validFiles.map(async (file) => {
              const block = await fileToContentBlock(file);
              onFileAdd?.(file);
              return block;
            })
          );
          setContentBlocks((prev) => [...prev, ...newBlocks]);

          const successMessage = `Added ${validFiles.length} file${
            validFiles.length > 1 ? "s" : ""
          }`;
          success(successMessage);
        } catch (err) {
          const errorMessage =
            err instanceof Error ? err.message : "Failed to process files";
          showError(errorMessage);
          onError?.(errorMessage);
        }
      }
    };

    const handleWindowDragEnd = () => {
      dragCounter.current = 0;
      setDragOver(false);
    };

    const handleWindowDragOver = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
    };

    window.addEventListener("dragenter", handleWindowDragEnter);
    window.addEventListener("dragleave", handleWindowDragLeave);
    window.addEventListener("drop", handleWindowDrop);
    window.addEventListener("dragend", handleWindowDragEnd);
    window.addEventListener("dragover", handleWindowDragOver);

    return () => {
      window.removeEventListener("dragenter", handleWindowDragEnter);
      window.removeEventListener("dragleave", handleWindowDragLeave);
      window.removeEventListener("drop", handleWindowDrop);
      window.removeEventListener("dragend", handleWindowDragEnd);
      window.removeEventListener("dragover", handleWindowDragOver);
      dragCounter.current = 0;
    };
  }, [
    contentBlocks,
    maxFiles,
    fileCount,
    allowedFileTypes,
    maxFileSize,
    onFileAdd,
    onError,
    success,
    showError,
    validateFile,
  ]);

  const removeBlock = (idx: number) => {
    const block = contentBlocks[idx];
    setContentBlocks((prev) => prev.filter((_, i) => i !== idx));
    if (block) {
      onFileRemove?.(block);
    }
  };

  const resetBlocks = () => {
    contentBlocks.forEach((block) => onFileRemove?.(block));
    setContentBlocks([]);
  };

  const handlePaste = async (
    e: React.ClipboardEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => {
    const items = e.clipboardData.items;
    if (!items) return;

    const files: File[] = [];
    for (let i = 0; i < items.length; i += 1) {
      const item = items[i];
      if (item.kind === "file") {
        const file = item.getAsFile();
        if (file) files.push(file);
      }
    }

    if (files.length === 0) return;

    // Check if we're at the file limit
    if (fileCount + files.length > maxFiles) {
      const errorMsg = `Maximum ${maxFiles} files allowed. You can add ${
        maxFiles - fileCount
      } more files.`;
      showError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    const validFiles: File[] = [];
    const errors: string[] = [];

    // Validate each file
    for (const file of files) {
      const validation = validateFile(file);
      if (validation.valid) {
        validFiles.push(file);
      } else if (validation.error) {
        errors.push(validation.error);
      }
    }

    // Show errors if any
    if (errors.length > 0) {
      errors.forEach((errorMsg) => {
        showError(errorMsg);
        onError?.(errorMsg);
      });
    }

    // Process valid files
    if (validFiles.length > 0) {
      try {
        e.preventDefault();
        const newBlocks = await Promise.all(
          validFiles.map(async (file) => {
            const block = await fileToContentBlock(file);
            onFileAdd?.(file);
            return block;
          })
        );
        setContentBlocks((prev) => [...prev, ...newBlocks]);

        const successMessage = `Added ${validFiles.length} file${
          validFiles.length > 1 ? "s" : ""
        }`;
        success(successMessage);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to process files";
        showError(errorMessage);
        onError?.(errorMessage);
      }
    }
  };

  return {
    contentBlocks,
    setContentBlocks,
    handleFileUpload,
    dropRef,
    removeBlock,
    resetBlocks,
    dragOver,
    handlePaste,
    totalSize,
    fileCount,
    isAtLimit,
  };
};
