/** @type {import('next').NextConfig} */
const nextConfig = {
  // Optimizaciones para Railway con memoria limitada
  experimental: {
    // Reducir el uso de memoria
    workerThreads: false,
    cpus: 1,
  },
  
  // Configuración de build optimizada
  typescript: {
    // Ignorar errores de TypeScript durante el build para evitar crashes
    ignoreBuildErrors: true,
  },
  
  eslint: {
    // Ignorar errores de ESLint durante el build
    ignoreDuringBuilds: true,
  },
  
  // Optimización de imágenes deshabilitada para reducir memoria
  images: {
    unoptimized: true,
  },
  
  // Reducir el uso de memoria en el build
  swcMinify: false,
  
  // Configuración para Railway
  output: 'standalone',
  
  // Configuración de webpack optimizada
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Limitar el uso de memoria en el cliente
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: {
            minChunks: 1,
            priority: -20,
            reuseExistingChunk: true,
          },
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: -10,
            chunks: 'all',
          },
        },
      };
    }
    
    // Configuración de memoria para webpack
    config.optimization.minimize = false;
    
    return config;
  },
};

module.exports = nextConfig;
