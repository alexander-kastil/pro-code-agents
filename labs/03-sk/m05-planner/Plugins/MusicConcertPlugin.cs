using System.ComponentModel;
using System.IO;
using Microsoft.SemanticKernel;

public class MusicConcertPlugin
{
    [KernelFunction, Description("Get a list of upcoming concerts")]
    public static string GetTours()
    {
        string dir = Directory.GetCurrentDirectory();
        string content = File.ReadAllText($"{dir}/data/concert-dates.txt");
        return content;
    }
}