using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

namespace SKOrchestration
{
    public class Selection
    {
        // Define Selection Strategy (Which Agent Speaks Next?)
        public static readonly KernelFunction selectionFunction =
            AgentGroupChat.CreatePromptFunctionForStrategy(
                @"Examine the provided RESPONSE and choose the next participant.
                State only the name of the chosen participant without explanation.
                Never choose the participant named in the RESPONSE.

                Choose only from these participants:
                - INCIDENT_MANAGER
                - DEVOPS_ASSISTANT

                Always follow these rules when choosing the next participant:
                - If RESPONSE is user input, analyze the message:
                    - If it contains words like 'incident', 'issue', 'problem', choose INCIDENT_MANAGER.
                    - If it contains words like 'deploy', 'build', 'pipeline', choose DEVOPS_ASSISTANT.
                - If RESPONSE is by INCIDENT_MANAGER, the next step MUST be the DEVOPS_ASSISTANT.
                - If RESPONSE is by DEVOPS_ASSISTANT, the next step MUST be the INCIDENT_MANAGER.
                - If the topic is unclear, default to INCIDENT_MANAGER.

                RESPONSE:
                {{$lastmessage}}",
                safeParameterNames: "lastmessage"
            );

    }
}
