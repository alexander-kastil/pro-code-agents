#!/usr/bin/env bash
set -euo pipefail

###############################################
# clean-users.sh
# Deletes Entra ID users matching prefix (default aistudent-)
# and optionally cleans up the ai-students group if empty.
#
# Usage:
#  ./clean-users.sh [PREFIX] [DELETE_EMPTY_GROUP] [DOMAIN(optional for display)]
#    PREFIX              Username prefix (default: aistudent-)
#    DELETE_EMPTY_GROUP  true/false (default false) - delete group if becomes empty
#    DOMAIN              Optional for echoing UPN pattern only
#
# Example:
#  ./clean-users.sh aistudent- true
###############################################

PREFIX="${1:-aistudent-}"
DELETE_GROUP_FLAG="${2:-false}"
GROUP_NAME="ai-students"
DOMAIN="${3:-}" # only informational

echo "-> Cleaning users with prefix: $PREFIX"

# Collect candidate users (filtering client-side for portability)
echo "-> Querying users ... (this may page through large sets)" >&2
USER_UPNS=$(az ad user list --query "[].userPrincipalName" -o tsv | grep -E "^${PREFIX}[0-9]{2,}@" || true)

if [[ -z "$USER_UPNS" ]]; then
  echo "-> No users found matching pattern ${PREFIX}NN@""${DOMAIN}"". Nothing to delete."
  exit 0
fi

COUNT=$(echo "$USER_UPNS" | wc -l | tr -d ' ')
echo "-> Found $COUNT users to delete."

for UPN in $USER_UPNS; do
  echo "   - Deleting $UPN"
  az ad user delete --id "$UPN" || echo "     ! Failed to delete $UPN (continuing)" >&2
done

echo "-> Deletion loop complete. Verifying group membership status ..."
GROUP_ID=$(az ad group show --group "$GROUP_NAME" --query id -o tsv 2>/dev/null || true)
if [[ -z "$GROUP_ID" ]]; then
  echo "-> Group $GROUP_NAME not present; nothing further to do.";
  exit 0
fi

REMAINING=$(az ad group member list --group "$GROUP_NAME" --query "length(@)" -o tsv || echo 0)
echo "-> Remaining members in $GROUP_NAME: $REMAINING"

if [[ "$REMAINING" == "0" && "$DELETE_GROUP_FLAG" == "true" ]]; then
  echo "-> Deleting empty group $GROUP_NAME"
  az ad group delete --group "$GROUP_NAME" || echo "   ! Failed to delete group (you may lack privileges)" >&2
else
  echo "-> Keeping group (either not empty or DELETE_EMPTY_GROUP != true)"
fi

echo "-> Clean-up complete."
