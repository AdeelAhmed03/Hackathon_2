/**
 * Proxy utility for forwarding API requests to the FastAPI backend
 */

import { NextRequest, NextResponse } from 'next/server';

// Backend API URL
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

/**
 * Generic proxy handler for forwarding requests to the FastAPI backend
 */
export async function proxyRequest(
  req: NextRequest,
  path: string
): Promise<NextResponse> {
  try {
    // Get the authorization header if it exists
    const authHeader = req.headers.get('authorization');

    // Forward the request to the backend with proper API version prefix
    const backendUrl = `${BACKEND_API_URL}/api/v1${path}`;

    // Prepare headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
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
      body: req.method !== 'GET' && req.method !== 'HEAD'
        ? await req.text()
        : undefined,
    });

    // Create response with backend data
    const response = NextResponse.json(
      await backendResponse.json(),
      { status: backendResponse.status }
    );

    // Forward any Set-Cookie headers from the backend
    const setCookieHeader = backendResponse.headers.get('set-cookie');
    if (setCookieHeader) {
      response.headers.set('set-cookie', setCookieHeader);
    }

    return response;
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
