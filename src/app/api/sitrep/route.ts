import { NextResponse } from 'next/server';

const AI_SERVER_URL = 'http://127.0.0.1:8000/api/sitrep';

export async function POST(req: Request) {
    let body: unknown;
    try {
        body = await req.json();
    } catch {
        return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
    }

    try {
        const res = await fetch(AI_SERVER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            // Short timeout so the fallback triggers quickly when server is offline
            signal: AbortSignal.timeout(15_000),
        });

        const data = await res.json();
        return NextResponse.json(data, { status: res.status });
    } catch (err: unknown) {
        const isTimeout = err instanceof DOMException && err.name === 'TimeoutError';
        return NextResponse.json(
            {
                error: 'ai_server_offline',
                details: isTimeout
                    ? 'Request to AI server timed out.'
                    : 'Could not reach the local AI server. Is backend_server.py running?',
            },
            { status: 503 }
        );
    }
}
