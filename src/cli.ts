#!/usr/bin/env node
import {createInterface} from "node:readline/promises";import {stdin,stdout} from "node:process";import {startServer} from "./server.js";
const cmd=process.argv[2]??"chat";
if(cmd==="dashboard"){const s=await startServer();console.log("NEXUS dashboard at "+s.url+" — Ctrl+C to stop");}
else if(cmd==="doctor"){try{const r=await fetch((process.env.NEXUS_AGENT_URL??"http://127.0.0.1:8000")+"/health");console.log("Agent "+(r.ok?"online":"unhealthy"));}catch{console.log("Agent offline. Start python -m nexus_agent.main");}}
else if(cmd==="skills"){console.log("Bundled: deep-research, code-architect, fullstack-engineer, debug-master, code-review, test-engineer, security-auditor, database-architect, git-master");}
else if(cmd==="chat"){const rl=createInterface({input:stdin,output:stdout});console.log("NEXUS AI · /help /exit");try{while(true){const m=(await rl.question("\nYou › ")).trim();if(!m)continue;if(m==="/exit"||m==="/quit")break;if(m==="/help"){console.log("Configure models at http://127.0.0.1:4317");continue;}try{const r=await fetch((process.env.NEXUS_AGENT_URL??"http://127.0.0.1:8000")+"/chat",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({message:m,workspace:process.cwd()})});const d=await r.json() as{response?:string;detail?:string};console.log("\nNEXUS › "+(d.response??d.detail??"No response"));}catch{console.log("Agent unavailable. Start python -m nexus_agent.main");}}}finally{rl.close();}}
else console.log("Usage: nexus <dashboard|chat|doctor|skills>");
