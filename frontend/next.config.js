/** @type {import('next').NextConfig} */
// Server-side proxy: the browser uses relative /api/* + /health/* and the Next standalone
// server forwards them to the in-cluster backend. BACKEND_URL overrides the default at runtime.
const BACKEND_URL = process.env.BACKEND_URL || 'http://dclaw-fleet-backend:8139';

const nextConfig = {
  output: 'standalone',
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      { source: '/api/:path*', destination: `${BACKEND_URL}/api/:path*` },
      { source: '/health/:path*', destination: `${BACKEND_URL}/health/:path*` },
    ];
  },
}

module.exports = nextConfig
