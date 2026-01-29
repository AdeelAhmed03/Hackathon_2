import { auth } from "@/lib/auth"; // import the auth client
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth.api);
