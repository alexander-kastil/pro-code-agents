using System.ComponentModel;
using Microsoft.SemanticKernel;

namespace SKOrchestration;

public class LogFilePlugin
{
    [KernelFunction, Description("Accesses the given file path string and returns the file contents as a string")]
    public string ReadLogFile(string filepath = "")
    {
        return File.ReadAllText(filepath);
    }
}