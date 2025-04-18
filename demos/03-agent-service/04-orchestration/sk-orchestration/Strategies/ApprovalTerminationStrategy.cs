using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

namespace SKOrchestration.Strategies
{
    /// <summary>
    /// A termination strategy that ends the conversation based on approval from specific agents.
    /// </summary>
    public class ApprovalTerminationStrategy : IAgentTerminationStrategy
    {
        private readonly List<IAgent> approvalAgents;
        private readonly int maximumIterations;
        private readonly bool automaticReset;
        private int currentIterations = 0;

        public ApprovalTerminationStrategy(List<IAgent> approvalAgents, int maximumIterations = 10, bool automaticReset = false)
        {
            this.approvalAgents = approvalAgents ?? throw new ArgumentNullException(nameof(approvalAgents));
            this.maximumIterations = maximumIterations > 0 ? maximumIterations : throw new ArgumentException("Maximum iterations must be greater than zero", nameof(maximumIterations));
            this.automaticReset = automaticReset;
        }

        public Task<bool> ShouldTerminateAsync(IReadOnlyList<ChatMessageContent> chatHistory, CancellationToken cancellationToken = default)
        {
            currentIterations++;

            // Check if we've reached the maximum number of iterations
            if (currentIterations >= maximumIterations)
            {
                if (automaticReset)
                {
                    currentIterations = 0;
                }
                return Task.FromResult(true);
            }

            // If there are no messages, don't terminate
            if (chatHistory.Count == 0)
            {
                return Task.FromResult(false);
            }

            // Check if the last message is from an approval agent and indicates termination
            var lastMessage = chatHistory[^1];

            // Check if the last message is from an approval agent
            var isFromApprovalAgent = approvalAgents.Any(agent => agent.Name == lastMessage.AuthorName);

            if (isFromApprovalAgent)
            {
                // Check if the message indicates "No action needed" or "Escalate issue"
                if (lastMessage.Content.Contains("No action needed") ||
                    lastMessage.Content.Contains("Escalate issue"))
                {
                    if (automaticReset)
                    {
                        currentIterations = 0;
                    }
                    return Task.FromResult(true);
                }
            }

            return Task.FromResult(false);
        }
    }
}
