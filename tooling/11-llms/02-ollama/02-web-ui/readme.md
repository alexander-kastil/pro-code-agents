# Using Ollama WebUI

## Setup Ollama WebUI

- Clone the Ollama WebUI repository:

    ```bash
    git clone https://github.com/ollama-webui/ollama-webui
    ```

- Run Ollama WebUI (with build):

    ```bash
    docker compose up
    docker compose up -d --build
    ```

- Check if Ollama is running:

    ```bash
    http://127.0.0.1:11434
    ```

- Open Ollama in a browser:

    ```bash
    http://localhost:3000
    ```

    >Note: You might have to register a new user and login to use Ollama.

    ![Ollama WebUI](_images/ollama-web-ui.png)

- Set `Ollama API URL` in the settings of Ollama WebUI.

    ![Ollama WebUI Settings](_images/ollama-web-settings.png)    

- Select a model from https://ollamahub.com/. In this example, we will use the `mistral` model.

    ![Ollama Hub](_images/load-model.jpg)


## Load a custom model from Ollama Hub

- Visit https://ollamahub.com/ and select a model and click on `Get`.

    ![Ollama Hub](_images/ollama-hub.jpg)

- Ensure that WebUI is running, add the OpenWebUI URL and click `Import to WebUI`.

    ![Ollama Hub](_images/import.jpg)

- Select and test the model:

    ![Ollama Hub](_images/scrape.jpg)