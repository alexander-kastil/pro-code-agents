using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents.Chat;
using Microsoft.SemanticKernel.Agents;

namespace SKOrchestration
{
    public class ApprovalTerminationStrategy : TerminationStrategy
    {
        protected override Task<bool> ShouldAgentTerminateAsync(Agent agent, IReadOnlyList<ChatMessageContent> history, CancellationToken cancellationToken = default)
        {
            var lastContent = history[^1].Content?.ToLowerInvariant() ?? string.Empty;
            return Task.FromResult(lastContent.Contains("no action needed"));
        }
    }
}
