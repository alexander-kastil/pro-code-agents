using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Azure.AI.Projects;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents.Chat;
using Microsoft.SemanticKernel.Agents;

namespace SKOrchestration
{
    public class SelectionStrategy
    {
        private const string IncidentManager = "INCIDENT_MANAGER";
        private const string DevOpsAssistant = "DEVOPS_ASSISTANT";
        private const string User = "USER";

        public async Task<Microsoft.SemanticKernel.Agents.Agent?> SelectAgentAsync(
            IReadOnlyList<Microsoft.SemanticKernel.Agents.Agent> agents,
            IReadOnlyList<ChatMessageContent> history,
            CancellationToken cancellationToken = default)
        {
            if (history == null || history.Count == 0)
            {
                return null;
            }

            var lastMessage = history[^1];

            // The Incident Manager should go after the User or the DevOps Assistant
            if (string.Equals(lastMessage.AuthorName, DevOpsAssistant, StringComparison.OrdinalIgnoreCase) ||
                string.Equals(lastMessage.AuthorName, User, StringComparison.OrdinalIgnoreCase))
            {
                return agents.FirstOrDefault(agent => string.Equals(agent.Name, IncidentManager, StringComparison.OrdinalIgnoreCase));
            }

            // Otherwise it is the DevOps Assistant's turn
            return agents.FirstOrDefault(agent => string.Equals(agent.Name, DevOpsAssistant, StringComparison.OrdinalIgnoreCase));
        }
    }
}
