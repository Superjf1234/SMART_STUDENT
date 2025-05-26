/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // Disable strict mode to reduce errors
  transpilePackages: ["@radix-ui/themes", "@radix-ui/react-form"],
  // Disable dev indicators which might cause connection errors
  devIndicators: {
    buildActivity: false
  },
  // Improve debugging stability
  webpack: (config, { isServer }) => {
    // Fixes npm packages that depend on `fs` module
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        module: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;