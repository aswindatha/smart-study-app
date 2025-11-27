# ---------- Stage 1: Build ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Install deps
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN if [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --frozen-lockfile; \
    elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    else npm i; fi

# Build-time env for Vite
ARG VITE_API_BASE_URL
ARG VITE_API_BASE_URL_PROD
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_API_BASE_URL_PROD=${VITE_API_BASE_URL_PROD}

# Copy source and build
COPY . .
RUN npm run build

# ---------- Stage 2: Run (nginx) ----------
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
