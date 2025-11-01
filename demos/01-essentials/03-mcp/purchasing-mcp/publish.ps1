$env = "dev"
$grp = "cs-business-process-$env"
$loc = "westeurope"
az webapp up -n purchasing-mcp-$env -g $grp -p process-purchasing-plan-$env -l $loc -r "dotnet:9" --sku B1