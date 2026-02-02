/**
 * Tasks API proxy route
 * Proxies all task-related requests to the FastAPI backend
 */

import { NextRequest } from 'next/server';
import { proxyRequest } from '@/lib/proxy';

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

export async function GET(req: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const routePath = `/tasks${path.length > 0 ? '/' + path.join('/') : ''}`;
  return proxyRequest(req, routePath);
}

export async function POST(req: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const routePath = `/tasks${path.length > 0 ? '/' + path.join('/') : ''}`;
  return proxyRequest(req, routePath);
}

export async function PUT(req: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const routePath = `/tasks${path.length > 0 ? '/' + path.join('/') : ''}`;
  return proxyRequest(req, routePath);
}

export async function DELETE(req: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const routePath = `/tasks${path.length > 0 ? '/' + path.join('/') : ''}`;
  return proxyRequest(req, routePath);
}

export async function PATCH(req: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const routePath = `/tasks${path.length > 0 ? '/' + path.join('/') : ''}`;
  return proxyRequest(req, routePath);
}
