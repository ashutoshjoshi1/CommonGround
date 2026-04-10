FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json /app/package.json
COPY apps/web/package.json /app/apps/web/package.json
COPY packages/ui/package.json /app/packages/ui/package.json
COPY packages/types/package.json /app/packages/types/package.json
COPY packages/config/package.json /app/packages/config/package.json
RUN npm install

FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules /app/node_modules
COPY . /app
RUN npm --workspace apps/web run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app /app
EXPOSE 3000
CMD ["npm", "--workspace", "apps/web", "run", "start"]
