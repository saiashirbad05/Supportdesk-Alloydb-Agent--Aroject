$BaseUrl = if ($args.Count -gt 0) { $args[0] } else { "https://supportdesk-nl-api-260584325793.us-central1.run.app" }

Write-Host "Testing service: $BaseUrl"
Write-Host ""

Write-Host "[1/5] Root"
Invoke-RestMethod -Uri "$BaseUrl/" | ConvertTo-Json -Depth 6
Write-Host ""

Write-Host "[2/5] Health"
Invoke-RestMethod -Uri "$BaseUrl/health" | ConvertTo-Json -Depth 6
Write-Host ""

Write-Host "[3/5] Payments Open"
Invoke-RestMethod -Uri "$BaseUrl/demo/payments-open" | ConvertTo-Json -Depth 6
Write-Host ""

Write-Host "[4/5] Unresolved by Service"
Invoke-RestMethod -Uri "$BaseUrl/demo/unresolved-by-service" | ConvertTo-Json -Depth 6
Write-Host ""

Write-Host "[5/5] Critical Auth"
Invoke-RestMethod -Uri "$BaseUrl/demo/critical-auth" | ConvertTo-Json -Depth 6
