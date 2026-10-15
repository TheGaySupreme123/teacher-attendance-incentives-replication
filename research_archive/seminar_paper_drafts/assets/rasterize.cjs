const sharp = require("/Users/shayb/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp");
sharp(process.argv[2], {density:300}).png().toFile(process.argv[3]).catch(e=>{console.error(e);process.exit(1)});
