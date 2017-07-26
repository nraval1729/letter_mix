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
var request = require('request');
var cheerio = require('cheerio');

// To get difference of arrays
var _ = require('underscore');

// Handlers
app.get("/", function(req, res) {
	console.log("Got to the home page!");
	var rw = randomWord();
	var validWords = getAllValidWordsFrom(rw);
	console.log("got all valid words: " +validWords);
	res.render("index.html", {rw: shuffleString(rw), vws: validWords});
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

function getAllValidWordsFrom(rw) {
	console.log("url: "+ "http://www.allscrabblewords.com/unscramble/" +rw);

	request("http://www.allscrabblewords.com/unscramble/" +rw, function (error, response, body) {
  	console.log('ERROR:', error);
  	console.log("Loading html into cheerio");

  	var $ = cheerio.load(body);

  	// All words
  	var allWordLinks = $('div.panel-body.unscrambled').find('ul > li> a')
  	var allWords = [];
  	for(var i=0; i<allWordLinks.length; i++) {
  		allWords.push($(allWordLinks[i]).text());
  	}

  	// Words formed by adding one extra letter
  	var oneExtraLetterWordLinks = $('div.panel-body.unscrambled').last().find('ul > li> a')
  	var oneExtraLetterWords = []
  	for(var i=0; i<oneExtraLetterWordLinks.length; i++) {
  		oneExtraLetterWords.push($(oneExtraLetterWordLinks[i]).text());
  	}

  	// Just the valid words i.e no extra letter words
  	var allValidWords = _.difference(allWords, oneExtraLetterWords)
	});
}

app.listen(process.env.PORT || 5000);
console.log("Server started. Listening.");
