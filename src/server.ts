import express from "express";
import { createServer } from "node:http";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { list, upsert, remove, runtime } from "./store.js";

const host = process.env.CLAUDE_HOST ?? "127.0.0.1";
const port = Number(process.env.CLAUDE_PORT ?? 4317);
const agentUrl = (process.env.CLAUDE_AGENT_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const assets = join(dirname(fileURLToPath(import.meta.url)), "..", "dashboard");

export async function startServer() {
  const app = express();
  app.disable("x-powered-by");
  app.use(express.json({ limit: "64kb" }));
  app.use((request, response, next) => {
    response.setHeader("X-Content-Type-Options", "nosniff");
    response.setHeader("Referrer-Policy", "no-referrer");
    response.setHeader(
      "Content-Security-Policy",
      "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'",
    );
    if (request.headers.host && !/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(request.headers.host)) {
      return response.status(403).send("Local access only");
    }
    next();
  });

  app.get("/api/health", (_request, response) => response.json({ ok: true }));
  app.get("/api/workspace", (_request, response) => response.json({ path: process.cwd() }));
  app.get("/api/providers", async (_request, response, next) => {
    try { response.json(await list()); } catch (error) { next(error); }
  });
  app.get("/api/runtime/provider", async (_request, response, next) => {
    try { response.json(await runtime()); } catch (error) { next(error); }
  });
  app.post("/api/providers", async (request, response, next) => {
    try { response.status(201).json(await upsert(request.body)); } catch (error) { next(error); }
  });
  app.delete("/api/providers/:id", async (request, response, next) => {
    try { await remove(request.params.id); response.status(204).end(); } catch (error) { next(error); }
  });

  app.get("/api/sessions", async (request, response) => {
    const workspace = request.query.workspace;
    if (typeof workspace !== "string" || workspace.length < 1 || workspace.length > 4096) {
      return response.status(400).json({ error: "A valid workspace path is required." });
    }
    try {
      const url = new URL(agentUrl + "/sessions");
      url.searchParams.set("workspace", workspace);
      const result = await fetch(url, { signal: AbortSignal.timeout(5000) });
      const body = await result.text();
      response.status(result.status).type("application/json").send(body);
    } catch {
      response.status(503).json({ error: "Agent runtime unavailable. Start it with: python -m claude_agent.main" });
    }
  });
  app.delete("/api/sessions/:id", async (request, response) => {
    const workspace = request.query.workspace;
    if (typeof workspace !== "string" || workspace.length < 1 || workspace.length > 4096) {
      return response.status(400).json({ error: "A valid workspace path is required." });
    }
    try {
      const url = new URL(agentUrl + "/sessions/" + encodeURIComponent(request.params.id));
      url.searchParams.set("workspace", workspace);
      const result = await fetch(url, { method: "DELETE", signal: AbortSignal.timeout(5000) });
      const body = await result.text();
      response.status(result.status);
      if (body) response.type("application/json").send(body);
      else response.end();
    } catch {
      response.status(503).json({ error: "Agent runtime unavailable. Start it with: python -m claude_agent.main" });
    }
  });

  app.post("/api/providers/:id/test", async (request, response) => {
    try {
      const provider = await runtime();
      if (!provider.configured || provider.id !== request.params.id) {
        return response.status(400).json({ ok: false, error: "Set profile as active default first" });
      }
      const base = provider.baseUrl.replace(/\/$/, "");
      const anthropic = new URL(base).hostname === "api.anthropic.com";
      const url = anthropic
        ? (base.endsWith("/v1") ? base + "/models" : base + "/v1/models")
        : base + "/models";
      const headers: Record<string, string> = anthropic
        ? { "x-api-key": provider.apiKey, "anthropic-version": "2023-06-01" }
        : provider.apiKey ? { Authorization: "Bearer " + provider.apiKey } : {};
      const result = await fetch(url, { headers, signal: AbortSignal.timeout(10000) });
      response.status(result.ok ? 200 : 502).json({
        ok: result.ok,
        status: result.status,
        message: result.ok ? "Connected" : (await result.text()).slice(0, 250),
      });
    } catch (error) {
      response.status(502).json({
        ok: false,
        error: error instanceof Error ? error.message : "Connection failed",
      });
    }
  });

  app.use(express.static(assets));
  app.use((error: unknown, _request: express.Request, response: express.Response, _next: express.NextFunction) =>
    response.status(400).json({ error: error instanceof Error ? error.message : "Unexpected error" }),
  );

  const server = createServer(app);
  await new Promise<void>((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, host, resolve);
  });
  return { server, url: "http://" + host + ":" + port };
}
