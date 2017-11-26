{
    keywords: []
    score: 
    sentiment: 
    time: 
}

run script on mongo server
to verify data
run 
`mongo dicdatabase`
`db.twitterTweets.find().limit(1).sort({$natural:-1}).pretty()`