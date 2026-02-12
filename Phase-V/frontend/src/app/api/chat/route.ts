/**
 * Chat API proxy route
 * Handles /api/chat requests and forwards to backend
 */

import { NextRequest } from 'next/server';
import { proxyRequest } from '@/lib/proxy';

export async function POST(req: NextRequest) {
  return proxyRequest(req, '/chat');
}

export async function GET(req: NextRequest) {
  return proxyRequest(req, '/chat/conversations');
}
