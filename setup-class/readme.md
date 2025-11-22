# Student User Management (Training Environment)

Two helper scripts provision and clean up temporary student identities for AI Foundry demos:

```bash
# Create 10 students (default) in resource group ai-rg
./create-students.sh 10 contoso.onmicrosoft.com ai-rg

# Create 25 students using auto-detected domain
./create-students.sh 25 ai-rg

# Clean up all aistudent-* users, keep group
./clean-users.sh

# Clean up and delete empty group afterwards
./clean-users.sh aistudent- true
```

Script notes:

- Users are named `aistudent-01`, `aistudent-02`, ... with password `xxx`.
- Added to Entra ID group `ai-students` (created if missing).
- Attempts role assignment (Azure AI User + Azure AI Account Owner) at the AI Foundry account scope.
- If group assignment fails, roles are applied per user.
- Clean script deletes users matching the prefix and optionally deletes the group if empty.
