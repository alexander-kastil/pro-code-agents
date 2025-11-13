using System.Runtime.InteropServices;

#pragma warning disable CS8618
interface IAgentPersona
{
    static string Name { get; }
    static string Instructions { get; }
    static string Description { get; }
}
