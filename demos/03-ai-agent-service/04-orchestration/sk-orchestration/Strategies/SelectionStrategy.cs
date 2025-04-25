using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

namespace SKOrchestration.Strategies
{
    /// <summary>
    /// A selection strategy that determines which agent speaks next in the group chat.
    /// </summary>
    public class SelectionStrategy : IAgentSelectionStrategy
    {
        private readonly List<IAgent> agents;
        private int currentIndex = 0;

        public SelectionStrategy(List<IAgent> agents)
        {
            this.agents = agents ?? throw new ArgumentNullException(nameof(agents));
        }

        public Task<IAgent> SelectAgentAsync(IReadOnlyList<ChatMessageContent> chatHistory, IReadOnlyList<IAgent> groupParticipants, CancellationToken cancellationToken = default)
        {
            if (chatHistory.Count == 0 || groupParticipants.Count == 0)
            {
                return Task.FromResult(agents[0]); // Default to the first agent
            }

            // Get the last message
            var lastMessage = chatHistory[^1];

            // If the last message is from a user, start with the first agent (incident manager)
            if (lastMessage.Role == AuthorRole.User)
            {
                currentIndex = 0;
                return Task.FromResult(agents[0]);
            }

            // Alternate between agents
            currentIndex = (currentIndex + 1) % agents.Count;
            return Task.FromResult(agents[currentIndex]);
        }
    }
}
