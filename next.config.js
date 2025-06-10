/** @type {import('next').NextConfig} */
const nextConfig = {
  // CONFIGURACIÓN ULTRA-AGRESIVA PARA PREVENIR SIGBUS
  
  // Desactivar todo lo que pueda causar problemas de memoria
  experimental: {
    workerThreads: false,
    cpus: 1,
    esmExternals: false,
  },
  
  // Build configuration ultra-simple
  typescript: {
    ignoreBuildErrors: true,
  },
  
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // Imágenes sin optimización
  images: {
    unoptimized: true,
  },
  
  // Desactivar minificación pesada
  swcMinify: false,
  
  // Configuración para Railway
  output: 'standalone',
  
  // Webpack ultra-simple
  webpack: (config, { isServer, dev }) => {
    // En desarrollo, usar configuración mínima
    if (dev) {
      config.optimization.minimize = false;
      config.optimization.splitChunks = false;
      return config;
    }
    
    // En producción, configuración ultra-ligera
    config.optimization.minimize = false;
    config.optimization.splitChunks = {
      chunks: 'all',
      maxSize: 200000, // Chunks muy pequeños
      cacheGroups: {
        default: {
          minChunks: 1,
          priority: -20,
          reuseExistingChunk: true,
        },
      },
    };
    
    return config;
  },
  
  // Reducir uso de memoria
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },
  
  // Desactivar telemetría y características pesadas
  telemetry: false,
};

module.exports = nextConfig;
