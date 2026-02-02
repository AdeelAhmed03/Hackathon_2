module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[project]/frontend/src/lib/proxy.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Proxy utility for forwarding API requests to the FastAPI backend
 */ __turbopack_context__.s([
    "proxyRequest",
    ()=>proxyRequest
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/node_modules/next/server.js [app-route] (ecmascript)");
;
// Backend API URL
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';
async function proxyRequest(req, path) {
    try {
        // Get the authorization header if it exists
        const authHeader = req.headers.get('authorization');
        // Forward the request to the backend with proper API version prefix
        const backendUrl = `${BACKEND_API_URL}/api/v1${path}`;
        // Prepare headers
        const headers = {
            'Content-Type': 'application/json'
        };
        // Add authorization header if present
        if (authHeader) {
            headers['Authorization'] = authHeader;
        }
        // Forward cookies for session handling
        const cookieHeader = req.headers.get('cookie');
        if (cookieHeader) {
            headers['Cookie'] = cookieHeader;
        }
        // Make the request to the backend
        const backendResponse = await fetch(backendUrl, {
            method: req.method,
            headers,
            body: req.method !== 'GET' && req.method !== 'HEAD' ? await req.text() : undefined
        });
        // Create response with backend data
        const response = __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(await backendResponse.json(), {
            status: backendResponse.status
        });
        // Forward any Set-Cookie headers from the backend
        const setCookieHeader = backendResponse.headers.get('set-cookie');
        if (setCookieHeader) {
            response.headers.set('set-cookie', setCookieHeader);
        }
        return response;
    } catch (error) {
        console.error('Proxy error:', error);
        return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: 'Internal server error'
        }, {
            status: 500
        });
    }
}
}),
"[project]/frontend/src/app/api/auth/[...path]/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Authentication API proxy route
 * Proxies all authentication requests to the FastAPI backend
 */ __turbopack_context__.s([
    "DELETE",
    ()=>DELETE,
    "GET",
    ()=>GET,
    "POST",
    ()=>POST,
    "PUT",
    ()=>PUT
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$lib$2f$proxy$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/src/lib/proxy.ts [app-route] (ecmascript)");
;
async function GET(req, context) {
    const { path } = await context.params;
    const routePath = `/auth/${path.join('/')}`;
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$lib$2f$proxy$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["proxyRequest"])(req, routePath);
}
async function POST(req, context) {
    const { path } = await context.params;
    const routePath = `/auth/${path.join('/')}`;
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$lib$2f$proxy$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["proxyRequest"])(req, routePath);
}
async function PUT(req, context) {
    const { path } = await context.params;
    const routePath = `/auth/${path.join('/')}`;
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$lib$2f$proxy$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["proxyRequest"])(req, routePath);
}
async function DELETE(req, context) {
    const { path } = await context.params;
    const routePath = `/auth/${path.join('/')}`;
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$lib$2f$proxy$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["proxyRequest"])(req, routePath);
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__abc244b7._.js.map