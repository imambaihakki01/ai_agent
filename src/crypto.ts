import {createCipheriv,createDecipheriv,randomBytes} from "node:crypto";
import {chmod,mkdir,readFile,writeFile} from "node:fs/promises";
import {homedir} from "node:os";import {join} from "node:path";
const dir=join(homedir(),".nexus"),keyFile=join(dir,"master.key");
async function getKey():Promise<Buffer>{await mkdir(dir,{recursive:true,mode:0o700});try{const k=await readFile(keyFile);if(k.length!==32)throw Error("Invalid key");return k;}catch(e){if((e as NodeJS.ErrnoException).code!=="ENOENT")throw e;const k=randomBytes(32);await writeFile(keyFile,k,{flag:"wx",mode:0o600});try{await chmod(keyFile,0o600);}catch{}return k;}}
export async function encrypt(v:string):Promise<string>{const iv=randomBytes(12),c=createCipheriv("aes-256-gcm",await getKey(),iv),d=Buffer.concat([c.update(v,"utf8"),c.final()]);return [iv,c.getAuthTag(),d].map(x=>x.toString("base64")).join(".");}
export async function decrypt(v:string):Promise<string>{const [iv,tag,data]=v.split(".");if(!iv||!tag||!data)throw Error("Malformed secret");const d=createDecipheriv("aes-256-gcm",await getKey(),Buffer.from(iv,"base64"));d.setAuthTag(Buffer.from(tag,"base64"));return Buffer.concat([d.update(Buffer.from(data,"base64")),d.final()]).toString("utf8");}
