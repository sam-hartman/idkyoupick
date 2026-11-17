// Server-side proxy for the few TMDB calls the app needs; the API key stays in the environment, never in the page.
export const config = { runtime: 'edge' };

const ALLOWED = [/^\/search\/keyword$/, /^\/discover\/movie$/, /^\/movie\/\d+\/keywords$/];

export default async function handler(req) {
  const u = new URL(req.url);
  const path = u.searchParams.get('path') || '';
  if (!ALLOWED.some((re) => re.test(path))) return new Response('forbidden', { status: 403 });
  const q = new URLSearchParams(u.searchParams);
  q.delete('path');
  q.set('api_key', process.env.TMDB_API_KEY);
  const upstream = await fetch('https://api.themoviedb.org/3' + path + '?' + q.toString(), {
    headers: { accept: 'application/json' },
  });
  return new Response(upstream.body, {
    status: upstream.status,
    headers: { 'content-type': 'application/json', 'cache-control': 'public, s-maxage=86400, stale-while-revalidate=604800' },
  });
}
