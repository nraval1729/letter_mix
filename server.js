var express = require('express');
var app = express();

// To server static files (html, css, js)
app.use(express.static(__dirname + '/public'));

// Templating set up
var engines = require('consolidate');
app.engine('html', engines.hogan);
app.set('views', __dirname + '/public/html');
app.set('view engine', 'html');

// To pick a random English word
var randomWord = require('random-words');

// To scrape the http://www.allscrabblewords.com/unscramble/ page
var osmosis = require('osmosis');

// Handlers
app.get("/", function(req, res) {
	console.log("Got to the home page!");
	var rw = randomWord();
	res.render("index.html", {rw: shuffleString(rw)});
});


// Helper functions
function shuffleString(s) {
	var a = s.split(""),
    n = a.length;

    for(var i = n - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
    }
    return a.join("");
}

app.listen(process.env.PORT || 5000);
console.log("Server started. Listening.");
