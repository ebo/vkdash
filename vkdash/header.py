header = '<!DOCTYPE html>\n\
<html lang="en">\n\
<head>\n\
<meta charset="utf-8">\n\
<title>VKDash</title>\n\
<!--[if lt IE 9]>\n\
<script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>\n\
</script>\n\
<![endif]-->\n\
<style>\n\
body {margin: 5vw;}\n\
.test:hover{background-color: white;}\n\
details:hover{background-color: rgb(250, 250, 255);}\n\
.test {\n\
  display: grid;\n\
  border-bottom: solid lightgrey;\n\
  border-width: 1px;\n\
  padding: 0.5vh;\n\
  grid-template-columns: [status] minmax(10px, 1vw) [name] 20vw [info] 38vw;\n\
  align-items:center;\n\
}\n\
.result{\n\
padding-left: 1vw;\n\
padding-top: 4vh;\n\
padding-bottom: 4vh;\n\
align-self:stretch;\n\
}\n\
.stat {\n\
    display: grid;\n\
    grid-gap: 1px;\n\
    grid-template-columns: repeat(40, 1fr);\n\
}\n\
.overview {\n\
    display: grid;\n\
    grid-gap: 1px;\n\
    grid-template-columns: repeat(50, 1fr);\n\
}\n\
.report {\n\
    padding-top: 0.40vw;\n\
    padding-bottom: 0.40vw;\n\
    align-self: stretch;\n\
    text-align: center\n\
}\n\
.view {\n\
    padding-top: 0.25vw;\n\
    padding-bottom: 0.25vw;\n\
    align-self: stretch;\n\
}\n\
.skip{background-color: #38B9ED;}\n\
.pass{background-color: #60E589;}\n\
.fail{background-color: #FF5C5A;}\n\
.todo{background-color: #FFF171;}\n\
.diagnostic{background-color: #000000;}\n\
.name{}\n\
.info{display: grid;}\n\
details[open] SUMMARY ~ * {animation: sweep .25s;}\n\
@keyframes sweep {\n\
  0%    {opacity: 0; margin-top: -1px;}\n\
  100%  {opacity: 1;}\n\
}\n\
</style>\n\
</head>\n\
<header>\n\
<h1>Unit Tests</h1>\n\
</header>\n'

footer = '<footer>\n\
<p>&copy; 2017 Example Test Suites ... </p>\n\
</footer>\n\
</html>'


