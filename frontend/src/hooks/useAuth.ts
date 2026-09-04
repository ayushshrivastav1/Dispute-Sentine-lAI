/** Client-side session state backed by src/lib/auth-storage. */
import { useSyncExternalStore } from "react";

import { getUser, subscribe } from "@/lib/auth-storage";
import type { AuthUser } from "@/services/types";

export function useAuth(): { user: AuthUser | null; hydrated: boolean } {
  const user = useSyncExternalStore(
    subscribe,
    () => getUser(),
    () => null,
  );
  const hydrated = useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );
  return { user, hydrated };
}
