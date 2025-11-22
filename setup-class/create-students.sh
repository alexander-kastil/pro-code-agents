#!/usr/bin/env bash
set -euo pipefail

###############################################
# create-students.sh
# Creates a set of Entra ID users (aistudent-01..N),
# adds them to the ai-students group, and assigns
# Azure AI roles (Azure AI User + Azure AI Account Owner)
# on the deployed Azure AI Foundry (AIServices) account.
#
# Requirements:
#  - Azure CLI logged in with sufficient Tenant & RBAC rights
#  - User creation requires Directory (User) administrator perms
#  - Role assignment requires Owner or User Access Administrator on subscription/resource
#
# Usage:
#  ./create-students.sh [COUNT] [DOMAIN] [RESOURCE_GROUP]
#    COUNT          Number of students to create (default 10)
#    DOMAIN         UPN domain (e.g. contoso.onmicrosoft.com). If omitted, first verified domain is used.
#    RESOURCE_GROUP Resource group containing the deployed AI Foundry (default: from AZURE_RG env or prompts)
#
# Example:
#  ./create-students.sh 15 contoso.onmicrosoft.com ai-training-rg
###############################################

DEFAULT_COUNT=10
PASSWORD="TiTp4student@"
GROUP_NAME="ai-students"
PREFIX="aistudent"

COUNT="${1:-$DEFAULT_COUNT}"
DOMAIN="${2:-}"
RG_INPUT="${3:-}" # optional resource group

if ! [[ "$COUNT" =~ ^[0-9]+$ ]]; then
  echo "ERROR: COUNT must be a positive integer" >&2
  exit 1
fi

echo "-> Target student count: $COUNT"

# Resolve resource group
if [[ -z "$RG_INPUT" ]]; then
  if [[ -n "${AZURE_RG:-}" ]]; then
    RG="$AZURE_RG"
  else
    echo "Enter resource group hosting AI Foundry (or press Enter to list):" >&2
    read -r RG
    if [[ -z "$RG" ]]; then
      echo "Listing resource groups (select one with --resource-group next time):" >&2
      az group list --query "[].name" -o tsv
      echo "ERROR: Resource group is required." >&2
      exit 1
    fi
  fi
else
  RG="$RG_INPUT"
fi

echo "-> Using resource group: $RG"

# Resolve domain if not provided
if [[ -z "$DOMAIN" ]]; then
  echo "-> Resolving tenant domain..."
  DOMAIN=$(az ad domain list --query "[?isVerified].name | [0]" -o tsv || true)
  if [[ -z "$DOMAIN" ]]; then
    echo "ERROR: Could not auto-detect a verified domain. Provide DOMAIN explicitly." >&2
    exit 1
  fi
fi
echo "-> Using UPN domain: $DOMAIN"

# Locate AI Foundry (AIServices) account in resource group
echo "-> Locating AI Foundry account (kind=AIServices) in $RG ..."
AI_ACCOUNT_ID=$(az resource list \
  --resource-group "$RG" \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --query "[?kind=='AIServices'].id | [0]" -o tsv || true)
if [[ -z "$AI_ACCOUNT_ID" ]]; then
  echo "ERROR: No AIServices (Azure AI Foundry) account found in resource group $RG" >&2
  exit 1
fi
AI_ACCOUNT_NAME=$(basename "$AI_ACCOUNT_ID")
echo "-> Found AI Foundry account: $AI_ACCOUNT_NAME"

# (Optional) Locate a project child resource (accounts/projects) - may be absent
AI_PROJECT_ID=$(az resource list \
  --resource-group "$RG" \
  --resource-type "Microsoft.CognitiveServices/accounts/projects" \
  --query "[?contains(id,'$AI_ACCOUNT_NAME')].id | [0]" -o tsv || true)
if [[ -n "$AI_PROJECT_ID" ]]; then
  echo "-> Found AI Project: $(basename "$AI_PROJECT_ID")"
else
  echo "-> No AI Project child resource found (continuing with hub scope only)"
fi

# Ensure group exists
echo "-> Ensuring group $GROUP_NAME exists ..."
GROUP_ID=$(az ad group show --group "$GROUP_NAME" --query id -o tsv 2>/dev/null || true)
if [[ -z "$GROUP_ID" ]]; then
  echo "-> Creating group $GROUP_NAME"
  GROUP_ID=$(az ad group create --display-name "$GROUP_NAME" --mail-nickname "$GROUP_NAME" --query id -o tsv)
else
  echo "-> Group already exists (id: $GROUP_ID)"
fi

# Resolve role names dynamically to avoid hard-coding GUIDs
echo "-> Resolving Azure AI role definitions ..."
ROLE_AI_USER_ID=$(az role definition list --name "Azure AI User" --query "[0].id" -o tsv || true)
ROLE_AI_OWNER_ID=$(az role definition list --name "Azure AI Account Owner" --query "[0].id" -o tsv || true)

if [[ -z "$ROLE_AI_USER_ID" || -z "$ROLE_AI_OWNER_ID" ]]; then
  echo "WARNING: Could not resolve one or both Azure AI role IDs. They may not yet be available in your CLI/tenant." >&2
  echo "         Skipping role assignment; you can re-run after roles propagate." >&2
  ASSIGN_ROLES=false
else
  ASSIGN_ROLES=true
  echo "-> Resolved roles: Azure AI User ($ROLE_AI_USER_ID), Azure AI Account Owner ($ROLE_AI_OWNER_ID)"
fi

echo "-> Creating users ..."
CREATED=0
for i in $(seq 1 "$COUNT"); do
  NUM=$(printf "%02d" "$i")
  USERNAME="$PREFIX-$NUM"
  UPN="$USERNAME@$DOMAIN"
  echo "   - Processing $UPN"
  # Check existence
  if az ad user show --id "$UPN" --query id -o tsv >/dev/null 2>&1; then
    echo "     > User exists, skipping create"
    USER_ID=$(az ad user show --id "$UPN" --query id -o tsv)
  else
    USER_ID=$(az ad user create \
      --display-name "$USERNAME" \
      --user-principal-name "$UPN" \
      --password "$PASSWORD" \
      --force-change-password-next-sign-in false \
      --account-enabled true \
      --query id -o tsv)
    echo "     > Created (id: $USER_ID)"
    CREATED=$((CREATED+1))
  fi
  # Add to group (idempotent)
  if ! az ad group member check --group "$GROUP_NAME" --member-id "$USER_ID" --query "value" -o tsv | grep -q true; then
    az ad group member add --group "$GROUP_NAME" --member-id "$USER_ID" >/dev/null
    echo "     > Added to group"
  else
    echo "     > Already in group"
  fi
done

echo "-> Users processed. Newly created: $CREATED"

if $ASSIGN_ROLES; then
  echo "-> Assigning roles to group at AI Foundry scope ..."
  set +e
  az role assignment create --role "Azure AI User" --assignee-object-id "$GROUP_ID" --assignee-principal-type Group --scope "$AI_ACCOUNT_ID" >/dev/null 2>&1
  if [[ $? -ne 0 ]]; then
    echo "   ! Failed to assign Azure AI User to group. Will attempt per-user assignment." >&2
    GROUP_ASSIGN_USER=false
  else
    echo "   > Assigned Azure AI User to group"
    GROUP_ASSIGN_USER=true
  fi
  az role assignment create --role "Azure AI Account Owner" --assignee-object-id "$GROUP_ID" --assignee-principal-type Group --scope "$AI_ACCOUNT_ID" >/dev/null 2>&1
  if [[ $? -ne 0 ]]; then
    echo "   ! Failed to assign Azure AI Account Owner to group. Will attempt per-user assignment." >&2
    GROUP_ASSIGN_OWNER=false
  else
    echo "   > Assigned Azure AI Account Owner to group"
    GROUP_ASSIGN_OWNER=true
  fi
  set -e

  if [[ "$GROUP_ASSIGN_USER" == false || "$GROUP_ASSIGN_OWNER" == false ]]; then
    echo "-> Falling back to per-user role assignments ..."
    for i in $(seq 1 "$COUNT"); do
      NUM=$(printf "%02d" "$i")
      USERNAME="$PREFIX-$NUM"
      UPN="$USERNAME@$DOMAIN"
      USER_ID=$(az ad user show --id "$UPN" --query id -o tsv)
      if [[ "$GROUP_ASSIGN_USER" == false ]]; then
        az role assignment create --role "Azure AI User" --assignee-object-id "$USER_ID" --assignee-principal-type User --scope "$AI_ACCOUNT_ID" >/dev/null || echo "   ! User $UPN: Azure AI User assign failed"
      fi
      if [[ "$GROUP_ASSIGN_OWNER" == false ]]; then
        az role assignment create --role "Azure AI Account Owner" --assignee-object-id "$USER_ID" --assignee-principal-type User --scope "$AI_ACCOUNT_ID" >/dev/null || echo "   ! User $UPN: Azure AI Account Owner assign failed"
      fi
    done
  fi
else
  echo "-> Skipping role assignments (roles not resolved)."
fi

echo "-> Completed. Summary:";
echo "   Group: $GROUP_NAME (id: $GROUP_ID)"
echo "   AI Foundry: $AI_ACCOUNT_NAME"
echo "   Users total requested: $COUNT | created: $CREATED"
echo "   Password (all users): $PASSWORD"
echo "-> You can verify with: az ad group show --group $GROUP_NAME --query 'members'"
