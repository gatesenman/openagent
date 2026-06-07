"use client";

import { useParams } from "next/navigation";
import { SessionDetail } from "@/components/session/SessionDetail";

export function SessionPageClient() {
  const params = useParams();
  const sessionId = params.id as string;

  return (
    <div className="h-full">
      <SessionDetail sessionId={sessionId} />
    </div>
  );
}
