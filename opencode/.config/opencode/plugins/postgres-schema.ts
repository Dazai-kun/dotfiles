import { Plugin } from "@opencode/plugin"
import path from "node:path"

type CliResult = {
  error?: {
    code?: string
    message?: string
  }
  [key: string]: unknown
}

type ToolArgs = {
  schema: string
  table: string
  includeDdl?: boolean
  includeIndexes?: boolean
  includeComments?: boolean
  includePartitioning?: boolean
}

function boolArg(value: boolean | undefined, enabled: string, disabled: string): string {
  return value === false ? disabled : enabled
}

export default Plugin.define({
  id: "postgres-schema",
  async setup(ctx) {
    const directory = ctx.location.directory

    await ctx.tool.transform((editor) => {
      editor.add({
        name: "postgres_schema",
        description:
          "Inspect an allowlisted PostgreSQL table schema using project .opencode/postgres-schema.json policy. Does not run arbitrary SQL.",
        options: { codemode: true },
        input: {
          type: "object",
          properties: {
            schema: { type: "string", description: "Allowlisted PostgreSQL schema name" },
            table: { type: "string", description: "PostgreSQL table name" },
            includeDdl: { type: "boolean", description: "Include best-effort reconstructed DDL" },
            includeIndexes: { type: "boolean", description: "Include index metadata" },
            includeComments: { type: "boolean", description: "Include table and column comments" },
            includePartitioning: { type: "boolean", description: "Include partitioning metadata" },
          },
          required: ["schema", "table"],
          additionalProperties: false,
        },
        async execute(input) {
          const args = input as ToolArgs

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
            directory,
            boolArg(args.includeIndexes, "--include-indexes", "--no-include-indexes"),
            boolArg(args.includeComments, "--include-comments", "--no-include-comments"),
            boolArg(args.includePartitioning, "--include-partitioning", "--no-include-partitioning"),
          ]
          if (args.includeDdl) command.push("--include-ddl")

          const proc = Bun.spawn(command, {
            cwd: directory,
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
          return { content: JSON.stringify(parsed, null, 2) }
        },
      })
    })
  },
})
