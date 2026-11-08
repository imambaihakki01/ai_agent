#!/usr/bin/env node
import {createInterface} from "node:readline/promises";
import {stdin,stdout} from "node:process";
import {startServer} from "./server.js";

const AGENT_URL=process.env.CLAUDE_AGENT_URL??"http://127.0.0.1:8000";
const DASHBOARD_URL="http://"+(process.env.CLAUDE_HOST??"127.0.0.1")+":"+(process.env.CLAUDE_PORT??"4317");
const cmd=process.argv[2]??"chat";
const skills=["deep-research","code-architect","fullstack-engineer","debug-master","code-review","test-engineer","security-auditor","database-architect","git-master"];

if(cmd==="--version"||cmd==="-v") console.log("Claude CLI 0.1.0");
else if(cmd==="--help"||cmd==="-h"||cmd==="help") console.log("Claude CLI — independent Claude-style coding agent\n\nUsage: claude <chat|dashboard|doctor|skills>\n\nRun claude with no command to start chat.");
else if(cmd==="dashboard"){const s=await startServer();console.log("Claude CLI dashboard at "+s.url+" — Ctrl+C to stop");}
else if(cmd==="doctor"){try{const r=await fetch(AGENT_URL+"/health");console.log("Agent "+(r.ok?"online":"unhealthy"));}catch{console.log("Agent offline. Start python -m claude_agent.main");}}
else if(cmd==="skills"){console.log("Available skills:\n"+skills.map(x=>"  • "+x).join("\n"));}
else if(cmd==="chat"){
 const rl=createInterface({input:stdin,output:stdout});let allowWrite=false,allowShell=false,sessionId:string|undefined;
 console.log("\n  Claude CLI · local coding agent\n  /help commands · /exit quit · writes OFF · shell OFF\n");
 try{while(true){
  const m=(await rl.question("You › ")).trim();if(!m)continue;
  if(m==="/exit"||m==="/quit")break;
  if(m==="/help"){console.log("\n/allow-write  Toggle file write permission\n/allow-shell  Toggle shell permission\n/status        Check agent runtime\n/new           Start a fresh conversation\n/skills        List bundled skills\n/dashboard     Show local dashboard URL\n/exit          Quit\nPermissions start disabled for every session.");continue;}
  if(m==="/allow-write"){allowWrite=!allowWrite;console.log("File writes "+(allowWrite?"ENABLED":"DISABLED")+" for this session.");continue;}
  if(m==="/allow-shell"){allowShell=!allowShell;console.log("Shell execution "+(allowShell?"ENABLED":"DISABLED")+" for this session.");continue;}
  if(m==="/new"||m==="/clear"){sessionId=undefined;console.log("Started a fresh conversation.");continue;}
  if(m==="/skills"){console.log(skills.join(" · "));continue;}
  if(m==="/dashboard"){console.log("Dashboard: "+DASHBOARD_URL);continue;}
  if(m==="/status"){try{const r=await fetch(AGENT_URL+"/health");const d=await r.json() as {service?:string;version?:string};console.log(r.ok?"Agent online · "+(d.version??"runtime"):"Agent unhealthy");}catch{console.log("Agent offline. Start python -m claude_agent.main");}continue;}
  try{
   const r=await fetch(AGENT_URL+"/chat",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({message:m,workspace:process.cwd(),session_id:sessionId,allowWrite,allowShell})});
   const d=await r.json() as{response?:string;detail?:string;session_id?:string};if(d.session_id)sessionId=d.session_id;console.log("\nClaude › "+(d.response??d.detail??"No response")+"\n");
  }catch{console.log("Agent unavailable. Start python -m claude_agent.main");}
 }}finally{rl.close();}
}else console.log("Usage: claude <dashboard|chat|doctor|skills>");
