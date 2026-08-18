import { tool } from "@opencode-ai/plugin"
import path from "node:path"

type CliResult = {
  error?: {
    code?: string
    message?: string
  }
  [key: string]: unknown
}

function boolArg(value: boolean | undefined, enabled: string, disabled: string): string {
  return value === false ? disabled : enabled
}

export default tool({
  description:
    "Inspect an allowlisted PostgreSQL table schema using project .opencode/postgres-schema.json policy. Does not run arbitrary SQL.",
  args: {
    schema: tool.schema.string().describe("Allowlisted PostgreSQL schema name"),
    table: tool.schema.string().describe("PostgreSQL table name"),
    includeDdl: tool.schema.boolean().optional().describe("Include best-effort reconstructed DDL"),
    includeIndexes: tool.schema.boolean().optional().describe("Include index metadata"),
    includeComments: tool.schema.boolean().optional().describe("Include table and column comments"),
    includePartitioning: tool.schema.boolean().optional().describe("Include partitioning metadata"),
  },
  async execute(args, context) {
    const home = process.env.HOME
    if (!home) throw new Error("HOME is not set; cannot locate postgres-schema CLI package.")

    const projectPath = path.join(home, ".config", "opencode", "postgres-schema")
    const command = [
      "uv",
      "run",
      "--project",
      projectPath,
      "postgres-schema",
      "--schema",
      args.schema,
      "--table",
      args.table,
      "--start-dir",
      context.directory,
      boolArg(args.includeIndexes, "--include-indexes", "--no-include-indexes"),
      boolArg(args.includeComments, "--include-comments", "--no-include-comments"),
      boolArg(args.includePartitioning, "--include-partitioning", "--no-include-partitioning"),
    ]
    if (args.includeDdl) command.push("--include-ddl")

    const proc = Bun.spawn(command, {
      cwd: context.directory,
      env: process.env,
      stdout: "pipe",
      stderr: "pipe",
    })
    const [stdout, stderr, exitCode] = await Promise.all([
      new Response(proc.stdout).text(),
      new Response(proc.stderr).text(),
      proc.exited,
    ])

    let parsed: CliResult
    try {
      parsed = JSON.parse(stdout) as CliResult
    } catch {
      const detail = stderr.trim() ? ` stderr: ${stderr.trim()}` : ""
      throw new Error(`postgres_schema returned invalid JSON.${detail}`)
    }

    if (parsed.error) {
      const code = parsed.error.code ?? "POSTGRES_SCHEMA_ERROR"
      const message = parsed.error.message ?? "PostgreSQL schema inspection failed."
      throw new Error(`${code}: ${message}`)
    }
    if (exitCode !== 0) {
      throw new Error("postgres_schema failed without a structured error.")
    }
    return JSON.stringify(parsed, null, 2)
  },
})
