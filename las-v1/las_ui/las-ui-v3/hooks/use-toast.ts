import { toast as sonnerToast, ExternalToast } from "sonner";
import { ReactNode } from "react";

type ToastVariant = "default" | "success" | "error" | "warning" | "info";

interface ToastOptions {
  title?: string;
  description?: string;
  variant?: ToastVariant;
  duration?: number;
  persistent?: boolean;
  action?: ReactNode;
}

export const useToast = () => {
  const toast = (options: ToastOptions) => {
    const { title, description, variant, duration, persistent, action } =
      options;

    const sonnerOptions: ExternalToast = {
      description,
      duration: persistent ? Infinity : duration,
    };

    // Note: Sonner 'action' prop expects { label, onClick }, but our interface has ReactNode.
    // If action is provided, we might need to handle it differently or accept that it might not render
    // exactly as the old custom toast if it was a complex component.
    // For now, we omit 'action' if it's not compatible, or we could try to adapt it if we knew the structure.
    if (action) {
      console.warn(
        "Action prop in toast is not fully supported in migration to Sonner",
        action
      );
    }

    // Since we are migrating, let's use the variant to determine the sonner method
    const message = title || description || "";
    const finalDescription = title ? description : undefined;

    // Update options with potentially shifted description
    sonnerOptions.description = finalDescription;

    switch (variant) {
      case "success":
        sonnerToast.success(message, sonnerOptions);
        break;
      case "error":
        sonnerToast.error(message, sonnerOptions);
        break;
      case "warning":
        sonnerToast.warning(message, sonnerOptions);
        break;
      case "info":
        sonnerToast.info(message, sonnerOptions);
        break;
      default:
        sonnerToast(message, sonnerOptions);
        break;
    }
  };

  const helper =
    (variant: ToastVariant) =>
    (
      title: string,
      description?: string,
      options?: Omit<ToastOptions, "title" | "description" | "variant">
    ) => {
      toast({ title, description, variant, ...options });
    };

  return {
    toast,
    success: helper("success"),
    error: helper("error"),
    warning: helper("warning"),
    info: helper("info"),
    remove: (id: string | number) => sonnerToast.dismiss(id),
    clear: () => sonnerToast.dismiss(),
  };
};
