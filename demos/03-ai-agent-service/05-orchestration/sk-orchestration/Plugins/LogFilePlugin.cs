using System;
using System.IO;
using Microsoft.SemanticKernel;

namespace SKOrchestration;

/// <summary>
/// A plugin that reads and writes log files.
/// </summary>
public class LogFilePlugin
{
    [KernelFunction(Description = "Accesses the given file path string and returns the file contents as a string")]
    public string ReadLogFile(string filepath = "")
    {
        return File.ReadAllText(filepath);
    }
}