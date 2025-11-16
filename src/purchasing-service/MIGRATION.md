# Migration from Semantic Kernel to Microsoft.Extensions.AI

This document describes the migration from the deprecated Semantic Kernel to the new Microsoft.Extensions.AI library with prompty support.

## Changes Made

### 1. Package Updates
- **Removed**: `Microsoft.SemanticKernel` (version 1.66.0)
- **Added**: 
  - `Azure.AI.OpenAI` (version 2.1.0)
  - `Microsoft.Extensions.AI.OpenAI` (version 9.1.0-preview.1.25064.3)

### 2. Configuration Updates
- **Renamed**: `SemanticKernelOptions` → `AzureOpenAIOptions`
- **Configuration section**: `"SemanticKernel"` → `"AzureOpenAI"`
- Configuration properties remain the same: `Model`, `Endpoint`, and `ApiKey`

### 3. Service Registration (Program.cs)
- **Before**: Registered `Kernel` using `Kernel.CreateBuilder()` with Azure OpenAI chat completion
- **After**: Registered `IChatClient` using `AzureOpenAIClient` with the `.AsChatClient()` extension method
- The service uses `AzureKeyCredential` for authentication

### 4. Prompty File Creation
Created `Prompts/EmailGeneration.prompty` following the prompty specification:
- Separated system instructions from user template
- Defined input variables (requestId, supplierId, transportationCost, timestamp, details)
- Uses Mustache-style template syntax (`{{variableName}}`)

### 5. ResponseHandler Updates
The `BuildEmailBodyAsync` method now:
- Uses `IChatClient` instead of `Kernel`
- Loads and parses the prompty file at runtime
- Creates a list of `ChatMessage` objects with:
  - System message (from prompty file)
  - User message (template with replaced variables)
- Calls `CompleteAsync()` instead of `InvokePromptAsync()`
- Extracts the result from `result.Message.Text`

Helper methods added:
- `LoadPromptyFileAsync()`: Loads the prompty file from disk
- `ParsePromptyFile()`: Parses system and user sections using regex
- `ReplaceTemplateVariables()`: Replaces `{{variable}}` placeholders with actual values

### 6. Controller Updates
- `PurchasingController` now depends on `IChatClient` instead of `Kernel`
- All method signatures updated accordingly

## Benefits of This Migration

1. **Modern API**: Microsoft.Extensions.AI is the recommended approach going forward
2. **Prompty Support**: Separates prompt engineering from code, making it easier to maintain and version control prompts
3. **ChatMessages Pattern**: More explicit and testable message construction
4. **Better Separation of Concerns**: System instructions and templates are now in a dedicated file
5. **Compatibility**: Aligns with Microsoft's recommended patterns for AI agent development

## Running the Application

No changes to configuration values are required beyond renaming the section from `"SemanticKernel"` to `"AzureOpenAI"` in `appsettings.json` and `appsettings.Development.json`.

The application continues to work exactly as before, with the same API endpoints and behavior.
