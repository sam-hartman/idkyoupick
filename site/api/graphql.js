// Forwards the app's GraphQL queries to the movie data source without browser-origin headers (which the source rejects).
export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method !== 'POST') return new Response('method not allowed', { status: 405 });
  const body = await req.text();
  if (body.length > 100000) return new Response('too large', { status: 413 });
  const upstream = await fetch('https://apis.justwatch.com/graphql', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'user-agent': 'Mozilla/5.0 idkyoupick' },
    body,
  });
  const headers = { 'content-type': 'application/json' };
  const ra = upstream.headers.get('retry-after');
  if (ra) headers['retry-after'] = ra;
  return new Response(upstream.body, { status: upstream.status, headers });
}
