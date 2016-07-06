var a = {a:1};
var fs = require('fs');
var path = require('path');
fs.writeFileSync(path.join('a', 'b'), "BOWERDEPS="+JSON.stringify(a)+";");
