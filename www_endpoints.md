### Matchs
- match/before
```
{
    mapName = GetMapName(),
    players = players
}
```
- match/update-settings
```
{
    players = players
}
```

- match/after_match_player
```
    mapName = GetMapName(),
    matchId = WebApi.matchId,
    duration = GameRules:GetGameTime(),
    players = {
        steamId = PlayerResource:GetSteamID(player_id),
        roundsWon = 0,
        roundsLost = 0,
        totalBets = 0,
        biggestProfit = 0,
        biggestLost = 0,
        isWinner = false
    }
```
- match/events
```
{
    matchId = tonumber(tostring(GameRules:GetMatchID())) 
}
```
- match/script-errors
```
{
    matchId = WebApi.matchId,
    errors = ErrorTracking.collectedErrors
}
```
- payment/create
```
{
    steamId = steamId,
    matchId = matchId,
    method = event.method,
    paymentKind = event.paymentKind 
}
```
