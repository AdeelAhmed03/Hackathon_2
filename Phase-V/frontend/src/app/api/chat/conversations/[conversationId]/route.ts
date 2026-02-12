/**
 * Chat conversation API proxy route
 * Handles /api/chat/conversations/:id requests
 */

import { NextRequest } from 'next/server';
import { proxyRequest } from '@/lib/proxy';

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ conversationId: string }> }
) {
  const { conversationId } = await params;
  return proxyRequest(req, `/chat/conversations/${conversationId}`);
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ conversationId: string }> }
) {
  const { conversationId } = await params;
  return proxyRequest(req, `/chat/conversations/${conversationId}`);
}
