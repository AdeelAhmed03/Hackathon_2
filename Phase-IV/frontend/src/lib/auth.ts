import { betterAuth } from "better-auth";
import { openAPI } from "better-auth/plugins";

export const auth = betterAuth({
    baseURL: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
    database: {
        provider: "postgres", // or sqlite for dev
        url: process.env.DATABASE_URL || "postgres://user:pass@localhost:5432/db",
    },
    emailAndPassword: {
        enabled: true
    },
    plugins: [
        openAPI()
    ]
});
