using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

public partial class Agents
{
    public static ChatCompletionAgent CreatePrincipalAgent(Kernel kernelBuilder)
    {

        string principalAgentInstructions =
            """
                You are PrincipalAgent. you should receive complete user information and 
                Your final task is to approve the results evaluated by the English and Math teachers.
                You should only approve the results and not provide any other information.
                """;


        ChatCompletionAgent principalAgent =
            new()
            {
                Instructions = principalAgentInstructions,
                Name = "Principal",
                Kernel = kernelBuilder,
            };

        return principalAgent;
    }

    public static ChatCompletionAgent CreateEnglishAgent(Kernel kernelBuilder)
    {

        string englishTeacherInstructions =
            """
            You are an English teacher with fifteen years of experience, known for your patience and clarity.
            Your goal is to refine and ensure the provided text is grammatically correct and well-structured. 
            Provide one clear and concise suggestion per response. Focus solely on improving the writing quality. 
            Avoid unnecessary comments or corrections. Do not handle any other subject requests.
            """;


        ChatCompletionAgent englishAgent =
                new()
                {
                    Instructions = englishTeacherInstructions,
                    Name = "EnglishTeacher",
                    Kernel = kernelBuilder,
                };

        return englishAgent;
    }

    public static ChatCompletionAgent CreateMathsAgent(Kernel kernelBuilder)
    {
        string mathTeacherInstructions =
            """
            You are a math teacher passionate about making complex concepts understandable.
            Your goal is to determine if the given mathematical explanation or solution is clear and correct.
            Do not handle any other subject requests
            """;
        ChatCompletionAgent mathsAgent =
                new()
                {
                    Instructions = mathTeacherInstructions,
                    Name = "MathsTeacher",
                    Kernel = kernelBuilder,
                };
        return mathsAgent;
    }

    public static AgentGroupChat GetGroupChat(ChatCompletionAgent[] agents, int maxIterations = 5)
    {
        AgentGroupChat chat =
            new(agents)
            {
                ExecutionSettings =
                    new()
                    {
                        TerminationStrategy =
                            new ApprovalTerminationStrategy()
                            {
                                Agents = [agents[0]],
                                MaximumIterations = maxIterations,
                            }
                    }
            };
        return chat;
    }
}