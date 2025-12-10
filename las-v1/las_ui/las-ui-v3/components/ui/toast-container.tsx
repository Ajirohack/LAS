import React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Toast } from "./toast";
import { useStore } from "@/lib/store";

export interface ToastItem {
  id: string;
  title?: string;
  description?: string;
  variant?: "default" | "success" | "error" | "warning" | "info";
  duration?: number;
  persistent?: boolean;
  action?: React.ReactNode;
}

const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useStore();

  return (
    <div className="fixed top-4 right-4 z-[100] space-y-2">
      <AnimatePresence mode="sync">
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: 100, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.9 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 30,
            }}
            layout>
            <Toast
              id={toast.id}
              title={toast.title}
              description={toast.description}
              variant={toast.variant}
              duration={toast.duration}
              persistent={toast.persistent}
              action={toast.action}
              onDismiss={() => removeToast(toast.id)}
              className="min-w-[300px] max-w-[400px] shadow-lg backdrop-blur-sm bg-background/80"
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export { ToastContainer };
