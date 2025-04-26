using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;

namespace SKOrchestration
{
    public class LogService
    {
        public static async Task CopyLogFilesAsync(string sourceDirectory, string destinationDirectory)
        {
            Directory.CreateDirectory(destinationDirectory);

            // Copy all files from source to destination
            foreach (string file in Directory.GetFiles(sourceDirectory))
            {
                string fileName = Path.GetFileName(file);
                string destFile = Path.Combine(destinationDirectory, fileName);
                File.Copy(file, destFile, true);
            }

            await Task.CompletedTask;
        }
    }
}
