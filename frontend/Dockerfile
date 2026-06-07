FROM node:20-alpine AS base

WORKDIR /app

# 安装依赖
COPY package.json ./
RUN npm install

# 构建
COPY . .
RUN npm run build

# 生产运行
FROM node:20-alpine AS runner
WORKDIR /app

COPY --from=base /app/.next/standalone ./
COPY --from=base /app/.next/static ./.next/static
COPY --from=base /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
