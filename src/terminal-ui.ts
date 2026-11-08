import { stdout } from "node:process";

type Tone = "accent" | "muted" | "success" | "warning" | "error";

const colors: Record<Tone, string> = {
  accent: "\u001b[38;2;159;177;255m",
  muted: "\u001b[38;2;143;157;179m",
  success: "\u001b[38;2;87;219;166m",
  warning: "\u001b[38;2;250;193;95m",
  error: "\u001b[38;2;255;119;119m",
};
const reset = "\u001b[0m";
const color = (tone: Tone, text: string) => stdout.isTTY ? `${colors[tone]}${text}${reset}` : text;

// Model output is untrusted. Remove terminal control sequences before writing it
// so a response cannot manipulate the user's terminal or forge CLI output.
function safeTerminalText(value: string): string {
  return value
    .replace(/\u001b\][^\u0007]*(?:\u0007|\u001b\\)/g, "")
    .replace(/\u001b\[[0-?]*[ -/]*[@-~]/g, "")
    .replace(/\u001b[@-Z\\-_]/g, "")
    .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/g, "");
}

export function printBanner(version: string, workspace: string): void {
  const line = "─".repeat(58);
  console.log(`\n${color("accent", "╭" + line + "╮")}`);
  console.log(`${color("accent", "│")}  ${color("accent", "✦")}  ${color("accent", `Claude CLI`)} ${color("muted", `v${version} · local coding agent`)}`);
  console.log(`${color("accent", "│")}  ${color("muted", workspace)}`);
  console.log(`${color("accent", "╰" + line + "╯")}`);
  console.log(`  ${color("muted", "Type a message to begin · /help for commands · /exit to quit")}`);
  console.log(`  ${color("warning", "Safety defaults: file writes OFF · shell OFF")}`);
  console.log();
}

export function promptLabel(allowWrite: boolean, allowShell: boolean): string {
  const permissions = `${color(allowWrite ? "success" : "muted", `write:${allowWrite ? "on" : "off"}`)} ${color(allowShell ? "success" : "muted", `shell:${allowShell ? "on" : "off"}`)}`;
  return `${color("accent", "❯")} ${permissions} ${color("accent", "› ")}`;
}

export function printNotice(message: string, tone: Tone = "muted"): void {
  console.log(`  ${color(tone, tone === "success" ? "✓" : tone === "error" ? "✗" : "•")} ${message}`);
}

export function printAssistant(message: string): void {
  const safeMessage = safeTerminalText(message).trimEnd();
  const line = "─".repeat(58);
  console.log(`\n${color("accent", "╭─ ✦ Claude ")}${color("muted", line.slice(11))}`);
  console.log(safeMessage || color("muted", "No response"));
  console.log(`${color("muted", "╰" + "─".repeat(58))}\n`);
}

export function startSpinner(label: string): () => void {
  if (!stdout.isTTY) {
    console.log(`  ${label}…`);
    return () => undefined;
  }
  const frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
  let frame = 0;
  let stopped = false;
  const render = () => {
    stdout.write(`\r  ${color("accent", frames[frame++ % frames.length])} ${color("muted", label + "…")}`);
  };
  render();
  const timer = setInterval(render, 90);
  return () => {
    if (stopped) return;
    stopped = true;
    clearInterval(timer);
    stdout.write("\r\u001b[2K");
  };
}
