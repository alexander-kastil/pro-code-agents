$grp = "rg-pro-code-agents"
$loc = "swedencentral"
$acct = "procodestorageacct"
$container = "food"

az group create -n $grp -l $loc

az storage account create -l $loc -n $acct -g $grp --sku Standard_LRS
$key = az storage account keys list -n $acct -g $grp --query "[0].value" -o tsv
az storage container create -n $container --account-key $key --account-name $acct

az storage blob upload-batch -d $container -s "assets/images" --account-name $acct --account-key $key

Set-Location food-catalog-api
dotnet publish -c Release -o ./publish
az webapp deployment source config-zip --src ./publish.zip --name food-catalog-api --resource-group $grp
az webapp cors add --allowed-origins "*" --name food-catalog-api --resource-group $grp
Set-Location ..

Set-Location hr-mcp-server
dotnet publish -c Release -o ./publish
az webapp deployment source config-zip --src ./publish.zip --name hr-mcp-server-$env --resource-group $grp
az webapp cors add --allowed-origins "*" --name hr-mcp-server-$env --resource-group $grp
Set-Location ..
