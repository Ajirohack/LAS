import { AppShell } from "@/components/layout/AppShell";
import { ChatInterface } from "@/components/chat/ChatInterface";

export default function Home() {
  return (
    <AppShell>
      <ChatInterface />
    </AppShell>
  );
}

